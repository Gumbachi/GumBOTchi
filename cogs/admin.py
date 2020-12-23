from discord.ext import commands
from common.cfg import bot, admin_ids


class AdminCommands(commands.Cog):
    """Handles all of the simple commands such as saying howdy or
    the help command. These commands are unrelated to anything
    color-related and most work in disabled channels
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='purge')
    async def delete_messages(self, ctx, amount):
        """purge a set amount of messages!"""
        if ctx.author.id in admin_ids:
            await ctx.channel.purge(limit=int(amount)+1)
            await ctx.send(f"purged {amount} messages", delete_after=2)


def setup(bot):
    bot.add_cog(AdminCommands(bot))
