import asyncio
import os

import discord
from discord import Interaction, VoiceClient
from discord.ui import Button, View


class SoundboardMenu(View):

    def __init__(self):
        super().__init__()

    async def play_soundclip(self, interaction: Interaction, path: str):
        """Plays a sound clip"""

        if interaction.guild.voice_client:
            voice_client = interaction.guild.voice_client
            disconnect = False
        else:
            voice_client = await interaction.user.voice.channel.connect()
            disconnect = True

        # Play audio
        soundclip = discord.FFmpegPCMAudio(
            executable=os.getenv("FFMPEG_PATH"),
            source=path
        )

        if voice_client.is_playing() or voice_client.is_paused():
            current_source = voice_client.source
            current_after = voice_client._player.after

            def resume_playing(error):
                voice_client.play(current_source, after=current_after)

            voice_client.source = soundclip
            voice_client._player.after = resume_playing

        else:
            voice_client.play(soundclip)

        # Wait for clip to finish and dc
        if current_source != None:
            while voice_client.source != None:
                await asyncio.sleep(1)

        if disconnect:
            await voice_client.disconnect()

    @discord.ui.button(label="CC")
    async def clingclang(self, button: Button, interaction: Interaction):
        """Plays the CLINGCLANG sound clip."""
        await interaction.response.edit_message(content="clingclang")
        await self.play_soundclip(interaction, "./cogs/soundboard/sounds/clingclang.mp3")

    @discord.ui.button(label="BRUH")
    async def bruh(self, button: Button, interaction: Interaction):
        """Plays the BRUH sound clip."""
        await interaction.response.edit_message(content="bruh")
        await self.play_soundclip(interaction, "./cogs/soundboard/sounds/bruh.mp3")

    @discord.ui.button(label="GUH")
    async def guh(self, button: Button, interaction: Interaction):
        """Plays the GUH sound clip."""
        await interaction.response.edit_message(content="guh")
        await self.play_soundclip(interaction, "./cogs/soundboard/sounds/guh.mp3")
