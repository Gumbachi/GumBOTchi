import discord
from discord.commands import slash_command, Option
from discord.ext.commands import MissingPermissions


class AdminCommands(discord.Cog):
    """Handles all of the powerful commands."""

    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="purge")
    async def purge(self, ctx, amount: Option(int, "The amount of messages to purge", min_value=1, max_value=99)):
        """purge a specific amount of messages"""

        # Admin check
        if not ctx.author.guild_permissions.administrator:
            raise MissingPermissions()

        await ctx.channel.purge(limit=amount + 1)
        await ctx.respond(f"purged {amount} messages")


def setup(bot):
    bot.add_cog(AdminCommands(bot))
