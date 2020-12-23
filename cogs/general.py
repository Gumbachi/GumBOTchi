import random

from common.cfg import bot, poggers_links
from discord.ext import commands


class GeneralCommands(commands.Cog):
    """Handles all of the simple commands such as saying howdy or
    the help command. These commands are unrelated to anything
    color-related and most work in disabled channels
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx):
        """The standard help command."""
        await ctx.send("Help dont exist yet")

    @commands.command(name='howdy')
    async def howdy(self, ctx):
        """Says howdy!"""
        await ctx.send(f"Howdy, {ctx.message.author.mention}!")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen to messages."""

        # ignore the bot user
        if message.author.id == bot.user.id:
            return

        # poggers support
        if message.content in ("pog", "poggies", "poggers"):
            await message.channel.send(random.choice(poggers_links))


def setup(bot):
    bot.add_cog(GeneralCommands(bot))
