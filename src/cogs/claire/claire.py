import discord
from discord.ext import tasks
from discord import ApplicationContext, slash_command, Option
from cogs.claire.claire_model import ClaireQuery, Claire
from database.claire import insert_query, delete_query
from datetime import datetime
from cogs.claire.api.maps import get_lat_lon
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
        lat, lon = get_lat_lon(zip_code)
        new_query = ClaireQuery(
            owner_id= ctx.user.id, 
            zip_code=zip_code, 
            state=state, 
            channel=ctx.channel.id, 
            site = site,
            lat=lat,
            lon=lon,
            keywords=keywords, 
            spam_probability=spam_probability,
            budget=budget, 
            distance=distance, 
            category=category, 
            has_image=has_image, 
            ping=ping
        )
        
        await ctx.defer()
        
        try:
            new_query.search() # Dummy search to see if it works
        except Exception as e:
            error = f"Invalid query please double check your parameters (Error: {e})"
            return await ctx.respond(error)

        result = insert_query(new_query)

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
        result = delete_query(to_delete)
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
        print("Claire is searching", datetime.now())
        await self.claire.check_queries(self.bot)
        

    @lookup_queries.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()


def setup(bot):
    """Entry point for loading cogs."""
    bot.add_cog(ClaireCog(bot))
