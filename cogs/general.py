import random

import discord
import common.cfg as cfg
import common.database as db
from discord.ext import commands, tasks
from .catalog import Catalog
import docs.docs as docs


class GeneralCommands(commands.Cog):
    """Handles all of the simple commands such as saying howdy or
    the help command.
    """

    def __init__(self, bot):
        self.bot = bot
        self.activity_switcher.start()

    @commands.command(name="help", aliases=["halp"])
    async def help(self, ctx):
        """The standard help command."""
        catalog = Catalog(docs.help_book(ctx.prefix))
        await catalog.send(ctx.channel)

    @commands.command(name='howdy')
    async def howdy(self, ctx):
        """Says howdy!"""
        await ctx.send(f"Howdy, {ctx.message.author.mention}!")

    @commands.command(name="prefix", aliases=["gumbotchiprefix"])
    @commands.has_guild_permissions(manage_guild=True)
    async def change_server_prefix(self, ctx, *, new_prefix):
        """Change the bots prefix for the guild."""
        db.guilds.update_one(
            {"_id": ctx.guild.id},
            {"$set": {"prefix": new_prefix}}
        )
        await ctx.send(f"Prefix changed to `{new_prefix}`")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen to messages."""
        # ignore the bot user
        if message.author.id == self.bot.user.id:
            return

        # poggers listener
        if message.content.lower() in cfg.poggers_activation_phrases:
            await message.channel.send(random.choice(cfg.poggers_links))

        # guh listener
        if message.content.lower() == "guh":
            guh = self.bot.get_emoji(755546594446671963)
            if guh:
                await message.channel.send(str(guh))

        # f listener
        if message.content.lower() == "f":
            await message.channel.send("https://tenor.com/view/press-f-pay-respect-coffin-burial-gif-12855021")

        # rainbow listener
        if message.author.id == 235902262168256515 and message.role_mentions:
            if message.role_mentions[0].id == 853368252474196018:
                await message.channel.send(file=discord.File('resources/images/hereitcomes.png'))

    @tasks.loop(seconds=300)
    async def activity_switcher(self):
        await self.bot.change_presence(activity=next(cfg.activities))

    @activity_switcher.before_loop
    async def before_activity_switcher(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Add new guild to database."""
        db.guilds.insert_one(
            {
                "_id": guild.id,
                "prefix": "!",
                "groups": []
            }
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Delete guild from database if bot is kicked/removed"""
        db.guilds.delete_one({"_id": guild.id})


def setup(bot):
    bot.add_cog(GeneralCommands(bot))
