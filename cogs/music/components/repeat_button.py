
from typing import TYPE_CHECKING

import discord

from ..enums import RepeatType

if TYPE_CHECKING:
    from ..player import MusicPlayer


class RepeatButton(discord.ui.Button):
    def __init__(self, player: "MusicPlayer"):

        self.player = player

        match player.repeat:
            case RepeatType.REPEATOFF:
                super().__init__(emoji="🔁", style=discord.ButtonStyle.gray, row=1)
            case RepeatType.REPEAT:
                super().__init__(emoji="🔁", style=discord.ButtonStyle.green, row=1)
            case RepeatType.REPEATONE:
                super().__init__(emoji="🔂", style=discord.ButtonStyle.green, row=1)

    async def callback(self, interaction: discord.Interaction):
        """Cycle the repeat type."""

        match self.player.repeat:
            case RepeatType.REPEATOFF:
                self.player.repeat = RepeatType.REPEAT
            case RepeatType.REPEAT:
                self.player.repeat = RepeatType.REPEATONE
            case RepeatType.REPEATONE:
                self.player.repeat = RepeatType.REPEATOFF

        await interaction.response.edit_message(view=self.player.controls)
