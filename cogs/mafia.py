"""Module with mafia related cog and commands."""

import discord
from discord.ext import commands


class MafiaCommands(commands.Cog):
    """All mafia related commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mafia')
    async def begin_mafia_game(self, ctx):
        """Start mafia game"""
        await ctx.send("Please @ the players")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Listen for reactions."""
        pass


def setup(bot):
    bot.add_cog(MafiaCommands(bot))
