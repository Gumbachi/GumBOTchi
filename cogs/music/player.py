"""Holds the queue class for the music player."""
from dataclasses import dataclass, field

import common.utils as utils
import discord

from .components import MusicControls, RepeatType
from .errors import NoVoiceClient
from .song import Song


@dataclass
class MusicPlayer:
    message: discord.Message  # The message holding the music player

    # Song Queue
    repeat: RepeatType = RepeatType.REPEATOFF
    current: Song | None = None
    history: set[str] = field(default_factory=set)
    songlist: list[Song] = field(default_factory=list)

    # Display
    page: int = 1
    pagesize: int = 3
    description: str = ""
    footer: str = ""

    def __repr__(self):
        return f"MusicPlayer(current={self.current}, songlist={self.songlist}, history={self.history})"

    @property
    def voice_client(self) -> discord.VoiceClient:
        """Fetch the voice client for the guild associated with the player."""
        if self.message.guild and self.message.guild.voice_client:
            if isinstance(self.message.guild.voice_client, discord.VoiceClient):
                return self.message.guild.voice_client

        raise NoVoiceClient("Voice Client Not Found")

    @property
    def total_pages(self):
        amount = len(utils.chunk(self.songlist, self.pagesize))
        return 1 if amount == 0 else amount

    @property
    def _nothing_playing_embed(self):
        embed = discord.Embed(
            title="No Songs Playing", description=f"Hint: Hit the big **+** button"
        )
        embed.set_footer(text="Buttons won't work until the bot is singing")
        return embed

    @property
    def embed(self) -> discord.Embed:
        """Generates a discord Embed object based on music player state."""

        if not self.current:
            return self._nothing_playing_embed

        embed = discord.Embed(
            title="GumBOTchi's Jukebox", description=f"*{self.description}*\n"
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
                value="\n\n".join(
                    [str(song) for song in song_chunks[self.page - 1]]
                ),
                inline=False,
            )
        return embed

    @property
    def controls(self) -> discord.ui.View:
        """Generates the buttons for the music player based on music player state."""
        return MusicControls(player=self)

    async def replace_message(self, new_message: discord.Message):
        """Replace the holder message for the player"""
        old_message = self.message

        try:
            await old_message.delete()
        except discord.NotFound:
            pass  # message was probably deleted which is fine

        self.message = new_message

    # MUSIC PLAYER ACTIONS

    def enqueue(self, song: Song, person: discord.User | discord.Member | None):
        """Add a song to the music player's queue."""
        self.songlist.append(song)

        if person:
            self.description = f"{person.name} queued {song.title}"

    def play(self, song: Song):
        """Play the provided song"""
        if self.voice_client.is_playing():
            self.voice_client.source = song
        else:
            self.voice_client.play(source=song, after=self.play_next)

    def load_next_song(self):
        """Load the next song into the current song based on repeat type"""

        if self.current:
            self.history.add(self.current.title)

        match self.repeat:
            case RepeatType.REPEATOFF:
                if not self.songlist:
                    self.current = None
                else:
                    self.current = self.songlist.pop(0)
            case RepeatType.REPEAT:
                self.songlist.append(self.current.copy())
                self.current = self.songlist.pop(0)
            case RepeatType.REPEATONE:
                if self.current is not None:
                    self.current = self.current.copy()

    def play_next(self, error: Exception | None = None):
        """Will begin the next song based on the repeat configuration."""

        if error:
            print(f"PROBLEM PLAYING SONG: {error}")

        self.load_next_song()

        if self.page > self.total_pages:
            self.page -= 1

        # disconnect if needed
        if self.current == None:
            self.voice_client.loop.create_task(
                self.message.edit(embed=self.embed)
            )
            self.voice_client.loop.create_task(self.voice_client.disconnect())
            return
        else:
            self.play(self.current)

        self.voice_client.loop.create_task(self.message.edit(embed=self.embed))
