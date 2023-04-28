from datetime import timedelta, datetime

import discord
from common.cfg import Emoji
from discord import ApplicationContext, Option, slash_command
from discord.ext import tasks

from cogs.claire.api.modules.craigslist import Craigslist
from cogs.claire.api.sources import Sources
from cogs.claire.claire_model import ClaireQuery
from cogs.claire.claire_listing import ClaireListing
from cogs.claire.ml.claire_ml import insert_query as ml_insert_query
import httpx

# BASE_URL = "http://127.0.0.1:8000"
BASE_URL = "http://claire-server:80"

class ClaireCog(discord.Cog):
    """Handles all of the logic for deals monitoring"""

    def __init__(self, bot):
        self.bot = bot
        self.currently_checking = False
        self.last_checked = None
        self.lookup_queries.start()

    @slash_command(name="steponme")
    async def clairme(
        self, ctx: ApplicationContext,
        zip_code: Option(int,
            "Zip code to search (eg. 20815)"
        ),
        state: Option(str,
            "State to search (eg. MD)"
        ),
        site: Option(str,
            "Get from your local site. Eg: https://<washingtondc>.craigslist.org would be washingtondc"
        ),
        budget: Option(int,
            "Maximum price you will pay"
        ),
        keywords: Option(str,
            "Keywords to search for, separate each keyword with a comma. Eg. Desk, Office Desk, Wood Desk"
        ),
        distance: Option(int,
            "Maximum distance in miles",
            default=20
        ),
        has_image: Option(bool,
            "Only show listings with image",
            default=True
        ),
        spam_probability: Option(int,
            "Probability of something being spam before it is filtered out. Default is 80%",
            default=80
        ),
        ping: Option(bool,
            "If you want to be pinged or not (defaults to yes)",
            default=True
        ),
        category: Option(str,
            "CL Code to search \
            (Advanced: don't touch unless you know what you're doing)",
            default="sss"
        ),
    ):
        """Creates a query to monitor in Craigslist"""
        
        await ctx.defer()

        args = f"uid={ctx.user.id}&channel_id={ctx.channel.id}&zip_code={zip_code}&state={state}&site={site}&budget={budget}&keywords={keywords}&distance={distance}&has_image={has_image}&spam_probability={spam_probability}&ping={ping}&category={category}"

        url = f"{BASE_URL}/add_query/?{args}"
        response = await make_request(url)

        return await ctx.respond(f"{response.get('message')} {response.get('error', '')}")

    @slash_command(name="safeword")
    async def unclaireme(self, ctx,
        index: Option(int, "Index of query you want to delete")
        ):
        """Deletes a Claire query"""

        await ctx.defer()
        
        url = f"{BASE_URL}/delete_query/?uid={ctx.user.id}&index={index}"
        response = await make_request(url)

        return await ctx.respond(response.get('message'))

    @slash_command(name="claire_queries")
    async def show_queries(self, ctx):
        """Display currently monitored queries"""

        await ctx.defer()

        url = f"{BASE_URL}/claire_queries/?uid={ctx.user.id}"
        response = await make_request(url)

        queries = [ClaireQuery(**query) for query in response.get('queries')]

        query_embed = discord.Embed(
            title="Currently monitoring:",
            color=discord.Color.blue()
        )

        query_embed.set_footer(
            text="If this recently added a query it might still be processing.")
        
        query_embed.set_author(name=ctx.author.name)

        # Populate the embed with data
        for i, query in enumerate(queries, 1):
            query_embed.add_field(
                name=f"{i}. {query.keywords.title()}",
                value=f"Budget: ${query.budget}\n Ping: {query.ping}",
                inline=False
            )

        return await ctx.respond(embed=query_embed)

    @slash_command(name="claire_status")
    async def status(self, ctx):
        """Display information on last update"""
        ETA = -1
        next_check = "Now"
        if self.last_checked:
            next_check = self.last_checked + timedelta(seconds=300)
            ETA = round(abs((next_check - datetime.now()).total_seconds()))

        status_embed = discord.Embed(
            title="Status Report:",
            color=discord.Color.blue()
        )
        
        status_embed.set_author(name='Claire')

        status_embed.add_field(
            name="Last:",
            value=f"{self.last_checked}"
        )

        status_embed.add_field(
            name="Next:",
            value=f"{next_check}"
        )

        if ETA < 0:
            if self.currently_checking:
                status_embed.add_field(
                    name="ETA:",
                    value="Currently searching"
                )
            else:
                status_embed.add_field(
                    name="ETA:",
                    value="I'm busted"
                )
        else:
            status_embed.add_field(
                name="ETA:",
                value=f"{ETA} second{'s' if ETA > 1 else ''}"
            )

        return await ctx.respond(embed=status_embed)
    
    @discord.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.id == 224506294801793025:
            if reaction.emoji in [Emoji.CHECK, Emoji.CROSS]:
                if reaction.message.embeds:
                    embed = reaction.message.embeds[0]
                    if embed.author.name.lower() in [source.name.lower() for source in Sources]:
                        dic = {
                            'name': embed.title.split(" - ")[1],
                            'label': 1 if reaction.emoji == Emoji.CROSS else 0
                        }
                        for field in embed.fields:
                            if field.name == 'Details':
                                dic['details'] = field.value
                        if dic.get('details'):
                            ml_insert_query(dic)

    @slash_command(name="add_spam")
    @discord.default_permissions(administrator=True)
    async def add_spam(
            self, ctx,
            url: Option(str,
                "URL of craigslist post"
            ),
        ):
        """Gets URL details and adds them to spam list"""

        await ctx.defer()

        try:
            listing = Craigslist.get(url)

            if listing.body:

                dic = {
                    'name': "Added by URL",
                    'label': 1
                }

                dic['details'] = listing.body

                ml_insert_query(dic)
                return await ctx.respond("Success")
            
            return await ctx.respond("Nothing to add")
            
        except Exception as e:
            return await ctx.respond("Error", e)
    

    @tasks.loop(seconds=300, reconnect=True)
    async def lookup_queries(self):
        if self.currently_checking:
            return
        
        self.currently_checking = True
        url = f"{BASE_URL}/search/"

        response = await make_request(url)

        for query in response.get('results'):
            current_query = ClaireQuery(**query['query'])
            channel = self.bot.get_channel(current_query.channel)
            if channel is None:
                continue

            await current_query.send_listings(
                self.bot,
                listings=[ClaireListing(**listing) for listing in query.get('listings')]
            )

        self.currently_checking = False
        self.last_checked = datetime.now()

    @lookup_queries.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

async def make_request(url):
    async with httpx.AsyncClient(timeout=300) as client:
        response = await client.get(url)
        return response.json()

def setup(bot):
    """Entry point for loading cogs."""
    bot.add_cog(ClaireCog(bot))
