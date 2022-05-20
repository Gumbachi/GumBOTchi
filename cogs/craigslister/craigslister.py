from pathlib import Path

import discord
from discord.ext import tasks
from discord import ApplicationContext, slash_command, Option
from cogs.craigslister.Craigs import Craigs, CLQuery
from common.database import db
from datetime import datetime

class Craigslister(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot):
        self.bot = bot
        self.craig = Craigs()
        self.lookup_queries.start()
        self.craig.update()

    @slash_command(name="craigslistmedaddy")
    async def craigslistme(
        self, ctx: ApplicationContext,
        zip: Option(int, "Zip code to search"),
        state: Option(str, "State to search"),
        site: Option(str, "Location to search"),
        budget: Option(float, "Maximum price you will pay"),
        distance: Option(int, "Maximum distance in miles"),
        keywords: Option(str, "Keywords to search for"),
        has_image: Option(bool, "Only show listings with image"),
        spam_tolerance: Option(int, "The higher the number the more relaxed the spam check is"),
        ping: Option(bool, "If you want to be pinged or not (defaults to yes)"),
        category: Option(str, "CL Code to search"),
    ):
        """Treat yo self to a craigslist query"""
        new_query = CLQuery(
                            uid= ctx.user.id, zip_code=zip, state=state, channel=ctx.channel.id, site = site, keywords=keywords, spam_tolerance=spam_tolerance, budget=budget, distance=distance, category=category, has_image=has_image, ping=ping)
        result = db.insert_query(new_query)

        if result:
            self.craig.active_queries.append(new_query)
            self.craig.update()
            return await ctx.respond("Added.")
        else:
            return await ctx.respond("Failed to add to DB.")

    @slash_command(name="uncraigslistmedaddy")
    async def uncraigslist_me_daddy(self, ctx,
            index: Option(int, "Index of query you want to delete")
        ):
        queries = self.craig.get_user_queries(ctx.author.id)
        to_delete = queries[index-1]
        result = db.delete_query(to_delete)
        if result:
            self.craig.active_queries.remove(to_delete)
            self.craig.update()
            return await ctx.respond("Query removed.")
        else:
            return await ctx.respond("Didn't work.")

    @slash_command(name="clqueries")
    async def show_queries(self, ctx):
        queries = self.craig.get_user_queries(ctx.author.id)
        query_embed = discord.Embed(
            title=f"Craigslistings for {ctx.author.name}",
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

        return await ctx.respond(embed=query_embed)

    @tasks.loop(seconds=300)
    async def lookup_queries(self):
        print("Checking CL", datetime.now())
        for query in self.craig.active_queries:
            await self.craig.process_query(bot=self.bot, query=query)

    @lookup_queries.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()        

def setup(bot):
    """Entry point for loading cogs."""
    bot.add_cog(Craigslister(bot))
