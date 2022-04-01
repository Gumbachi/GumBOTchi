import discord
from discord.commands import slash_command

from common.cfg import devguilds
from .game import Game


class RPS(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.instances = {}

    @slash_command(name="rps")
    async def startgame(self, ctx, opponent: discord.Member):
        """Rock Paper Scissors"""
        game = Game(ctx.author, opponent)
        self.instances[(ctx.author.id, opponent)] = game
        await ctx.respond(embed=game.embed, view=game.view)


def setup(bot):
    bot.add_cog(RPS(bot))
