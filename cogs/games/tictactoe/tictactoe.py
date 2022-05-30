import discord
from discord.commands import slash_command, user_command, Option
from .game import Game


class TicTacToe(discord.Cog):

    def __init__(self, bot):
        self.bot = bot

    @user_command(name="Tic-Tac-Toe")
    async def user_tictactoe(self, ctx: discord.ApplicationContext, opponent: discord.Member):
        """Context menu Rock Paper Scissors"""
        game = Game(ctx.author, opponent)
        await ctx.respond(embed=game.embed, view=game.view)


def setup(bot: discord.Bot):
    bot.add_cog(TicTacToe(bot))
