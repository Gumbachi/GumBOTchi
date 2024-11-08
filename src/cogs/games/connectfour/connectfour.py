import discord
from discord.commands import user_command

from .game import Game


class ConnectFour(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot):
        self.bot = bot

    @user_command(name="Connect 4")
    async def user_connectfour(
        self, ctx: discord.ApplicationContext, opponent: discord.Member
    ):
        """Context menu Connect Four"""

        if opponent == ctx.author:
            return await ctx.respond(
                "I get lonely too, that doesnt mean you have to play by yourself. Play against me",
                ephemeral=True,
            )

        game = Game(ctx.author, opponent)
        await ctx.respond(embed=game.embed, view=game)


def setup(bot: discord.Bot):
    """Entry point for loading cogs. Required for all cogs"""
    bot.add_cog(ConnectFour(bot))
