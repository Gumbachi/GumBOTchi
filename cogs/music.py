import os
from datetime import timedelta
import asyncio
import youtube_dl
import discord
from discord.ext import commands
from discord.ext.commands import CommandError
import common.cfg as cfg
from common.cfg import song_queue


class MusicCommands(commands.Cog):
    """Cog that handles all audio related commands."""

    CLIENT_TIMEOUT = 60

    def __init__(self, bot):
        self.bot = bot
        self.soundclip_aliases = {
            "cc": "clingclang",
            "dtyd": "dancetillyouredead"
        }

    def get_voice_client(self, gid):
        for client in self.bot.voice_clients:
            if gid == client.guild.id:
                cfg.client_timeout = 0  # reset timeout counter
                return client

    async def play_next_song(self, player):
        """Plays the next song up in the Queue"""
        # song is skipped
        if player.is_playing():
            player.stop()

        # break and dc if no more songs queued
        if not song_queue:
            return

        # pop and play next song
        song = song_queue.pop()
        audio_stream = discord.FFmpegPCMAudio(
            song["url"],
            executable=os.getenv("FFMPEG_PATH")
        )
        player.play(audio_stream)

        # Send now playing embed
        play_embed = discord.Embed(
            title=f"{song['title']}",
            description=str(timedelta(seconds=int(song["duration"]))),
            color=discord.Color.green()
        )
        play_embed.set_thumbnail(url=song["thumbnail"])
        await song["textchannel"].send(embed=play_embed)

        # disconnect when bot is out of songs to play
        while player.is_playing():
            await asyncio.sleep(1)
            cfg.client_timeout = 0

        if song_queue:
            await self.play_next_song(player)

    @commands.command(name="connect", aliases=["join"])
    async def connect_to_voice(self, ctx):
        """Disconnects if active voice channel"""
        client = self.get_voice_client(ctx.guild.id)
        if client:
            raise CommandError("Bot is already connected somewhere")
        player = await ctx.author.voice.channel.connect()

        while cfg.client_timeout <= self.CLIENT_TIMEOUT:
            await asyncio.sleep(1)
            if not player.is_playing():
                if song_queue:
                    await self.play_next_song(player)
                else:
                    print("counting")
                    cfg.client_timeout += 1

        await player.disconnect()

    @commands.command(name="disconnect", aliases=["dc"])
    async def disconnect_from_voice(self, ctx):
        """Disconnects if active voice channel"""
        client = self.get_voice_client(ctx.guild.id)
        if not client:
            raise CommandError("Bot is not in your VC")
        await client.disconnect()
        song_queue.clear()

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

        # Play audio
        player = await ctx.invoke(self.bot.get_command("connect"))
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
    async def enqueue_song(self, ctx, *, query):
        """Plays and audiostream from a youtube video."""

        if len(song_queue) >= 10:
            raise CommandError("Max 10 Queued songs")

        # Find youtube video data with ytdl
        ydl_opts = {"format": "bestaudio", "noplaylist": True, "quiet": True}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            song_info = ydl.extract_info(f"ytsearch:{query}", download=False)
            data = song_info["entries"][0]

        # Attempt to acquire voice client
        try:
            player = await ctx.invoke(self.bot.get_command("connect"))
        except CommandError:
            player = self.get_voice_client(ctx.guild.id)
            if not player:
                raise CommandError("Bot is probably in another channel rn")

        # Prepare and add song data to queue
        required_data = ("url", "title", "duration", "thumbnail")
        song = {k: data[k] for k in required_data}
        song["textchannel"] = ctx.channel
        song_queue.append(song)

        # added song to queue
        if player.is_playing():
            embed = discord.Embed(
                title=f"{song['title']} added to queue.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=song["thumbnail"])
            await ctx.send(embed=embed)
        # now playing song
        else:
            await self.play_next_song(player)

    @commands.command(name="skip")
    async def skip_song(self, ctx):
        """Skips to the next song in the queue"""
        player = self.get_voice_client(ctx.guild.id)
        if player.channel != ctx.author.voice.channel:
            raise CommandError("You gotta be in the same channel")

        await self.play_next_song(player)

    @commands.command(name="pause")
    async def pause_song(self, ctx):
        """Pause the song"""
        player = self.get_voice_client(ctx.guild.id)
        if player.channel != ctx.author.voice.channel:
            raise CommandError("You gotta be in the same channel")
        player.pause()

    @commands.command(name="unpause", aliases=["resume"])
    async def resume_song(self, ctx):
        """resumes the paused song"""
        player = self.get_voice_client(ctx.guild.id)
        if player.channel != ctx.author.voice.channel:
            raise CommandError("You gotta be in the same channel")

        player.resume()

    @commands.command(name="queue", aliases=["q"])
    async def show_queue(self, ctx):
        """Shows the queue of songs"""
        if len(song_queue) == 0:
            raise CommandError("Nothing is currently queued")

        q_embed = discord.Embed(
            title="Your Queue",
            description='\n'.join([song["title"] for song in song_queue]),
            color=discord.Color.teal()
        )
        await ctx.send(embed=q_embed)

    @commands.command(name="stop")
    async def stopsong(self, ctx):
        """stop song"""
        player = self.get_voice_client(ctx.guild.id)
        if player.channel != ctx.author.voice.channel:
            raise CommandError("You gotta be in the same channel")
        player.stop()


def setup(bot):
    bot.add_cog(MusicCommands(bot))
