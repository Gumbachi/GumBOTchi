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
        if not ctx.guild:
            return

        message = await ctx.send("*Inserting Quarters*")

        # Fetch the music player or create new one if needed
        if ctx.guild.id in self.players:
            player = self.players[ctx.guild.id]
            await player.replace_message(new_message=message)
        else:
            player = MusicPlayer(message=message)

        # finalize jukebox
        await player.message.edit(
            content=None, embed=player.embed, view=player.controls
        )
        await ctx.respond("Vibe Established 🎧")

    @discord.Cog.listener(name="on_message_delete")
    async def player_delete_listener(self, message: discord.Message):
        """Check if the player message was deleted so it can destroy the player."""
        if not message.guild:
            return

        # guild message is from doesn't have a player
        if message.guild.id not in self.players:
            return

        player = self.players[message.guild.id]
        if message.id == player.message.id:
            player = self.players[message.guild.id]
            await player.message.delete()
            del self.players[message.guild.id]


def setup(bot: discord.Bot):
    """Entry point for loading cogs. Required for all cogs"""
    if os.getenv("FFMPEG_PATH") != "ffmpeg" and not os.path.isfile(
        os.getenv("FFMPEG_PATH", default="")
    ):
        raise FileNotFoundError("Couldn't locate FFMPEG executable")

    bot.add_cog(Music(bot))
