"""Holds the queue class for the music player."""
import os

import discord
from discord.ui import View
from discord.enums import ButtonStyle

from .buttons import *
from .song import Song

FFMPEG_OPTS = {
    "executable": os.getenv("FFMPEG_PATH"),
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


class MusicPlayer():
    """A player class with only 1 belonging to each guild."""

    def __init__(self, guild: discord.Guild):
        self.guild: discord.Guild = guild
        self.message: discord.Message = None
        self.repeat_type: RepeatType = RepeatType.REPEATOFF
        self.paused = False
        self.current: Song = None
        self.queue_displayed = False
        self.songlist: list[Song] = []

    @property
    def playing(self):
        return not self.paused

    @property
    def empty(self):
        return len(self.songlist) == 0

    @property
    def embed(self) -> discord.Embed:
        """Generates a discord Embed object based on music player state."""
        if not self.current:
            return discord.Embed(
                title="No Songs Playing",
                description="`/play` is the solution"
            )

        if self.queue_displayed:
            return self.queue

        embed = discord.Embed(
            title="NOW PLAYING",
            description=f"[{self.current.title}]({self.current.webpage_url})\n{self.current.duration}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=self.current.thumbnail)
        return embed

    @property
    def controller(self) -> discord.ui.View:
        """Generates the buttons for the music player based on music player state."""
        play_button = PlayButton(self) if self.paused else PauseButton(self)
        skip_button = SkipButton(self)

        # Handle displaying the repeat button
        if self.repeat_type == RepeatType.REPEAT:
            repeat_button = RepeatButton(self)
        elif self.repeat_type == RepeatType.REPEATONE:
            repeat_button = RepeatOneButton(self)
        else:
            repeat_button = RepeatOffButton(self)

        # Handle displaying the queue button
        if self.queue_displayed:
            queue_button = QueueButton(self, style=ButtonStyle.green)
        else:
            queue_button = QueueButton(self)

        return View(repeat_button, play_button, skip_button, queue_button, timeout=None)

    @property
    def queue(self) -> discord.Embed:
        """Generates the song queue discord Embed based on the songlist and state of the player."""
        embed = discord.Embed(
            title="QUEUEUEUEUEUE",
            description=f"**NOW PLAYING**\n[{self.current.title}]({self.current.webpage_url})"
        )
        embed.set_thumbnail(url=self.current.thumbnail)
        embed.set_footer(
            text=f"Shows up to 5 songs. Hidden: {max(0, len(self.songlist) - 5)}")

        for i, song in enumerate(self.songlist[:5], 1):
            embed.add_field(
                name=f"{i}. {song.title}",
                value=f"🕒 {song.duration} - [Link]({song.webpage_url})",
                inline=False
            )
        return embed

    def enqueue(self, song: Song):
        """Add a song to the music player's queue."""
        self.songlist.append(song)

    async def play_next(self):
        """Will begin the next song based on the repeat configuration."""

        # only disconnect if not repeatone because repeat one doesnt need to pop queue
        if self.empty and self.repeat_type != RepeatType.REPEATONE:
            return await self.guild.voice_client.disconnect()

        # Repeat should loop the entire list
        if self.repeat_type == RepeatType.REPEAT:
            self.songlist.append(self.current)
            self.current = self.songlist.pop(0)

        # Repeat off should just burn through the songs
        elif self.repeat_type == RepeatType.REPEATOFF:
            self.current = self.songlist.pop(0)

        # update player message
        await self.update()

        # Play the song
        audio = discord.FFmpegPCMAudio(self.current.url, **FFMPEG_OPTS)
        self.guild.voice_client.play(audio)
        self.paused = False

    async def update(self):
        """Attempt to update the active player message."""
        if self.message:
            try:
                await self.message.edit(embed=self.embed, view=self.controller)
            except discord.NotFound:
                pass

    def resume(self):
        self.paused = False
        self.guild.voice_client.resume()

    def pause(self):
        self.paused = True
        self.guild.voice_client.pause()

    async def skip(self):
        self.guild.voice_client.stop()
        await self.play_next()
