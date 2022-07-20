import random
from pathlib import Path

import discord
from common.cfg import Role, Tenor, Vip, activities
from discord.commands import slash_command, Option
from discord.ext import tasks


class GeneralCommands(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.activity_cycler.start()

    @slash_command(name="howdy")
    async def howdy(self, ctx: discord.ApplicationContext):
        """Command to check if bot is alive or if you need a friend."""
        await ctx.respond(f"Howdy {ctx.author.mention}!")

    @slash_command(name="purge")
    @discord.default_permissions(administrator=True)
    async def purge(
        self, ctx: discord.ApplicationContext,
        amount: Option(int, "The amount of messages to purge"),
        target: Option(discord.Member, "We all know who this is for") = None
    ):
        """purge a specific amount of messages"""
        await ctx.defer()

        if target:
            messages = await ctx.channel.purge(
                limit=amount,
                check=lambda x: x.author == target
            )
            return await ctx.respond(f"purged {len(messages)} messages")

        messages = await ctx.channel.purge(limit=amount + 1)
        await ctx.respond(f"purged {len(messages)} messages")

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listen to messages."""
        # ignore the bot user
        if message.author.id == self.bot.user.id:
            return

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


def setup(bot: discord.Bot):
    """Entry point for loading cogs."""
    bot.add_cog(GeneralCommands(bot))
