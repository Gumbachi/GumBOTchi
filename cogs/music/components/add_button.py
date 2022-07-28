from typing import TYPE_CHECKING

import discord

from .song_modal import SongModal

if TYPE_CHECKING:
    from ..player import MusicPlayer


class AddButton(discord.ui.Button):
    def __init__(self, player: "MusicPlayer"):
        super().__init__(custom_id="ADD", emoji="➕", style=discord.ButtonStyle.blurple, row=2)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SongModal(self.player))
