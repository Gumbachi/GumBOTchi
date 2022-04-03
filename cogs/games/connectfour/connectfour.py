import discord
from common.cfg import devguilds
from discord.commands import slash_command, Option
from .game import Game


class ConnectFour(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="connect4")
    async def begin_connect4(
        self,
        ctx: discord.ApplicationContext,
        opponent: Option(discord.Member, description="Select Player 2")
    ):
        """Begin a game of Connect Four with a friend."""
        game = Game(ctx.author, opponent)
        await ctx.respond(embed=game.embed, view=game.view)


def setup(bot):
    """Entry point for loading cogs. Required for all cogs"""
    bot.add_cog(ConnectFour(bot))
