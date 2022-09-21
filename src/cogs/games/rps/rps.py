import discord
from discord.commands import user_command

from .game import Game


class RPS(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @user_command(name="Rock Paper Scissors")
    async def rock_paper_scissors(self, ctx: discord.ApplicationContext, opponent: discord.Member):
        """Rock Paper Scissors"""
        game = Game(ctx.author, opponent)
        await ctx.respond(embed=game.embed, view=game)


def setup(bot: discord.Bot):
    bot.add_cog(RPS(bot))
