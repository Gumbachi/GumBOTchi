import os

import discord
from discord.commands import slash_command
from discord.ext import tasks
from discord.ext.commands import CommandError

from .player import MusicPlayer


class Music(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.player_loop.start()

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
        mp.message = await ctx.send(embed=mp.embed, view=mp.controller)
        await ctx.respond(mp.message.jump_url)

    @tasks.loop(seconds=5)
    async def player_loop(self):
        """Checks the voice clients to see if one can go to next song"""
        for client in self.bot.voice_clients:

            # Voice client is already playing or paused so skip it
            if client.is_playing() or client.is_paused():
                continue

            mp = self.get_player(client.guild)
            await mp.play_next()
            await mp.update()

    @player_loop.before_loop
    async def before_player_loop(self):
        await self.bot.wait_until_ready()  # Wait until the bot logs in


def setup(bot):
    """Entry point for loading cogs. Required for all cogs"""
    if os.getenv("FFMPEG_PATH") != "ffmpeg" and not os.path.isfile(os.getenv("FFMPEG_PATH")):
        raise FileNotFoundError("Couldn't locate FFMPEG executable")

    bot.add_cog(Music(bot))
