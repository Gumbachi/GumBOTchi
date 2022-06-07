"""Holds the queue class for the music player."""
import os
import asyncio
import discord

from .components import *
from .song import Song
import common.utils as utils

from functools import partial

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
        self.history: set[str] = set()
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
        # Nothing playing embed
        if not self.current:
            return discord.Embed(
                title="No Songs Playing",
                description="Hint: Hit the big + button"
            )

        # Generate main player embed
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

    @property
    def controller(self) -> discord.ui.View:
        """Generates the buttons for the music player based on music player state."""
        return MusicControls(self)

    def _synchronous_playnext(self, loop, error):
        asyncio.run_coroutine_threadsafe(self.play_next(), loop)

    async def play_next(self, error=None):
        """Will begin the next song based on the repeat configuration."""

        # only disconnect if not repeatone because repeat one doesnt need to pop queue
        if self.empty and self.repeat_type == RepeatType.REPEATOFF:
            self.history.add(self.current.title)
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

            # Add song to history
            if self.current != None:
                self.history.add(self.current.title)

            self.current = self.songlist.pop(0)

        # Play the song
        audio = discord.FFmpegPCMAudio(self.current.url, **FFMPEG_OPTS)
        voice_client = self.guild.voice_client
        voice_client.play(
            source=audio,
            after=partial(self._synchronous_playnext, voice_client.loop)
        )
        self.paused = False

        await self.update()

    async def set_message(self, message: discord.Message):
        """Replace the active jukebox under the hood"""
        if self.message != None:
            try:
                await self.message.delete()
            except discord.NotFound:
                pass

        self.message = message

    async def enqueue(self, song: Song, person: discord.User = None):
        """Add a song to the music player's queue."""
        self.songlist.append(song)
        if person:
            self.last_action = f"{person.name} queued {song.title}"

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

    def resume(self, person: discord.User = None):
        if person and self.current:
            self.last_action = f"{person.name} resumed {self.current.title}"
        self.paused = False
        self.guild.voice_client.resume()

    def pause(self, person: discord.User = None):
        if person and self.current:
            self.last_action = f"{person.name} paused {self.current.title}"
        self.paused = True
        self.guild.voice_client.pause()

    async def rewind(self, person: discord.User = None):
        if person and self.current:
            self.last_action = f"{person.name} rewound {self.current.title}"

        self.songlist.insert(0, self.current)

        # stopping the voice client will trigger playnext automatically
        self.guild.voice_client.stop()

    async def skip(self, person: discord.User = None):
        if person and self.current:
            self.last_action = f"{person.name} skipped {self.current.title}"

        # stopping the voice client will trigger play next automatically
        self.guild.voice_client.stop()
