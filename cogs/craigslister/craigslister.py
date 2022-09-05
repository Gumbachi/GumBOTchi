from datetime import datetime

import discord
from common.database import db
from discord import option, slash_command
from discord.ext.tasks import loop

from .craigs import CLQuery, Craigs


class Craigslister(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.craig = Craigs()
        self.craig.update()
        self.lookup_queries.start()

    @slash_command(name="craigslistmedaddy")
    @option(name="zipcode", description="Zip code to search (eg. 20815)")
    @option(name="state", description="State to search (eg. MD)")
    @option(name="site", description="Get from your local site. Eg: https://<washingtondc>.craigslist.org/ would be washingtondc")
    @option(name="budget", description="Maximum price you will pay")
    @option(name="keywords", description="Keywords to search for, separate each keyword with a comma. Eg. Desk, Office Desk, Wood Desk")
    @option(name="distance", description="Maximum distance in miles", default=20)
    @option(name="has_image", description="Only show listings with image", default=True)
    @option(name="spam_tolerance", description="How many spam words are allowed before the listing is filtered? (Default is 1)", default=1)
    @option(name="ping", description="If you want to be pinged or not (defaults to true)", default=True)
    @option(name="category", description="CL Code to search (Advanced: don't touch unless you know what you're doing)", default="sss")
    async def craigslistme(
        self, ctx: discord.ApplicationContext,
        zip: int,
        state: str,
        site: str,
        budget: int,
        keywords: str,
        distance: int,
        has_image: bool,
        spam_tolerance: int,
        ping: bool,
        category: str,
    ):
        split_words = [kw.strip() for kw in keywords.split(",")]

        """Treat yo self to a craigslist query"""
        new_query = CLQuery(
            owner_id=ctx.author.id,
            zipcode=zip,
            state=state,
            channel=ctx.channel.id,
            site=site,
            keywords=split_words,
            spam_tolerance=spam_tolerance,
            budget=budget,
            distance=distance,
            category=category,
            has_image=has_image,
            ping=ping
        )

        try:
            new_query.search()
        except Exception as e:
            print(e)
            print("SHITS BUSTED")
            return await ctx.respond("You created an invalid query please double check your parameters")

        print("FULL SEND")

        result = db.insert_query(new_query)

        if result:
            self.craig.active_queries.append(new_query)
            self.craig.update()
            return await ctx.respond("Added.")
        else:
            return await ctx.respond("Failed to add to DB.")

    @slash_command(name="uncraigslistmedaddy")
    @option(name="index", description="Index of query you want to delete")
    async def uncraigslist_me_daddy(self, ctx: discord.ApplicationContext, index: int):
        """Treat yo self to deleting a query"""
        queries = self.craig.get_user_queries(ctx.author.id)
        to_delete = queries[index-1]
        result = db.delete_query(to_delete)
        if result:
            self.craig.active_queries.remove(to_delete)
            self.craig.update()
            return await ctx.respond("Query removed.")
        return await ctx.respond("Didn't work.")

    @slash_command(name="clqueries")
    async def show_queries(self, ctx: discord.ApplicationContext):
        """Treat yo self to seeing your queries"""
        queries = self.craig.get_user_queries(ctx.author.id)
        query_embed = discord.Embed(
            title=f"Craigslistings for {ctx.author.display_name}",
            color=discord.Color.blue()
        )
        query_embed.set_footer(
            text="If this looks empty its because you aint craigslisting")

        # populate the embed with data
        for i, query in enumerate(queries, 1):
            query_embed.add_field(
                name=f"{i}. {query.keywords}",
                value=f"Budget: ${query.budget}\nPing: {query.ping}",
                inline=False
            )

        await ctx.respond(embed=query_embed)

    @loop(seconds=300)
    async def lookup_queries(self):
        print("Checking CL", datetime.now())
        await self.craig.check_queries(self.bot)

    @lookup_queries.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()


def setup(bot: discord.Bot):
    """Entry point for loading cogs."""
    bot.add_cog(Craigslister(bot))
