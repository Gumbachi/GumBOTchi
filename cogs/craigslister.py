from pathlib import Path

import discord
from discord import ApplicationContext, slash_command, Option


class Craigslister(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="craigslistmedaddy")
    async def craigslistme(
        self, ctx: ApplicationContext,
        keywords: Option(str, "Keywords to search for"),
        budget: Option(float, "Maximum price you will pay"),
        distance: Option(int, "Maximum distance in miles")
    ):
        """Treat yo self to a craigslist query"""
        file = discord.File(Path("./res/img/craigslist.png"))
        await ctx.respond(file=file)


def setup(bot):
    """Entry point for loading cogs."""
    bot.add_cog(Craigslister(bot))
