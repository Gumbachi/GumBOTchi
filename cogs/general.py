import random

import discord
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

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """🚨Gotta track when salmon plays Genshin instead of deleting it.🚨"""
        # only salm and activity tracked
        if before.id != 244574519027564544:
            return

        genshin_app_id = 762434991303950386

        # isolate new app id
        before_ids = [a.application_id for a in before.activities]
        after_ids = [a.application_id for a in after.activities]
        new_activity_ids = set(after_ids) - set(before_ids)

        if not new_activity_ids:
            return

        # Salmon cant play genshin unnoticed
        for activity_id in new_activity_ids:
            # ignore non-genshin games/activities
            if activity_id == genshin_app_id:
                channel = before.guild.get_channel(672919881208954932)
                embed = discord.Embed(
                    title=f"🚨Salmon started playing Genshin Impact🚨",
                    color=discord.Color.blurple()
                )
                await channel.send(embed=embed)
                break


def setup(bot):
    bot.add_cog(GeneralCommands(bot))
