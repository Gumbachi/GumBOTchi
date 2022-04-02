import discord
from discord.commands import slash_command, Option

from common.cfg import devguilds
from .game import Game


class RPS(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="rps")
    async def startgame(
        self,
        ctx: discord.ApplicationContext,
        opponent: Option(discord.Member, "Select Player 2")
    ):
        """Rock Paper Scissors"""
        game = Game(ctx.author, opponent)
        await ctx.respond(embed=game.embed, view=game.view)


def setup(bot):
    bot.add_cog(RPS(bot))
