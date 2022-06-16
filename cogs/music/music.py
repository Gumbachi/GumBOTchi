import os

import discord
from discord import slash_command

from .player import MusicPlayer


class Music(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.players: dict[int, MusicPlayer] = {}

    @slash_command(name="jukebox")
    async def send_player(self, ctx: discord.ApplicationContext):
        """Get the music player and its buttons."""

        message = await ctx.send("*Inserting Quarters*")

        # Fetch the music player or create new one if needed
        if ctx.guild.id in self.players:
            player = self.players[ctx.guild.id]
            await player.replace_message(new_message=message)
        else:
            player = MusicPlayer(message=message)
            self.players[ctx.guild.id] = player

        # finalize jukebox
        await player.message.edit(
            content=None, embed=player.embed, view=player.controls
        )
        await ctx.respond("Vibe Established 🎧")


def setup(bot: discord.Bot):
    """Entry point for loading cogs. Required for all cogs"""
    if os.getenv("FFMPEG_PATH") != "ffmpeg" and not os.path.isfile(
        os.getenv("FFMPEG_PATH", default="")
    ):
        raise FileNotFoundError("Couldn't locate FFMPEG executable")

    bot.add_cog(Music(bot))
