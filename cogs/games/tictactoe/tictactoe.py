import discord
from common.cfg import devguilds
from discord.commands import slash_command
from .game import Game
import database


class TicTacToe(discord.Cog):
    instances = {}

    O = -1
    X = 1
    draw = 2

    def __init__(self, bot):
        self.bot = bot
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

    @slash_command(name="tictactoe", guild_ids=devguilds)
    async def startGame(self, ctx, opponent: discord.Member):
        game = Game(ctx.author, opponent)
        self.instances[ctx.guild.id] = game
        await ctx.respond(f"{ctx.author} vs {opponent}", view=game.view)

def setup(bot):
    bot.add_cog(TicTacToe(bot))
