"""Module holds classes for the buttons of the music player."""

from enum import Enum

import discord
from discord.enums import ButtonStyle
from discord.ui import Button


class RepeatType(Enum):
    REPEATOFF = 1
    REPEAT = 2
    REPEATONE = 3


class Emoji:
    PLAY = "▶️"
    PAUSE = "⏸"
    SKIP = "⏩"
    REPEAT = "🔁"
    REPEATONE = "🔂"
    QUEUE = "📜"


class PlayButton(Button):
    def __init__(self, player):
        super().__init__(emoji=Emoji.PLAY, style=ButtonStyle.green)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        self.player.resume()
        await interaction.response.edit_message(view=self.player.controller)


class PauseButton(Button):
    def __init__(self, player):
        super().__init__(emoji=Emoji.PAUSE, style=ButtonStyle.red)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        self.player.pause()
        await interaction.response.edit_message(view=self.player.controller)


class SkipButton(Button):
    def __init__(self, player):
        super().__init__(emoji=Emoji.SKIP, style=ButtonStyle.gray)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        await self.player.skip()
        await interaction.response.edit_message(embed=self.player.embed)


class RepeatOffButton(Button):
    def __init__(self, player):
        super().__init__(emoji=Emoji.REPEAT, style=ButtonStyle.gray)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        self.player.repeat_type = RepeatType.REPEAT
        await interaction.response.edit_message(view=self.player.controller)


class RepeatButton(Button):
    def __init__(self, player):
        super().__init__(emoji=Emoji.REPEAT, style=ButtonStyle.green)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        self.player.repeat_type = RepeatType.REPEATONE
        await interaction.response.edit_message(view=self.player.controller)


class RepeatOneButton(Button):
    def __init__(self, player):
        super().__init__(emoji=Emoji.REPEATONE, style=ButtonStyle.green)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        self.player.repeat_type = RepeatType.REPEATOFF
        await interaction.response.edit_message(view=self.player.controller)


class QueueButton(Button):
    def __init__(self, player, style: ButtonStyle = ButtonStyle.gray):
        super().__init__(emoji=Emoji.QUEUE, style=style)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        self.player.queue_displayed = not self.player.queue_displayed
        await self.player.update()
