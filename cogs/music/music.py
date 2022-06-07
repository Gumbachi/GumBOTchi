import os
import random

import discord
from discord.commands import slash_command
from discord.ext import tasks

from .player import MusicPlayer


class Music(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.response_lines = [
            "*Inserting Quarters*",
            "Vibe Established 🎧",
            "Queueing up so much country music",
            "Dropping the needle"
        ]

    def get_player(self, guild: discord.Guild) -> MusicPlayer:
        """Return active player or make a new one."""
        try:
            return self.players[guild.id]
        except KeyError:
            player = MusicPlayer(guild)
            self.players[guild.id] = player
            return player

    @slash_command(name="jukebox")
    async def send_player(self, ctx: discord.ApplicationContext):
        """Get the music player and its buttons."""
        mp = self.get_player(ctx.guild)
        await ctx.respond(random.choice(self.response_lines))

        message = await ctx.send(embed=mp.embed, view=mp.controller)
        await mp.set_message(message)


def setup(bot):
    """Entry point for loading cogs. Required for all cogs"""
    if os.getenv("FFMPEG_PATH") != "ffmpeg" and not os.path.isfile(os.getenv("FFMPEG_PATH")):
        raise FileNotFoundError("Couldn't locate FFMPEG executable")

    bot.add_cog(Music(bot))
