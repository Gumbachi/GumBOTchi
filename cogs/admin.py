import discord
from discord.commands import slash_command
from discord.ext.commands.errors import MissingPermissions
from common.cfg import dev_guilds


class AdminCommands(discord.Cog):
    """Handles all of the powerful commands."""

    def __init__(self, bot):
        self.bot = bot

    @slash_command(guild_ids=dev_guilds)
    async def purge(self, ctx, amount: int):
        """purge a set amount of messages!"""

        # Admin check
        if not ctx.author.guild_permissions.administrator:
            raise MissingPermissions()

        await ctx.channel.purge(limit=int(amount) + 1)
        await ctx.respond(f"purged {amount} messages")


def setup(bot):
    bot.add_cog(AdminCommands(bot))
