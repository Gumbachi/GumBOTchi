import discord
from common.cfg import devguilds
from discord.commands import slash_command
from .game import Game


class TicTacToe(discord.Cog):
    instances = {}

    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="tictactoe")
    async def startGame(self, ctx, opponent: discord.Member):
        game = Game(ctx.author, opponent)
        self.instances[(ctx.author.id, opponent.id)] = game
        await ctx.respond(f"{ctx.author} vs {opponent}", view=game.view)


def setup(bot):
    bot.add_cog(TicTacToe(bot))
