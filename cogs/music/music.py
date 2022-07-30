import os

import discord
from discord import guild_only, slash_command

from .player import MusicPlayer


class Music(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.players: dict[int, MusicPlayer] = {}

    @slash_command(name="jukebox")
    @guild_only()
    async def send_player(self, ctx: discord.ApplicationContext):
        """Get the music player and its buttons."""

        # Fetch the music player or create new one if needed
        if ctx.guild.id in self.players:
            player = self.players[ctx.guild.id]
            if player.message:
                try:
                    await player.message.delete()
                except discord.NotFound:
                    pass
        else:
            player = MusicPlayer(ctx.guild)
            self.players[ctx.guild.id] = player

        await ctx.respond("Vibe Established 🎧")
        player.message = await ctx.send(embed=player.embed, view=player.controls)


def setup(bot: discord.Bot):
    """Entry point for loading cogs. Required for all cogs"""
    ffmpeg_path = os.getenv("FFMPEG_PATH") or ""
    if ffmpeg_path != "ffmpeg" and not os.path.isfile(ffmpeg_path):
        raise FileNotFoundError("Couldn't locate FFMPEG executable")

    bot.add_cog(Music(bot))
