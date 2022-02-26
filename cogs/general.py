import random
from pathlib import Path

import discord
from common.cfg import (Role, Tenor, Vip, activities,
                        poggers_activation_phrases, poggers_links)
from discord.commands import slash_command
from discord.ext import tasks


class GeneralCommands(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot):
        self.bot = bot
        self.activity_cycler.start()

    @slash_command(name="howdy")
    async def howdy(self, ctx):
        """Command to check if bot is alive or if you need a friend."""
        await ctx.respond(f"Howdy {ctx.author.mention}!")

    @discord.Cog.listener()
    async def on_message(self, message):
        """Listen to messages."""
        # ignore the bot user
        if message.author.id == self.bot.user.id:
            return

        # pog listener
        if message.content.lower() in poggers_activation_phrases:
            await message.channel.send(random.choice(poggers_links))

        # f listener
        if message.content.lower() == "f":
            await message.channel.send(Tenor.F)

        # rainbow response listener
        if message.author.id == Vip.DIDNA and message.role_mentions:
            if message.role_mentions[0].id == Role.RAINBOW:
                # Get random list of files in response dir
                path = Path('./res/img/r6_responses/')
                response = random.choice(list(path.iterdir()))
                await message.channel.send(file=discord.File(response))

    @tasks.loop(seconds=300)
    async def activity_cycler(self):
        """Cycle the bot's presence to the next activity."""
        await self.bot.change_presence(activity=next(activities))

    @activity_cycler.before_loop
    async def before_activity_cycler(self):
        """Wait to cycle presence until bot is logged in."""
        await self.bot.wait_until_ready()

    @discord.Cog.listener()
    async def on_guild_join(self, guild):
        """Bot has joined a guild."""
        print(f"Joined {guild.name}")

    @discord.Cog.listener()
    async def on_guild_remove(self, guild):
        """Bot is kicked/removed."""
        print(f"Left {guild.name}")


def setup(bot):
    """Entry point for loading cogs."""
    bot.add_cog(GeneralCommands(bot))
