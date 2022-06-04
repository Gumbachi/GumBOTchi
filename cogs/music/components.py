"""Module holds classes for the buttons of the music player."""
from enum import Enum

import discord
from discord.enums import ButtonStyle
from discord.ui import Button, InputText, Modal

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


class PlayButton(Button):
    def __init__(self, player: 'MusicPlayer'):
        super().__init__(emoji=Emoji.PLAY, style=ButtonStyle.green)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        self.player.resume(person=interaction.user)
        await interaction.response.edit_message(embed=self.player.embed, view=self.player.controller)


class PauseButton(Button):
    def __init__(self, player: 'MusicPlayer'):
        super().__init__(emoji=Emoji.PAUSE, style=ButtonStyle.red)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        self.player.pause(person=interaction.user)
        await interaction.response.edit_message(embed=self.player.embed, view=self.player.controller)


class SkipButton(Button):
    def __init__(self, player: 'MusicPlayer'):
        super().__init__(emoji=Emoji.SKIP, style=ButtonStyle.gray)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        await self.player.skip(person=interaction.user)
        await interaction.response.edit_message(embed=self.player.embed, view=self.player.controller)


class RewindButton(Button):
    def __init__(self, player: 'MusicPlayer'):
        super().__init__(emoji=Emoji.REWIND, style=ButtonStyle.gray)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        await self.player.rewind(person=interaction.user)
        await interaction.response.edit_message(embed=self.player.embed, view=self.player.controller)


class RepeatOffButton(Button):
    def __init__(self, player: 'MusicPlayer'):
        super().__init__(emoji=Emoji.REPEAT, style=ButtonStyle.gray)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        self.player.repeat_type = RepeatType.REPEAT
        await interaction.response.edit_message(view=self.player.controller)


class RepeatButton(Button):
    def __init__(self, player: 'MusicPlayer'):
        super().__init__(emoji=Emoji.REPEAT, style=ButtonStyle.green)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        self.player.repeat_type = RepeatType.REPEATONE
        await interaction.response.edit_message(view=self.player.controller)


class RepeatOneButton(Button):
    def __init__(self, player: 'MusicPlayer'):
        super().__init__(emoji=Emoji.REPEATONE, style=ButtonStyle.green)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        self.player.repeat_type = RepeatType.REPEATOFF
        await interaction.response.edit_message(view=self.player.controller)


class LeftButton(Button):
    def __init__(self, player: 'MusicPlayer', style: ButtonStyle = ButtonStyle.gray):
        disabled = player.current_page == 1
        super().__init__(emoji=Emoji.LEFT, style=style, row=1, disabled=disabled)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        self.player.current_page -= 1
        await interaction.response.edit_message(embed=self.player.embed, view=self.player.controller)


class AddButton(Button):
    def __init__(self, player: 'MusicPlayer', style: ButtonStyle = ButtonStyle.blurple):
        super().__init__(emoji=Emoji.ADD, style=style, row=1)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SongModal(self.player))


class RightButton(Button):
    def __init__(self, player: 'MusicPlayer', style: ButtonStyle = ButtonStyle.gray):
        disabled = player.current_page >= player.total_pages
        super().__init__(emoji=Emoji.RIGHT, style=style, row=1, disabled=disabled)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        self.player.current_page += 1
        await interaction.response.edit_message(embed=self.player.embed, view=self.player.controller)


class SongModal(Modal):
    def __init__(self, player: 'MusicPlayer'):
        super().__init__(title="Song Search")
        self.player = player
        self.add_item(InputText(
            label="Song Query",
            placeholder="ex. rezonate - rebirth"
        ))

    async def callback(self, interaction: discord.Interaction):

        if not interaction.user.voice:
            self.player.last_action = f"{interaction.user.name} tried to grief"
            return await interaction.response.send_message(Tenor.KERMIT_LOST)

        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            self.player.last_action = f"{interaction.user.name} tried to steal the bot"
            return await self.player.update()

        query = self.children[0].value

        song = Song.from_query(query)
        await self.player.enqueue(song, person=interaction.user)

        voice_client = interaction.guild.voice_client

        await interaction.response.edit_message(embed=self.player.embed)

        if voice_client is None:
            await interaction.user.voice.channel.connect()
            await self.player.play_next()

        await self.player.update()
