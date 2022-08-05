"""Roast functionality."""
import random

import discord
from discord import option, slash_command


class Roasts(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("./res/roasts.txt") as f:
            self.roasts = f.readlines()

    @slash_command()
    @option("victim", description="Delete this man")
    async def roast(self, ctx: discord.ApplicationContext, victim: discord.Member):
        """Roasts the living shit out of somebody. These roasts are absolutely devastating. Use with caution."""
        roast_embed = discord.Embed(
            title=f"Hey {victim.name or victim.nick}, {random.choice(self.roasts)}",
            color=discord.Color.orange()
        )
        await ctx.respond(embed=roast_embed)


def setup(bot: discord.Bot):
    bot.add_cog(Roasts(bot))
