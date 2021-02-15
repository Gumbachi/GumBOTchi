import random

import common.cfg as cfg
from common.cfg import bot
from discord.ext import commands


class GeneralCommands(commands.Cog):
    """Handles all of the simple commands such as saying howdy or
    the help command.
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

        # poggers listener
        if message.content.lower() in cfg.poggers_activation_phrases:
            await message.channel.send(random.choice(cfg.poggers_links))

        # guh listener
        if message.content.lower() == "guh":
            guh = bot.get_emoji(755546594446671963)
            if guh:
                await message.channel.send(str(guh))


def setup(bot):
    bot.add_cog(GeneralCommands(bot))
