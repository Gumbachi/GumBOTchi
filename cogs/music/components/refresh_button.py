from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from ..player import MusicPlayer


class RefreshButton(discord.ui.Button):
    def __init__(self, player: "MusicPlayer"):
        self.player = player
        super().__init__(emoji="🔃", row=2)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            embed=self.player.embed,
            view=self.player.controls
        )
