from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from ..player import MusicPlayer


class PlayPauseButton(discord.ui.Button):
    """Handles pause and play interaction with the jukebox."""

    def __init__(self, player: "MusicPlayer"):
        self.player = player

        # voice client does not exist yet
        if not player.guild.voice_client or player.voice_client.is_paused():
            super().__init__(emoji="▶️", style=discord.ButtonStyle.green, row=1, disabled=True)
        else:
            super().__init__(emoji="⏸", style=discord.ButtonStyle.red, row=1)

        if isinstance((vcc := player.guild.voice_client), discord.VoiceClient):
            self.disabled = not (vcc.is_paused() or vcc.is_playing())
        else:
            self.disabled = True

    async def callback(self, interaction: discord.Interaction):
        if self.player.voice_client.is_paused():
            self.player.voice_client.resume()
            if self.player.current:
                self.player.footer = f"{interaction.user.name} resumed {self.player.current.title}"
        else:
            self.player.voice_client.pause()
            if self.player.current:
                self.player.footer = f"{interaction.user.name} paused {self.player.current.title}"

        await interaction.response.edit_message(embed=self.player.embed, view=self.player.controls)
