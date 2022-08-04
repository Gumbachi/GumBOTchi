from typing import TYPE_CHECKING

import discord
from common.cfg import Tenor
from discord.ui import InputText, Modal

from ..errors import NoVoiceClient
from ..song import Song

if TYPE_CHECKING:
    from ..player import MusicPlayer


class SongModal(Modal):
    def __init__(self, player: "MusicPlayer"):
        super().__init__(title="Song Search")
        self.player = player
        self.add_item(
            InputText(
                label="Song Query",
                placeholder='ex. "rezonate - rebirth" or a url to the youtube video',
                min_length=1,
                max_length=200,
            )
        )

    async def callback(self, interaction: discord.Interaction):

        # no user voice state
        if interaction.user.voice == None:
            return await interaction.response.send_message(Tenor.KERMIT_LOST)

        user_vc = interaction.user.voice.channel

        query = self.children[0].value

        await interaction.response.defer()

        try:
            _ = self.player.voice_client
        except NoVoiceClient:
            await user_vc.connect()

        try:
            song = await Song.from_query(query, loop=self.player.voice_client.loop)
        except ValueError:
            return await interaction.followup.send(f"Failed to queue song", ephemeral=True)

        if self.player.current is None:
            self.player.current = song
            self.player.description = f"{interaction.user.name} got this party started with {song.title}"
        else:
            self.player.enqueue(song, interaction.user)

        await interaction.followup.send(f"Added {song.title}", delete_after=1)
        await interaction.message.edit(embed=self.player.embed, view=self.player.controls)
