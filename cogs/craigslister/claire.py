import discord
from discord.ext import tasks
from discord import ApplicationContext, slash_command, Option
from cogs.craigslister.claire_model import ClaireQuery, Claire
from common.database import db
from datetime import datetime

class ClaireCog(discord.Cog):
    """Handles all of the logic for Craigslist monitoring"""

    def __init__(self, bot):
        self.bot = bot
        self.claire = Claire()
        self.claire.update()
        self.lookup_queries.start()

    @slash_command(name="steponmeclaire")
    async def clairme(
        self, ctx: ApplicationContext,
        zip: Option(int,
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
        spam_tolerance: Option(int,
            "How many spam words are allowed? Default is 5. Lower values mean more posts that might be spam",
            default=5
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

        new_query = ClaireQuery(
            owner_id= ctx.user.id, 
            zip_code=zip, 
            state=state, 
            channel=ctx.channel.id, 
            site = site, 
            keywords=keywords, 
            spam_tolerance=spam_tolerance, 
            budget=budget, 
            distance=distance, 
            category=category, 
            has_image=has_image, 
            ping=ping)
        
        await ctx.defer()
        
        try:
            new_query.search() # Dummy search to see if it works
        except Exception as e:
            error = f"Invalid query please double check your parameters (Error: {e})"
            return await ctx.respond(error)

        result = db.insert_query(new_query)

        if result:
            self.claire.active_queries.append(new_query)
            self.claire.update()
            return await ctx.respond("Added.")
        else:
            return await ctx.respond("Failed to add to DB. Try again later.")

    @slash_command(name="myballsarepurple")
    async def unclaireme(self, ctx,
        index: Option(int, "Index of query you want to delete")
        ):
        """Deletes a Claire query"""

        queries = self.claire.get_user_queries(ctx.author.id)
        to_delete = queries[index-1]
        result = db.delete_query(to_delete)
        if result:
            self.claire.active_queries.remove(to_delete)
            self.claire.update()
            return await ctx.respond("Query removed.")
        else:
            return await ctx.respond("Didn't work.")

    @slash_command(name="clairequeries")
    async def show_queries(self, ctx):
        """Display currently monitored queries"""

        queries = self.claire.get_user_queries(ctx.author.id)
        query_embed = discord.Embed(
            title=f"Claire queries {ctx.author.name}",
            color=discord.Color.blue()
        )
        query_embed.set_footer(
            text="If this looks empty it's because you don't have any queries")

        # Populate the embed with data
        for i, query in enumerate(queries, 1):
            query_embed.add_field(
                name=f"{i}. {query.keywords}",
                value=f"Budget: ${query.budget}\n Ping: {query.ping}",
                inline=False
            )

        return await ctx.respond(embed=query_embed)

    @tasks.loop(seconds=300)
    async def lookup_queries(self):
        print("Checking Craigslist", datetime.now())
        await self.claire.check_queries(self.bot)
        

    @lookup_queries.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()


def setup(bot):
    """Entry point for loading cogs."""
    bot.add_cog(ClaireCog(bot))
