import discord
from discord.commands import slash_command, user_command, Option

from .game import Game


class RPS(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @user_command(name="Rock Paper Scissors")
    async def userrps(self, ctx: discord.ApplicationContext, opponent: discord.Member):
        """Context menu Rock Paper Scissors"""
        rps = self.bot.get_application_command("rps")
        await ctx.invoke(rps, opponent)

    @slash_command(name="rps")
    async def rps(
        self,
        ctx: discord.ApplicationContext,
        opponent: Option(discord.Member, "Select Player 2")
    ):
        """Rock Paper Scissors"""
        game = Game(ctx.author, opponent)
        await ctx.respond(embed=game.embed, view=game.view)


def setup(bot):
    bot.add_cog(RPS(bot))
