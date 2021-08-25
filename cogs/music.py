import os
import asyncio
import youtube_dl
import discord
from discord.ext import commands, tasks
from discord.ext.commands import CommandError
from common.cfg import song_queue
from common.utils import normalize_time

# TODO Loooops, DC timer, better lookign queue, play all cmd, normalize volume maybe


def bot_in_vc(ctx):
    """A Check to see if bot is in the cmd author VC."""
    if ctx.voice_client:
        return ctx.voice_client.channel == ctx.author.voice.channel


class MusicCommands(commands.Cog):
    """Cog that handles all audio related commands."""
    YDL_OPTS = {
        "format": "bestaudio/best",
        "extractaudio": True,
        "audioformat": "mp3",
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0",
    }
    FFMPEG_OPTS = {
        "executable": os.getenv("FFMPEG_PATH"),
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    def __init__(self, bot):
        self.bot = bot
        self.queue_timer.start()

    def cog_check(self, ctx):
        return ctx.guild.id in (565257922356051973, 169562731085692928)

    @classmethod
    def get_song_data(cls, query):
        """Handles all youtubedl stuff."""
        with youtube_dl.YoutubeDL(cls.YDL_OPTS) as ydl:
            song_info = ydl.extract_info(f"ytsearch:{query}", download=False)
            try:
                data = song_info["entries"][0]
            except KeyError:
                return None  # Couldnt find song

            required_data = ("url", "title", "duration", "thumbnail")
            return {k: data[k] for k in required_data}

    @classmethod
    async def play_next_song(cls, voice_client):
        """Plays the next song in the queue."""
        if voice_client.is_playing():
            voice_client.stop()

        # do nothing if no more songs queued
        if not song_queue:
            return

        # pop and play next song
        song = song_queue.pop()
        audio = discord.FFmpegPCMAudio(song["url"], **cls.FFMPEG_OPTS)
        voice_client.play(audio)

        # Send now playing embed
        play_embed = discord.Embed(
            title="NOW PLAYING",
            description=f"{song['title']}\n{normalize_time(song['duration'])}",
            color=discord.Color.green()
        )
        play_embed.set_thumbnail(url=song["thumbnail"])
        await song["text_channel"].send(embed=play_embed)

    @commands.command(name="connect", aliases=["join"])
    async def connect_to_voice(self, ctx):
        """Connects bot to voice channel and returns the client."""
        # user is not in VC
        if not ctx.author.voice:
            return await ctx.send("https://tenor.com/view/kermit-the-frog-looking-for-directions-navigate-is-lost-gif-11835765")
        return await ctx.author.voice.channel.connect()

    @commands.command(name="disconnect", aliases=["dc"])
    @commands.check(bot_in_vc)
    async def disconnect_from_voice(self, ctx):
        """Disconnects if active voice channel"""
        await ctx.voice_client.disconnect()
        song_queue.clear()

    @commands.command(name="play")
    async def queue_song(self, ctx, *, query):
        """Plays audio from a YT vid in the voice channel."""
        voice_client = ctx.voice_client
        if not voice_client:
            voice_client = await ctx.invoke(self.bot.get_command("connect"))

        # attempt to find song data
        song = self.get_song_data(query)
        if not song:
            raise CommandError("No dice on that one.")
        song["text_channel"] = ctx.channel
        song_queue.append(song)

        # added song to queue
        if voice_client.is_playing() and len(song_queue) >= 1:
            embed = discord.Embed(
                title=f"Song added to queue.",
                description=f"{song['title']} added to queue behind {len(song_queue)-1} other songs.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=song["thumbnail"])
            await ctx.send(embed=embed)
        # now playing song
        else:
            await self.play_next_song(voice_client)

    @commands.command(name="skip")
    @commands.check(bot_in_vc)
    async def next_song(self, ctx):
        """Skips to the next song in the queue"""
        await self.play_next_song(ctx.voice_client)

    @commands.command(name="pause")
    @commands.check(bot_in_vc)
    async def pause_song(self, ctx):
        """Pause the song"""
        ctx.voice_client.pause()

    @commands.command(name="unpause", aliases=["resume"])
    @commands.check(bot_in_vc)
    async def resume_song(self, ctx):
        """resumes the paused song"""
        ctx.voice_client.resume()

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

    @tasks.loop(seconds=3.0)
    async def queue_timer(self):
        """Checks the voice clients to see if one has stopped."""
        for client in self.bot.voice_clients:
            if client.is_playing():
                continue
            if song_queue:
                await self.play_next_song(client)


class SoundclipCommands(commands.Cog):
    """A bunch of commands for soundclips."""

    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        """Checks if the bot is currently not connected or paused in the same channel"""
        if ctx.voice_client:
            if ctx.voice_client.is_playing or ctx.voice_client.channel != ctx.author.voice.channel:
                return False
        return True

    @staticmethod
    async def play_soundclip(ctx, source):
        """Plays a sound clip given a name."""
        voice_client = ctx.voice_client
        if not voice_client:
            voice_client = await ctx.author.voice.channel.connect()

        # Play audio
        soundclip = discord.FFmpegPCMAudio(
            executable=os.getenv("FFMPEG_PATH"),
            source=source
        )
        voice_client.play(soundclip)

        # Wait for clip to finish and dc
        while voice_client.is_playing():
            await asyncio.sleep(1)
        await voice_client.disconnect()

    @commands.command(name="bruh")
    async def sc_bruh(self, ctx):
        """Play bruh sound effect #2."""
        await self.play_soundclip(ctx, "resources/sounds/bruh.mp3")

    @commands.command(name="clingclang", aliases=["cc", "clanger"])
    async def sc_clingclang(self, ctx):
        """Play Cling Clang."""
        await self.play_soundclip(ctx, "resources/sounds/clingclang.mp3")

    @commands.command(name="gottem")
    async def sc_gottem(self, ctx):
        """Play we gottem soundclip."""
        await self.play_soundclip(ctx, "resources/sounds/gottem.mp3")

    @commands.command(name="guh")
    async def sc_guh(self, ctx):
        """Play guh soundclip."""
        await self.play_soundclip(ctx, "resources/sounds/guh.mp3")


def setup(bot):
    bot.add_cog(MusicCommands(bot))
    bot.add_cog(SoundclipCommands(bot))
