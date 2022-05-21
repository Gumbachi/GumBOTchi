import discord
from discord import message_command


class Emojifier(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot):
        self.bot = bot

    @message_command(name="emojify")
    async def emojify(self, ctx: discord.ApplicationContext, message: discord.Message):
        """Automatically convert an image into an emoji."""
        await ctx.respond("Yea wouldn't it be nice")


def setup(bot):
    """Entry point for loading cogs. Required for all cogs"""
    bot.add_cog(Emojifier(bot))
