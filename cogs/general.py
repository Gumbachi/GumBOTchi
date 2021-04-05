import random

import discord
import common.cfg as cfg
import common.database as db
from common.cfg import bot
from discord.ext import commands
from .catalog import Catalog
import docs.docs as docs


class GeneralCommands(commands.Cog):
    """Handles all of the simple commands such as saying howdy or
    the help command.
    """

    def __init__(self, bot):
        self.bot = bot

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

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """🚨Gotta track when salmon plays Genshin instead of deleting it.🚨"""
        # only salm and activity tracked
        if before.id != 244574519027564544:
            return

        genshin_app_id = 762434991303950386

        # isolate new app id
        new_activities = set(after.activities) - set(before.activities)

        if not new_activities:
            return

        try:
            # Check if genshin impact
            if new_activities[0].application_id == genshin_app_id:
                channel = before.guild.get_channel(672919881208954932)
                if not channel:
                    return
                embed = discord.Embed(
                    title=f"🚨 Salmon started playing Genshin Impact 🚨",
                    color=discord.Color.blurple()
                )
                return await channel.send(embed=embed)
        except:
            pass

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
