import discord
from discord.commands import user_command

from .game import Game


class TicTacToe(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @user_command(name="Tic-Tac-Toe")
    async def user_tictactoe(
        self, ctx: discord.ApplicationContext, opponent: discord.Member
    ):
        """Context menu Tic-Tac-Toe."""

        if opponent == ctx.author:
            return await ctx.respond(
                "I get lonely too, that doesnt mean you have to play by yourself. Play against me",
                ephemeral=True,
            )

        game = Game(ctx.author, opponent)
        await ctx.respond(embed=game.embed, view=game)


def setup(bot: discord.Bot):
    bot.add_cog(TicTacToe(bot))
