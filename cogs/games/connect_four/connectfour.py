import discord
from common.cfg import devguilds
from discord.commands import slash_command, Option
from .game import Game


class ConnectFour(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot):
        self.bot = bot
        self.instances = {}

    @slash_command(name="connect4", guild_ids=devguilds)
    async def begin_connect4(
        self,
        ctx: discord.ApplicationContext,
        opponent: Option(discord.Member, description="Player 2")
    ):
        """Begin a game of Connect Four with a friend."""

        game = Game(ctx.author, opponent)
        self.instances[(ctx.author.id, opponent.id)] = game

        await ctx.respond(embed=game.embed, view=game.view)


def setup(bot):
    """Entry point for loading cogs. Required for all cogs"""
    bot.add_cog(ConnectFour(bot))
