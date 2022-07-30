"""Holds the queue class for the music player."""
from dataclasses import dataclass, field

import common.utils as utils
import discord
from cogs.music.components.history_dropdown import HistoryDropdown

from .components.music_controls import MusicControls
from .enums import RepeatType
from .errors import NoVoiceClient
from .song import Song


@dataclass(slots=True)
class MusicPlayer:
    guild: discord.Guild
    message: discord.Message = None
    view: MusicControls = None

    # Song Queue
    repeat: RepeatType = RepeatType.REPEATOFF
    _current: Song | None = None
    history: set[str] = field(default_factory=set)
    songlist: list[Song] = field(default_factory=list)

    # Display
    _page: int = 1
    pagesize: int = 3
    description: str = ""
    footer: str = ""

    @property
    def page(self):
        if self._page > self.total_pages:
            self._page = self.total_pages
        return self._page

    @page.setter
    def page(self, page: int):
        if page > self.total_pages:
            self._page = self.total_pages
        elif page < 1:
            self._page = 1
        else:
            self._page = page

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, new: Song | None):
        self._current = new

        if new is None:
            self.voice_client.stop()
            return

        if self.voice_client.is_playing() or self.voice_client.is_paused():
            self.voice_client.source = new
        else:
            self.voice_client.play(new, after=self.load_next_song)

    @property
    def voice_client(self) -> discord.VoiceClient:
        """Fetch the voice client for the guild associated with the player."""
        vcc = self.guild.voice_client
        if vcc:
            if isinstance(vcc, discord.VoiceClient):
                return vcc

        raise NoVoiceClient("Voice Client Not Found")

    @property
    def total_pages(self):
        amount = len(utils.chunk(self.songlist, self.pagesize))
        return 1 if amount == 0 else amount

    @property
    def _nothing_playing_embed(self):
        embed = discord.Embed(
            title="No Songs Playing",
            description=f"Hint: Hit the big **+** button"
        )
        embed.set_footer(text="Buttons won't work until the bot is singing")
        return embed

    @property
    def embed(self) -> discord.Embed:
        """Generates a discord Embed object based on music player state."""

        if not self.current:
            return self._nothing_playing_embed

        embed = discord.Embed(
            title="GumBOTchi's Jukebox",
            description=f"*{self.description}*\n"
        )
        embed.set_thumbnail(url=self.current.thumbnail)
        embed.set_footer(text=utils.ellipsize(self.footer))
        embed.add_field(
            name="NOW PLAYING",
            value=f"[{self.current.title}]({self.current.webpage_url})\n",
            inline=False,
        )

        if self.songlist:
            song_chunks = utils.chunk(self.songlist, self.pagesize)
            embed.add_field(
                name=f"UP NEXT  •  {len(self.songlist)} Songs  •  Page {self.page}/{self.total_pages}",
                value="\n\n".join([str(song) for song in song_chunks[self.page - 1]]),
                inline=False,
            )
        return embed

    @property
    def controls(self) -> discord.ui.View:
        """Generates the buttons for the music player based on music player state."""
        self.view = MusicControls(player=self)
        return self.view

    def enqueue(self, song: Song, person: discord.Member):
        """Add a song to the music player's queue."""
        self.songlist.append(song)
        self.description = f"{person.nick or person.name} queued {song.title}"

    def play(self, song: Song):
        """Play the provided song"""
        self.current = song

    def load_next_song(self, error: Exception | None = None):
        """Load the next song into the current song based on repeat type"""

        if self.current != None:
            self.history.add(self.current.title)

        match self.repeat:
            case RepeatType.REPEATOFF:
                if self.songlist:
                    self.current = self.songlist.pop(0)
                else:
                    self.current = None

            case RepeatType.REPEAT:
                self.songlist.append(self.current.copy())
                self.current = self.songlist.pop(0)
            case RepeatType.REPEATONE:
                if self.current is not None:
                    self.current = self.current.copy()

        # Needs to update the history. NO TOUCHY i spent days on this
        if self.message:

            if len(self.view.children) == 8 and self.history:
                print("DROPDOWN ADDED")
                self.view.add_item(HistoryDropdown(self))

            self.voice_client.loop.create_task(
                self.message.edit(embed=self.embed, view=self.view)
            )

        # disconnect if needed
        if self.current is None:
            self.voice_client.loop.create_task(self.voice_client.disconnect())
