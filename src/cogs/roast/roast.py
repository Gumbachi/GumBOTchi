"""Roast functionality."""
import random

import discord
from discord import user_command


class Roast(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("./src/cogs/roast/roasts.txt") as f:
            self.roasts = f.readlines()

    @user_command(name="Roast")
    async def roast(self, ctx: discord.ApplicationContext, member: discord.Member):
        """Roasts the living shit out of somebody. These roasts are absolutely devastating. Use with caution."""
        await ctx.respond(
            embed=discord.Embed(
                title=f"Hey {member.display_name}, {random.choice(self.roasts)}",
                color=discord.Color.orange()
            )
        )


def setup(bot: discord.Bot):
    bot.add_cog(Roast(bot))
