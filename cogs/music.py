import collections
import os
import asyncio
import youtube_dl
import discord
from discord.ext import commands, tasks
from discord.ext.commands import CommandError
from common.utils import normalize_time

# TODO DC timer, play all cmd, normalize volume maybe


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

    @classmethod
    def get_song_data(cls, query):
        """Handles all youtubedl stuff."""
        with youtube_dl.YoutubeDL(cls.YDL_OPTS) as ydl:
            song_info = ydl.extract_info(f"ytsearch:{query}", download=False)
            try:
                data = song_info["entries"][0]
            except KeyError:
                return None  # Couldnt find song

            required_data = ("url", "title", "duration",
                             "thumbnail", "webpage_url")
            return {k: data[k] for k in required_data}

    @classmethod
    async def play_song(cls, voice_client, song):
        """Plays the next song in the queue.
        If song is not provided then it plays next song
        """
        # ensure voice client is not playing
        if voice_client.is_playing():
            voice_client.stop()

        # update queue object
        queue = SongQueue.get_queue(voice_client.guild.id)
        queue.current_song = song

        # format and play audio
        audio = discord.FFmpegPCMAudio(song["url"], **cls.FFMPEG_OPTS)
        voice_client.play(audio)

        # Send now playing message
        embed = discord.Embed(
            title="NOW PLAYING",
            description=f"[{song['title']}]({song['webpage_url']})\n{normalize_time(song['duration'])}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=song["thumbnail"])
        await song["text_channel"].send(embed=embed)

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
        SongQueue.instances.pop(ctx.guild.id, None)

    @commands.command(name="play")
    async def queue_song(self, ctx, *, query):
        """Plays audio from a YT vid in the voice channel."""

        if not (voice_client := ctx.voice_client):
            voice_client = await ctx.invoke(self.bot.get_command("connect"))

        # attempt to find song data
        if not (song := self.get_song_data(query)):
            raise CommandError("No dice on that one.")
        song["text_channel"] = ctx.channel

        queue = SongQueue.get_queue(ctx.guild.id)

        # added song to queue
        if queue.current_song:
            queue.appendleft(song)
            embed = discord.Embed(
                title=f"Added To Queue",
                description=(f"[{song['title']}]({song['webpage_url']})\n"
                             f"Estimated Wait: {queue.time_until(len(queue)-1)}"),
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=song["thumbnail"])
            await ctx.send(embed=embed)
        # now playing song
        else:
            await self.play_song(voice_client, song)

    @commands.command(name="skip")
    @commands.check(bot_in_vc)
    async def next_song(self, ctx):
        """Skips to the next song in the queue"""
        queue = SongQueue.get_queue(ctx.guild.id)
        if queue.is_empty():
            if queue.cycle:
                await self.play_song(ctx.voice_client, queue.current_song)
            else:
                ctx.voice_client.stop()
        else:
            queue.loop = False  # turn off looping if skipped
            # add song back onto queue if cycle is enabled
            if queue.cycle:
                queue.appendleft(queue.current_song)

            await self.play_song(ctx.voice_client, queue.pop())

    @commands.command(name="pause")
    @commands.check(bot_in_vc)
    async def pause_song(self, ctx):
        """Pause the song"""
        ctx.voice_client.pause()
        SongQueue.get_queue(ctx.guild.id).paused = True

    @commands.command(name="unpause", aliases=["resume"])
    @commands.check(bot_in_vc)
    async def resume_song(self, ctx):
        """resumes the paused song"""
        ctx.voice_client.resume()
        SongQueue.get_queue(ctx.guild.id).paused = False

    @commands.command(name="loop", aliases=["repeat"])
    @commands.check(bot_in_vc)
    async def loop_song(self, ctx):
        """Flips loop status for current song"""
        queue = SongQueue.get_queue(ctx.guild.id)
        queue.loop = not queue.loop

        if queue.loop:
            embed = discord.Embed(title="Looping  🔂")
        else:
            embed = discord.Embed(title="Not Looping  ❌")
        await ctx.send(embed=embed)

    @commands.command(name="cycle")
    @ commands.check(bot_in_vc)
    async def cycle_queue(self, ctx):
        """Flips cycle status for current song"""
        queue = SongQueue.get_queue(ctx.guild.id)
        queue.cycle = not queue.cycle

        if queue.cycle:
            embed = discord.Embed(title="Cycling  🔁")
        else:
            embed = discord.Embed(title="Not Cycling  ❌")
        await ctx.send(embed=embed)

    @ commands.command(name="nowplaying", aliases=["np"])
    async def display_current_song(self, ctx):
        """Shows the current song"""
        song = SongQueue.get_queue(ctx.guild.id).current_song
        if song:
            embed = discord.Embed(
                title="NOW PLAYING",
                description=f"[{song['title']}]({song['webpage_url']})\n{normalize_time(song['duration'])}",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=song["thumbnail"])
        else:
            embed = discord.Embed(title="Nothing is Playing")
        await ctx.send(embed=embed)

    @commands.command(name="queue", aliases=["q"])
    async def show_queue(self, ctx):
        """Shows the queue of songs"""
        queue = SongQueue.get_queue(ctx.guild.id)
        if not queue.current_song:
            raise CommandError("Nothing in queue or playing")

        loop_status = "🔂" if queue.loop else "❌"
        cycle_status = "🔁" if queue.cycle else "❌"
        pause_status = "⏸️" if queue.paused else "▶️"

        embed = discord.Embed(
            title=f"QUEUEUEUEUE\t\t\t{pause_status}\t{loop_status}\t{cycle_status}",
            description=f"**NOW PLAYING**\n[{queue.current_song['title']}]({queue.current_song['webpage_url']})",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=queue.current_song["thumbnail"])

        # Format queue to only 5 songs for space
        songlist = list(queue)
        songlist.reverse()  # needs to be reversed to display properly
        if len(queue) > 5:
            songlist = songlist[:5]  # only 5 songs displayed
            embed.set_footer(text=f"{len(queue)-5} Songs are not displayed")

        # Add each song
        for i, song in enumerate(songlist, 1):
            embed.add_field(
                name=f"{i}. {song['title']}",
                value=f"Estimated Wait: {queue.time_until(i-1)} - [Link]({song['webpage_url']})",
                inline=False
            )
        await ctx.send(embed=embed)

    @tasks.loop(seconds=3.0)
    async def queue_timer(self):
        """Checks the voice clients to see if one has stopped."""
        for client in self.bot.voice_clients:
            if client.is_playing():
                continue
            if (queue := SongQueue.get_queue(client.guild.id)):
                if queue.paused:
                    return
                elif queue.loop:
                    await self.play_song(client, queue.current_song)
                else:
                    # add song back onto queue if cycle is enabled
                    if queue.cycle:
                        queue.appendleft(queue.current_song)

                    await self.play_song(client, queue.pop())


class SoundclipCommands(commands.Cog):
    """A bunch of commands for soundclips."""

    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        """Checks if the bot is currently not connected or paused in the same channel"""
        if ctx.voice_client:
            if ctx.voice_client.is_playing or ctx.voice_client.channel != ctx.author.voice.channel:
                return False

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


class SongQueue(collections.deque):
    """Handles the current song queue."""
    instances = {}

    def __init__(self):
        super().__init__()
        self.loop = False
        self.cycle = False
        self.paused = False
        self.current_song = None

    @classmethod
    def get_queue(cls, gid: int):
        """Return active song queue or make a new one."""
        queue = cls.instances.get(gid)
        if queue is None:
            queue = SongQueue()
            cls.instances[gid] = queue
        return queue

    def is_empty(self):
        """Not necessary but more readable."""
        return len(self) == 0

    def time_until(self, index):
        """Calculate time until a song is played."""
        time_until = self.current_song["duration"]
        for i in range(index):
            time_until += self[i]["duration"]
        return normalize_time(time_until)


def setup(bot):
    bot.add_cog(MusicCommands(bot))
    bot.add_cog(SoundclipCommands(bot))
