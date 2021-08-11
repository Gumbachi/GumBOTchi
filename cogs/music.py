import os
import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import CommandError


class MusicCommands(commands.Cog):
    """Cog that handles all audio related commands."""

    def __init__(self, bot):
        self.bot = bot

    async def play_audio_clip(self, ctx, source):
        """Given a source it will connect and play audio clip."""
        voice = ctx.author.voice
        if not voice:
            raise CommandError("You aren't in VC")

        player = await voice.channel.connect()
        player.play(discord.FFmpegPCMAudio(
            executable=os.getenv("FFMPEG_PATH"),
            source=source)
        )
        # Sleep while audio is playing.
        while player.is_playing():
            await asyncio.sleep(1)
        await player.disconnect()

    @commands.command(name="clingclang", aliases=["cc"])
    async def clingclang(self, ctx):
        """Plays 'Cling Clang'."""
        source = "resources/sounds/clingclang.mp3"
        await self.play_audio_clip(ctx, source)

    @commands.command(name="guh")
    async def guh(self, ctx):
        """Plays 'Guh' sound clip"""
        source = "resources/sounds/guh.mp3"
        await self.play_audio_clip(ctx, source)

    @commands.command(name="gottem")
    async def gottem(self, ctx):
        """Plays 'gottem' sound clip"""
        source = "resources/sounds/gottem.mp3"
        await self.play_audio_clip(ctx, source)

    @commands.command(name="dancetillyouredead", aliases=["dtyd"])
    async def dtyd(self, ctx):
        """Plays 'dtyd' sound clip"""
        source = "resources/sounds/dtyd.mp3"
        await self.play_audio_clip(ctx, source)

    @commands.command(name="soundtest")
    async def sound_clip_test(self, ctx):
        """Plays a sound clip"""
        source = "resources/sounds/melonpack.mp3"
        await self.play_audio_clip(ctx, source)

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
