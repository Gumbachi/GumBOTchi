from typing import TYPE_CHECKING

import discord
from common.cfg import Tenor

from ..errors import NoVoiceClient
from ..song import Song

if TYPE_CHECKING:
    from ..player import MusicPlayer


class HistoryDropdown(discord.ui.Select):
    def __init__(self, player: "MusicPlayer"):
        self.player = player

        options = [discord.SelectOption(label=songname) for songname in player.history]

        super().__init__(
            custom_id="HISTORY",
            placeholder="Queue up a previously played song",
            min_values=1,
            max_values=1,
            options=options,
        )

    def update(self):
        """Adds unadded songs to the history in place"""
        self.options = [discord.SelectOption(label=songname) for songname in self.player.history]

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.defer()

        user_vc = interaction.user.voice.channel

        try:
            _ = self.player.voice_client
        except NoVoiceClient:
            await user_vc.connect()

        try:
            song = await Song.from_query(self.values[0], loop=self.player.voice_client.loop)
        except ValueError:
            self.player.description = f"{interaction.user.name} tried to queue a song and failed"
            return await interaction.edit_original_message(embed=self.player.embed, view=self.player.controls)

        if self.player.current is None:
            self.player.current = song
            self.player.description = f"{interaction.user.name} got this party started with {song.title}"
        else:
            self.player.enqueue(song, interaction.user)

        await interaction.edit_original_message(embed=self.player.embed, view=self.player.controls)
