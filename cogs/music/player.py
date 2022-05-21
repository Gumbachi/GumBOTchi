"""Holds the queue class for the music player."""
import os

import discord
from discord.ui import View
from discord.enums import ButtonStyle

from .components import *
from .song import Song
import common.utils as utils

FFMPEG_OPTS = {
    "executable": os.getenv("FFMPEG_PATH"),
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


class MusicPlayer():
    """A player class with only 1 belonging to each guild."""
    PAGESIZE = 3

    def __init__(self, guild: discord.Guild):
        self.guild: discord.Guild = guild
        self.message: discord.Message = None
        self.repeat_type: RepeatType = RepeatType.REPEATOFF
        self.paused = True
        self.current: Song = None
        self.current_page = 1
        self.queue_displayed = False
        self.last_action: str = "TODO"
        self.songlist: list[Song] = []

    @property
    def playing(self):
        return not self.paused

    @property
    def empty(self):
        return len(self.songlist) == 0

    @property
    def total_pages(self):
        amount = len(utils.chunk(self.songlist, self.PAGESIZE))
        return 1 if amount == 0 else amount

    @property
    def embed(self) -> discord.Embed:
        """Generates a discord Embed object based on music player state."""
        if not self.current:
            return discord.Embed(
                title="No Songs Playing",
                description="Hint: Hit the big + button"
            )

        return self.queue

    @property
    def controller(self) -> discord.ui.View:
        """Generates the buttons for the music player based on music player state."""
        play_button = PlayButton(self) if self.paused else PauseButton(self)
        rewind_button = RewindButton(self)
        skip_button = SkipButton(self)

        # Handle displaying the repeat button
        if self.repeat_type == RepeatType.REPEAT:
            repeat_button = RepeatButton(self)
        elif self.repeat_type == RepeatType.REPEATONE:
            repeat_button = RepeatOneButton(self)
        else:
            repeat_button = RepeatOffButton(self)

        left_button = LeftButton(self)
        add_button = AddButton(self)
        right_button = RightButton(self)

        return View(
            repeat_button, play_button, rewind_button, skip_button,
            left_button, add_button, right_button,
            timeout=None
        )

    @property
    def queue(self) -> discord.Embed:
        """Generates the song queue discord Embed based on the songlist and state of the player."""
        embed = discord.Embed(
            title="GumBOTchi's Jukebox",
            description=f"*{self.last_action}*\n"
        )
        embed.set_thumbnail(url=self.current.thumbnail)
        embed.add_field(
            name="NOW PLAYING",
            value=f"[{self.current.title}]({self.current.webpage_url})\n",
            inline=False
        )

        if self.songlist:

            song_chunks = utils.chunk(self.songlist, self.PAGESIZE)

            embed.add_field(
                name=f"UP NEXT  •  {len(self.songlist)} Songs  •  Page {self.current_page}/{self.total_pages}",
                value="\n\n".join(
                    [song.embed_format for song in song_chunks[self.current_page-1]]),
                inline=False
            )

        return embed

    async def enqueue(self, song: Song):
        """Add a song to the music player's queue."""
        self.songlist.append(song)
        self.last_action = f"Queued {song.title}"

    async def play_next(self):
        """Will begin the next song based on the repeat configuration."""

        # only disconnect if not repeatone because repeat one doesnt need to pop queue
        if self.empty and self.repeat_type == RepeatType.REPEATOFF:
            self.current = None
            self.paused = True
            await self.update()
            return await self.guild.voice_client.disconnect()

        # Repeat should loop the entire list
        if self.repeat_type == RepeatType.REPEAT:
            self.songlist.append(self.current)
            self.current = self.songlist.pop(0)

        # Repeat off should just burn through the songs
        elif self.repeat_type == RepeatType.REPEATOFF:
            self.current = self.songlist.pop(0)

        # Play the song
        audio = discord.FFmpegPCMAudio(self.current.url, **FFMPEG_OPTS)
        self.guild.voice_client.play(audio)
        self.paused = False

    async def update(self):
        """Attempt to update the active player message."""
        # Need to handle natural page reduction from playing songs
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages

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

    async def rewind(self):
        rtype = self.repeat_type
        self.repeat_type = RepeatType.REPEATONE
        await self.skip()
        self.repeat_type = rtype

    async def skip(self):
        self.guild.voice_client.stop()
        await self.play_next()
