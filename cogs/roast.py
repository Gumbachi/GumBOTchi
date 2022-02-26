"""Roast functionality."""
import discord
import random
from discord.commands import slash_command


class Roasts(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("./res/roasts.txt") as f:
            self.roasts = f.readlines()

    @slash_command()
    async def roast(self, ctx, victim: discord.Member):
        """Roasts the living shit out of somebody. These roasts are absolutely devastating. Use with caution."""
        roast_embed = discord.Embed(
            title=f"Hey {victim.name}, {random.choice(self.roasts)}",
            color=discord.Color.orange()
        )
        await ctx.respond(embed=roast_embed)


def setup(bot):
    bot.add_cog(Roasts(bot))
