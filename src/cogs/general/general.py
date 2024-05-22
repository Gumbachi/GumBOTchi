import random
from pathlib import Path

import discord
from common.cfg import Role, Tenor, Vip, activities
from discord.commands import option, slash_command, message_command
from discord.ext.tasks import loop


class GeneralCommands(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.activity_cycler.start()

    @slash_command(name="howdy")
    async def howdy(self, ctx: discord.ApplicationContext):
        """Command to check if bot is alive or if you need a friend."""
        await ctx.respond(f"Howdy {ctx.author.display_name}!")

    @slash_command(name="purge")
    @discord.default_permissions(administrator=True)
    @option(name="amount", description="The amount of messages to SEARCH THROUGH. If target is not specified this is the amount to delete")
    @option(name="target", description="We all know who this is for", required=False)
    async def purge(self, ctx: discord.ApplicationContext, amount: int, target: discord.Member):
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

    # User commands and message commands can have spaces in their names
    @message_command(name="Toggle Reddit Link")
    async def toggle_reddit_link(self, ctx: discord.ApplicationContext, message: discord.Message):
        """Toggle reddit links between old reddit and new reddit"""
        if message.content.lower().startswith("https://old.reddit.com"):
            return await ctx.respond(message.content.replace("https://old.reddit.com", "https://reddit.com"))
        
        if message.content.lower().startswith("https://reddit.com"):
            await ctx.respond(message.content.replace("https://reddit.com", "https://old.reddit.com"))

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

        # my man listener
        if message.content.lower() == "my man":
            await message.channel.send(Tenor.MY_MAN)

    @loop(seconds=300)
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
