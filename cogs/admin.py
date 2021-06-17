import discord
from discord.ext import commands, tasks
from discord.ext.commands import CommandError, UserInputError
from common.cfg import admin_ids, supermuted_users, activities

from .query_builder import QueryBuilder


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

    @commands.command(name="mute", aliases=["softmute"])
    async def silence_member(self, ctx, member: discord.Member):
        """Mutes a selected member for a certain amount of time"""
        # Normies Cant mute admins. But i can
        if member.guild_permissions.administrator and ctx.author.id != 128595549975871488:
            return await ctx.send("You wish")

        # mute member
        self.muted.add(member.id)
        await ctx.send(embed=discord.Embed(title=f"Muted {member.name}"))

    @commands.command(name="unmute", aliases=["unsilence"])
    async def unsilence_member(self, ctx, member: discord.Member):
        """Unmutes a member."""
        self.muted.discard(member.id)
        supermuted_users.discard(member.id)
        await ctx.send(embed=discord.Embed(title=f"Unmuted {member.name}"))

    @commands.command(name="mute_info", aliases=["minfo"])
    async def show_muted_members(self, ctx):
        """Shows muted members."""
        await ctx.send(f"{self.muted}")

    @commands.command(name="supermute", aliases=["hardmute"])
    async def supermute_member(self, ctx, member: discord.Member):
        """Prevents command use and message from muted members."""
        # Normies Cant mute admins. But i can
        if member.guild_permissions.administrator and ctx.author.id != 128595549975871488:
            return await ctx.send("You wish")

        # supermute users
        supermuted_users.add(member.id)
        await ctx.send(embed=discord.Embed(title=f"Supermuted {member.name}"))

    @commands.command(name="cycle")
    async def cycle_presence(self, ctx):
        """Force changes the bots status"""
        new_activity = next(activities)
        print(f"Cycling Presence to {new_activity}")
        if ctx.author.id in admin_ids:
            await self.bot.change_presence(activity=new_activity)

    @commands.command(name="test")
    async def test_command(self, ctx):
        """Just a test command."""

        instructions = {
            "Keywords": {"text": "Enter all of your keywords 1 by 1 and click the check to finish", "type": list},
            "Distance": {"text": "Enter the max distance", "type": int},
            "Max Price": {"text": "Enter your max price", "type": int},
            "HasImage?": {"text": "DO it need an image", "type": bool},
            "Ping?": {"text": "Should you get pinged?", "type": bool},
        }

        def fn(form):
            form.update({"type": "sss"})
            print(form)

        builder = QueryBuilder(ctx.author, instructions, fn)
        await builder.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen to messages."""
        # ignore the bot user
        if message.author.id == self.bot.user.id:
            return

        if message.author.id in self.muted:
            await message.delete()


def setup(bot):
    bot.add_cog(AdminCommands(bot))
