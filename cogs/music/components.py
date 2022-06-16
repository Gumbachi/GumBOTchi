"""Module holds classes for the buttons of the music player."""
from enum import Enum, auto
# This is here for typing to avoid cyclic import
from typing import TYPE_CHECKING

import discord
from common.cfg import Tenor
from discord import Interaction, SelectOption
from discord.enums import ButtonStyle
from discord.ui import Button, InputText, Modal

from .errors import NoVoiceClient
from .song import Song

if TYPE_CHECKING:
    from .player import MusicPlayer


class RepeatType(Enum):
    REPEATOFF = auto()
    REPEAT = auto()
    REPEATONE = auto()


class Emoji:
    PLAY = "▶️"
    PAUSE = "⏸"
    SKIP = "⏩"
    REWIND = "⏪"
    REPEAT = "🔁"
    REPEATONE = "🔂"
    LEFT = "\u25C0"
    RIGHT = "\u25B6"
    ADD = "➕"
    REFRESH = "🔃"


class MusicControls(discord.ui.View):
    def __init__(self, player: "MusicPlayer"):

        self.player = player

        super().__init__(
            RepeatButton(player),
            PlayPauseButton(player),
            RewindButton(player),
            SkipButton(player),
            LeftButton(player),
            AddButton(player),
            RightButton(player),
            RefreshButton(player),
            timeout=None
        )

        if self.player.history:
            self.add_item(HistoryDropdown(player))

    async def interaction_check(self, interaction: Interaction) -> bool:

        if not isinstance(interaction.user, discord.Member):
            return False

        if not interaction.user.voice:
            return False

        if interaction.custom_id in ("HISTORY", "ADD"):
            return True

        try:
            vcc = self.player.voice_client
        except NoVoiceClient:
            return False

        if interaction.user.voice.channel != vcc.channel:
            print("User is not in same channel as bot")
            return False

        return True


class RepeatButton(Button):
    def __init__(self, player: "MusicPlayer"):

        self.player = player

        match player.repeat:
            case RepeatType.REPEATOFF:
                super().__init__(emoji=Emoji.REPEAT, style=ButtonStyle.gray, row=1)
            case RepeatType.REPEAT:
                super().__init__(emoji=Emoji.REPEAT, style=ButtonStyle.green, row=1)
            case RepeatType.REPEATONE:
                super().__init__(emoji=Emoji.REPEATONE, style=ButtonStyle.green, row=1)

    async def callback(self, interaction: Interaction):
        """Cycle the repeat type."""

        match self.player.repeat:
            case RepeatType.REPEATOFF:
                self.player.repeat = RepeatType.REPEAT
            case RepeatType.REPEAT:
                self.player.repeat = RepeatType.REPEATONE
            case RepeatType.REPEATONE:
                self.player.repeat = RepeatType.REPEATOFF

        await interaction.response.edit_message(view=self.player.controls)


class PlayPauseButton(Button):
    """Handles pause and play interaction with the jukebox."""

    def __init__(self, player: "MusicPlayer"):
        self.player = player

        # voice client does not exist yet
        if player.message.guild and not player.message.guild.voice_client:
            super().__init__(
                emoji=Emoji.PLAY, style=ButtonStyle.green, row=1, disabled=True
            )
            return

        if self.player.voice_client.is_paused():
            super().__init__(emoji=Emoji.PLAY, style=ButtonStyle.green, row=1)
        else:
            super().__init__(emoji=Emoji.PAUSE, style=ButtonStyle.red, row=1)

        self.disabled = not (
            player.voice_client.is_paused() or player.voice_client.is_playing()
        )

    async def callback(self, interaction: Interaction):
        if self.player.voice_client.is_paused():
            self.player.voice_client.resume()
            if self.player.current:
                self.player.footer = f"{interaction.user.name} resumed {self.player.current.title}"
        else:
            self.player.voice_client.pause()
            if self.player.current:
                self.player.footer = f"{interaction.user.name} paused {self.player.current.title}"

        await interaction.response.edit_message(
            embed=self.player.embed, view=self.player.controls
        )


class SkipButton(Button):
    def __init__(self, player: "MusicPlayer"):
        super().__init__(emoji=Emoji.SKIP, row=1)
        self.player = player
        self.disabled = not self.player.current

    async def callback(self, interaction: Interaction):
        self.player.footer = f"{interaction.user.name} skipped {self.player.current.title}"
        self.player.play_next()
        await interaction.response.edit_message(
            embed=self.player.embed, view=self.player.controls
        )


