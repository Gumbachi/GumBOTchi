import discord
from common.cfg import devguilds
from discord.commands import slash_command
from .game import Game
from discord.commands import Option


class TicTacToe(discord.Cog):
    instances = {}

    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="tictactoe")
    async def startGame(
        self, ctx: discord.ApplicationContext,
        opponent: Option(discord.Member, "Select Player 2")
    ):
        """Play a game of tic-tac-toe"""
        game = Game(ctx.author, opponent)
        self.instances[(ctx.author.id, opponent.id)] = game
        await ctx.respond(embed=game.embed, view=game.view)


def setup(bot):
    bot.add_cog(TicTacToe(bot))
