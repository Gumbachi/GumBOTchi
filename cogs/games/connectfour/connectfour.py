import discord
from discord.commands import slash_command, user_command, Option
from .game import Game


class ConnectFour(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot):
        self.bot = bot

    @user_command(name="Connect 4")
    async def user_connectfour(self, ctx: discord.ApplicationContext, opponent: discord.Member):
        """Context menu Rock Paper Scissors"""
        c4 = self.bot.get_application_command("connect4")
        await ctx.invoke(c4, opponent)

    @slash_command(name="connect4")
    async def connectfour(
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
