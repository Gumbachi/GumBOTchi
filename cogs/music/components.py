"""Module holds classes for the buttons of the music player."""
from enum import Enum

import discord
from discord import Interaction, SelectOption
from discord.enums import ButtonStyle
from discord.ui import Button, InputText, Modal, View

from common.cfg import Tenor
from cogs.music.song import Song

# This is here for typing to avoid cyclic import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cogs.music.player import MusicPlayer


class RepeatType(Enum):
    REPEATOFF = 1
    REPEAT = 2
    REPEATONE = 3


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
    def __init__(self, player: 'MusicPlayer'):

        self.player = player

        super().__init__(
            RepeatButton(player),
            PlayPauseButton(player),
            RewindButton(player),
            SkipButton(player),
            LeftButton(player),
            AddButton(player),
            RightButton(player),
            RefreshButton(player)
        )

        if self.player.history:
            self.add_item(HistoryDropdown(player))

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.voice is None:
            return False

        voice_client = interaction.guild.voice_client

        if voice_client and interaction.user.voice.channel != voice_client.channel:
            print("User is not in same channel as bot")
            return False

        return True


class RepeatButton(Button):
    def __init__(self, player: 'MusicPlayer'):

        self.player = player

        match player.repeat_type:
            case RepeatType.REPEATOFF:
                super().__init__(emoji=Emoji.REPEAT, style=ButtonStyle.gray, row=1)
            case RepeatType.REPEAT:
                super().__init__(emoji=Emoji.REPEAT, style=ButtonStyle.green, row=1)
            case RepeatType.REPEATONE:
                super().__init__(emoji=Emoji.REPEATONE, style=ButtonStyle.green, row=1)

    async def callback(self, interaction: Interaction):
        """Cycle the repeat type."""

        match self.player.repeat_type:
            case RepeatType.REPEATOFF:
                self.player.repeat_type = RepeatType.REPEAT
            case RepeatType.REPEAT:
                self.player.repeat_type = RepeatType.REPEATONE
            case RepeatType.REPEATONE:
                self.player.repeat_type = RepeatType.REPEATOFF

        await interaction.response.edit_message(view=self.player.controller)


class PlayPauseButton(Button):
    """Handles pause and play interaction with the jukebox."""

    def __init__(self, player: 'MusicPlayer'):
        self.player = player
        disabled = player.current == None
        if player.paused:
            super().__init__(emoji=Emoji.PLAY, style=ButtonStyle.green, disabled=disabled, row=1)
        else:
            super().__init__(emoji=Emoji.PAUSE, style=ButtonStyle.red, disabled=disabled, row=1)

    async def callback(self, interaction: Interaction):
        if self.player.paused:
            self.player.resume(person=interaction.user)
        else:
            self.player.pause(person=interaction.user)

        await interaction.response.edit_message(embed=self.player.embed, view=self.player.controller)


class SkipButton(Button):
    def __init__(self, player: 'MusicPlayer'):
        super().__init__(emoji=Emoji.SKIP, row=1)
        self.player = player

    async def callback(self, interaction: Interaction):
        await self.player.skip(person=interaction.user)
        await interaction.response.edit_message(embed=self.player.embed, view=self.player.controller)


class RewindButton(Button):
    def __init__(self, player: 'MusicPlayer'):
        super().__init__(emoji=Emoji.REWIND, row=1)
        self.player = player

    async def callback(self, interaction: Interaction):
        await self.player.rewind(person=interaction.user)
        await interaction.response.edit_message(embed=self.player.embed, view=self.player.controller)


class LeftButton(Button):
    def __init__(self, player: 'MusicPlayer'):
        disabled = player.current_page == 1
        super().__init__(emoji=Emoji.LEFT, row=2, disabled=disabled)
        self.player = player

    async def callback(self, interaction: Interaction):
        self.player.current_page -= 1
        await interaction.response.edit_message(embed=self.player.embed, view=self.player.controller)


class AddButton(Button):
    def __init__(self, player: 'MusicPlayer'):
        super().__init__(emoji=Emoji.ADD, style=ButtonStyle.blurple, row=2)
        self.player = player

    async def callback(self, interaction: Interaction):
        await interaction.response.send_modal(SongModal(self.player))


class RightButton(Button):
    def __init__(self, player: 'MusicPlayer'):
        self.player = player
        disabled = player.current_page >= player.total_pages
        super().__init__(emoji=Emoji.RIGHT, row=2, disabled=disabled)

    async def callback(self, interaction: Interaction):
        self.player.current_page += 1
        await interaction.response.edit_message(embed=self.player.embed, view=self.player.controller)


class RefreshButton(Button):
    def __init__(self, player: 'MusicPlayer'):
        self.player = player
        super().__init__(emoji=Emoji.REFRESH, row=2)

    async def callback(self, interaction: Interaction):
        await interaction.response.edit_message(embed=self.player.embed, view=self.player.controller)


class HistoryDropdown(discord.ui.Select):
    def __init__(self, player: 'MusicPlayer'):
        self.player = player

        options = [SelectOption(label=songname) for songname in player.history]

        super().__init__(
            placeholder="Queue up a previously played song",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: Interaction):

        await interaction.response.defer()

        song = Song.from_query(self.values[0])
        await self.player.enqueue(song, person=interaction.user)

        voice_client = interaction.guild.voice_client
        if voice_client is None:
            await interaction.user.voice.channel.connect()
            await self.player.play_next()

        await self.player.update()


class SongModal(Modal):
    def __init__(self, player: 'MusicPlayer'):
        super().__init__(title="Song Search")
        self.player = player
        self.add_item(InputText(
            label="Song Query",
            placeholder="ex. rezonate - rebirth"
        ))

    async def callback(self, interaction: Interaction):

        voice_client = interaction.guild.voice_client
        user_vc = interaction.user.voice.channel

        if not interaction.user.voice:
            self.player.last_action = f"{interaction.user.name} tried to grief"
            return await interaction.response.send_message(Tenor.KERMIT_LOST)

        if voice_client != None and user_vc != voice_client.channel:
            self.player.last_action = f"{interaction.user.name} tried to steal the bot"
            return await self.player.update()

        await interaction.response.defer()

        query = self.children[0].value

        song = Song.from_query(query)
        await self.player.enqueue(song, person=interaction.user)

        voice_client = interaction.guild.voice_client

        if voice_client is None:
            await interaction.user.voice.channel.connect()
            await self.player.play_next()

        await self.player.update()
        await interaction.delete_original_message()
