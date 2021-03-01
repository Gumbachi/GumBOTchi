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
        if before.id != 244574519027564544 or before.activities == after.activities:
            return

        # Salmon cant play genshin unnoticed
        for activity in after.activities:
            # ignore non-genshin games/activities
            if "Genshin Impact" in activity.name and activity not in before.activities:
                channel = before.guild.get_channel(672919881208954932)
                embed = discord.Embed(
                    title=f"🚨Salmon started playing Genshin Impact at {activity.start}🚨",
                    color=discord.Color.blurple()
                )
                embed.set_footer(text=str(activity.application_id))
                await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(GeneralCommands(bot))
