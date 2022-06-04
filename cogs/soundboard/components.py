import os
import asyncio

import discord
from discord import Interaction
from discord.ui import View, Button


class SoundboardMenu(View):

    def __init__(self):
        super().__init__()

    @staticmethod
    async def play_soundclip(interaction: Interaction, path: str):
        """Plays a sound clip"""
        if not interaction.guild.voice_client:
            voice_client = await interaction.user.voice.channel.connect()

        # Play audio
        soundclip = discord.FFmpegPCMAudio(
            executable=os.getenv("FFMPEG_PATH"),
            source=path
        )
        voice_client.play(soundclip)

        # Wait for clip to finish and dc
        while voice_client.is_playing():
            await asyncio.sleep(1)
        await voice_client.disconnect()

    @discord.ui.button(label="CC")
    async def clingclang(self, button: Button, interaction: Interaction):
        """Plays the CLINGCLANG sound clip."""
        await self.play_soundclip(interaction, "./cogs/soundboard/sounds/clingclang.mp3")
        await interaction.response.edit_message(content="clingclang")

    @discord.ui.button(label="BRUH")
    async def bruh(self, button: Button, interaction: Interaction):
        """Plays the BRUH sound clip."""
        await self.play_soundclip(interaction, "./cogs/soundboard/sounds/bruh.mp3")
        await interaction.response.edit_message("bruh")

    @discord.ui.button(label="GUH")
    async def guh(self, button: Button, interaction: Interaction):
        """Plays the GUH sound clip."""
        await self.play_soundclip(interaction, "./cogs/soundboard/sounds/guh.mp3")
        await interaction.response.edit_message("guh")
