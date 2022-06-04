import os
import random

import discord
from discord.commands import slash_command
from cogs.soundboard.components import SoundboardMenu


class SoundBoard(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.response_lines = [
            "*Inserting Quarters*",
            "Vibe Established 🎧",
            "Queueing up so much country music",
            "Dropping the needle"
        ]

    @slash_command(name="soundboard")
    async def send_soundboard(self, ctx: discord.ApplicationContext):
        """Send the soundplayer"""
        await ctx.respond(random.choice(self.response_lines))
        await ctx.send("Soundboard", view=SoundboardMenu())


def setup(bot: discord.Bot):
    """Entry point for loading cogs. Required for all cogs"""
    if os.getenv("FFMPEG_PATH") != "ffmpeg" and not os.path.isfile(os.getenv("FFMPEG_PATH")):
        raise FileNotFoundError("Couldn't locate FFMPEG executable")

    bot.add_cog(SoundBoard(bot))
