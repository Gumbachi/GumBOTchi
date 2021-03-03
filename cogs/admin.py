import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import CommandError, UserInputError
from common.cfg import bot, admin_ids
import datetime


class AdminCommands(commands.Cog):
    """Handles all of the powerful commands."""

    def __init__(self, bot):
        self.bot = bot
        self.muted = set()

    def cog_check(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            raise CommandError(f"Get your weak ass permissions outta here")
        return True

    @commands.command(name="purge")
    async def delete_messages(self, ctx, amount):
        """purge a set amount of messages!"""
        if ctx.author.id in admin_ids:
            await ctx.channel.purge(limit=int(amount)+1)
            await ctx.send(f"purged {amount} messages", delete_after=2)

    @commands.command(name="mute", aliases=["silence"])
    async def silence_member(self, ctx, member: discord.Member, mute_time=None):
        """Mutes a selected member for a certain amount of time"""
        self.muted.add(member.id)
        try:
            # send message and sleep
            time = int(mute_time)
            await ctx.send(f"{member.name} muted for {datetime.timedelta(seconds=time)}")
            asyncio.sleep(time)
        except ValueError:
            raise commands.UserInputError("Needs to be a number. dumbass")
        self.muted.discard(member.id)

    @commands.command(name="unmute", aliases=["unsilence"])
    async def unsilence_member(self, ctx, member: discord.Member):
        """Unmutes a member."""
        self.muted.discard(member.id)
        await ctx.send(f"Unmuted {member.name}")

    @commands.command(name="mute_info", aliases=["minfo"])
    async def unsilence_member(self, ctx, member: discord.Member):
        """Shows muted members."""
        await ctx.send(f"{self.muted}")


def setup(bot):
    bot.add_cog(AdminCommands(bot))
