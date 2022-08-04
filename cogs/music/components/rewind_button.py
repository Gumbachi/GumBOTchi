from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from ..player import MusicPlayer


class RewindButton(discord.ui.Button):
    def __init__(self, player: "MusicPlayer"):
        super().__init__(emoji="⏪", row=1)
        self.player = player
        self.disabled = not self.player.current

    async def callback(self, interaction: discord.Interaction):
        self.player.play(self.player.current.copy())
        self.player.footer = f"{interaction.user.name} rewound {self.player.current.title}"
        await interaction.response.edit_message(embed=self.player.embed, view=self.player.controls)
