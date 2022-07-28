from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from ..player import MusicPlayer


class LeftButton(discord.ui.Button):
    def __init__(self, player: "MusicPlayer"):
        super().__init__(emoji="\u25C0", row=2)
        self.player = player
        self.disabled = player.page <= 1

    async def callback(self, interaction: discord.Interaction):
        self.player.page -= 1
        await interaction.response.edit_message(embed=self.player.embed, view=self.player.controls)


class RightButton(discord.ui.Button):
    def __init__(self, player: "MusicPlayer"):
        super().__init__(emoji="\u25B6", row=2)
        self.player = player
        self.disabled = player.page >= player.total_pages

    async def callback(self, interaction: discord.Interaction):
        self.player.page += 1
        await interaction.response.edit_message(embed=self.player.embed, view=self.player.controls)
