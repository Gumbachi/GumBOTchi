import discord
from discord.ext import commands, tasks
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
    async def silence_member(self, ctx, member: discord.Member):
        """Mutes a selected member for a certain amount of time"""
        self.muted.add(member.id)
        await ctx.send(embed=discord.Embed(title=f"Muted {member.name}"))

    @commands.command(name="unmute", aliases=["unsilence"])
    async def unsilence_member(self, ctx, member: discord.Member):
        """Unmutes a member."""
        self.muted.discard(member.id)
        await ctx.send(embed=discord.Embed(title=f"Unmuted {member.name}"))

    @commands.command(name="mute_info", aliases=["minfo"])
    async def show_muted_members(self, ctx):
        """Shows muted members."""
        await ctx.send(f"{self.muted}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen to messages."""
        # ignore the bot user
        if message.author.id == bot.user.id:
            return

        if message.author.id in self.muted:
            await message.delete()


def setup(bot):
    bot.add_cog(AdminCommands(bot))
