from typing import TYPE_CHECKING

import discord
from common.cfg import Tenor
from discord.ui import InputText, Modal

from ..errors import NoVoiceClient, SongError
from ..song import Song

if TYPE_CHECKING:
    from .jukebox import Jukebox


class SongModal(Modal):
    def __init__(self, jukebox: "Jukebox"):
        super().__init__(title="Coin Inserted")
        self.jukebox = jukebox
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
            return await interaction.response.send_message(Tenor.KERMIT_LOST, ephemeral=True)

        user_vc = interaction.user.voice.channel

        query = self.children[0].value

        await interaction.response.defer()

        try:
            _ = self.jukebox.voice_client
        except NoVoiceClient:
            await user_vc.connect()

        song = await Song.from_query(query, loop=self.jukebox.voice_client.loop)

        if self.jukebox.current is None:
            self.jukebox.play(song)
            self.jukebox.description = f"{interaction.user.display_name} got this party started with {song.title}"
        else:
            self.jukebox.enqueue(song)
            self.jukebox.description = f"{interaction.user.display_name} queued {song.title}"

        await interaction.followup.send(f"Added {song.title}", delete_after=1)
        await interaction.message.edit(embed=self.jukebox.embed, view=self.jukebox)

    async def on_error(self, error: Exception, interaction: discord.Interaction) -> None:

        if isinstance(error, SongError):
            return await interaction.followup.send("Failed to queue song", ephemeral=True)

        raise error