class RewindButton(Button):
    def __init__(self, player: "MusicPlayer"):
        super().__init__(emoji=Emoji.REWIND, row=1)
        self.player = player
        self.disabled = not self.player.current

    async def callback(self, interaction: Interaction):
        new_source = self.player.current.copy()
        self.player.voice_client.source = new_source
        # self.player.voice_client.play()
        self.player.footer = f"{interaction.user.name} rewinded {self.player.current.title}"

        await interaction.response.edit_message(
            embed=self.player.embed, view=self.player.controls
        )


class LeftButton(Button):
    def __init__(self, player: "MusicPlayer"):
        super().__init__(emoji=Emoji.LEFT, row=2)
        self.player = player

    async def callback(self, interaction: Interaction):
        if self.player.page == 1:
            self.player.page = self.player.total_pages
        else:
            self.player.page -= 1

        await interaction.response.edit_message(
            embed=self.player.embed, view=self.player.controls
        )


class AddButton(Button):
    def __init__(self, player: "MusicPlayer"):
        super().__init__(
            custom_id="ADD", emoji=Emoji.ADD, style=ButtonStyle.blurple, row=2
        )
        self.player = player

    async def callback(self, interaction: Interaction):
        await interaction.response.send_modal(SongModal(self.player))


class RightButton(Button):
    def __init__(self, player: "MusicPlayer"):
        self.player = player
        super().__init__(emoji=Emoji.RIGHT, row=2)

    async def callback(self, interaction: Interaction):
        if self.player.page == self.player.total_pages:
            self.player.page = 1
        else:
            self.player.page += 1

        await interaction.response.edit_message(
            embed=self.player.embed, view=self.player.controls
        )


class RefreshButton(Button):
    def __init__(self, player: "MusicPlayer"):
        self.player = player
        super().__init__(emoji=Emoji.REFRESH, row=2)

    async def callback(self, interaction: Interaction):
        await interaction.response.edit_message(
            embed=self.player.embed, view=self.player.controls
        )


class HistoryDropdown(discord.ui.Select):
    def __init__(self, player: "MusicPlayer"):
        self.player = player

        options = [SelectOption(label=songname) for songname in player.history]

        super().__init__(
            custom_id="HISTORY",
            placeholder="Queue up a previously played song",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: Interaction):

        await interaction.response.defer()

        if interaction.user.voice == None:
            return await interaction.response.send_message(Tenor.KERMIT_LOST)

        user_vc = interaction.user.voice.channel

        try:
            _ = self.player.voice_client
        except NoVoiceClient:
            await user_vc.connect()

        try:
            song = await Song.from_query(self.values[0], loop=self.player.voice_client.loop)
        except ValueError:
            self.player.description = f"{interaction.user.name} tried to queue a song and failed"
            await self.player.message.edit(embed=self.player.embed, view=self.player.controls)
            return

        if self.player.current is None:
            self.player.current = song
            self.player.description = f"{interaction.user.name} got this party started with {song.title}"
            self.player.play(song=song)
        else:
            self.player.enqueue(song, interaction.user)

        await self.player.message.edit(embed=self.player.embed, view=self.player.controls)


class SongModal(Modal):
    def __init__(self, player: "MusicPlayer"):
        super().__init__(title="Song Search")
        self.player = player
        self.add_item(
            InputText(
                label="Song Query",
                placeholder="ex. rezonate - rebirth",
                min_length=1,
                max_length=200,
            )
        )

    async def callback(self, interaction: Interaction):

        if interaction.user.voice == None:
            return await interaction.response.send_message(Tenor.KERMIT_LOST)

        user_vc = interaction.user.voice.channel

        query = self.children[0].value

        await interaction.response.defer()

        try:
            _ = self.player.voice_client
        except NoVoiceClient:
            await user_vc.connect()

        try:
            song = await Song.from_query(query, loop=self.player.voice_client.loop)
        except ValueError:
            self.player.description = f"{interaction.user.name} tried to queue a song and failed"
            await self.player.message.edit(embed=self.player.embed, view=self.player.controls)
            await interaction.delete_original_message()
            return

        if self.player.current is None:
            self.player.current = song
            self.player.description = f"{interaction.user.name} got this party started with {song.title}"
            self.player.play(song=song)
        else:
            self.player.enqueue(song, interaction.user)

        await self.player.message.edit(embed=self.player.embed, view=self.player.controls)
        await interaction.delete_original_message()
