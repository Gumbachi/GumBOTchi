import os
import asyncio
import youtube_dl
import discord
from discord.ext import commands
from discord.ext.commands import CommandError
from pprint import pprint


class MusicCommands(commands.Cog):
    """Cog that handles all audio related commands."""

    def __init__(self, bot):
        self.bot = bot
        self.soundclip_aliases = {
            "cc": "clingclang",
            "dtyd": "dancetillyouredead"
        }

    @commands.command(name="soundclip", aliases=["sc", "clip"])
    async def play_soundclip(self, ctx, *, name):
        """Plays a sound clip given a name"""
        # turn input into a sound clip path
        name = name.lower()
        name = self.soundclip_aliases.get(name, name)
        name += ".mp3"
        if name not in os.listdir("resources/sounds"):
            raise CommandError("Invalid clip name")

        source = f"resources/sounds/{name}"

        # Get voice state
        voice = ctx.author.voice
        if not voice:
            raise CommandError("You aren't in VC")

        player = await voice.channel.connect()
        audio_clip = discord.FFmpegPCMAudio(
            executable=os.getenv("FFMPEG_PATH"),
            source=source
        )
        player.play(audio_clip)

        # Wait for clip to finish and dc
        while player.is_playing():
            await asyncio.sleep(1)
        await player.disconnect()

    @commands.command(name="play")
    async def play_audiostream(self, ctx, *, query):
        """Plays and audiostream from a youtube video."""

        ydl_opts = {
            "format": "bestaudio",
            "noplaylist": True
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            song_info = ydl.extract_info(f"ytsearch:{query}", download=False)
            print(song_info["entries"][0].keys())

            # Get voice state
            voice = ctx.author.voice
            if not voice:
                raise CommandError("You aren't in VC")

            player = await voice.channel.connect()
            audio_stream = discord.FFmpegPCMAudio(
                song_info["entries"][0]["url"],
                executable=os.getenv("FFMPEG_PATH")
            )
            player.play(audio_stream)

            # Wait for clip to finish and dc
            while player.is_playing():
                await asyncio.sleep(1)
            await player.disconnect()

    @commands.command(name="disconnect", aliases=["dc"])
    async def disconnect_voice(self, ctx):
        """Disconnects if active voice channel"""
        if not (voice := ctx.author.voice):
            raise CommandError("You gotta be in a VC for that")

        clients = self.bot.voice_clients
        for client in clients:
            if voice.channel == client.channel:
                return await client.disconnect()

        raise CommandError("Bot is not in a VC")


def setup(bot):
    bot.add_cog(MusicCommands(bot))
