import os

import discord
from discord import guild_only, option, slash_command

from .components.jukebox import Jukebox


class Music(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.players: dict[int, discord.Message] = {}

    @slash_command(name="jukebox")
    @guild_only()
    @option(name="fresh", description="Start with a brand new jukebox. Deletes the previous", default=False)
    async def send_jukebox(self, ctx: discord.ApplicationContext, fresh: bool):
        """Get the music player and its buttons."""
        interaction = await ctx.respond("Establishing Vibe...")

        if fresh:
            if (jukebox := Jukebox.instances.pop(ctx.guild.id, None)):
                jukebox.stop()

        try:
            jukebox = Jukebox.instances[ctx.guild.id]
            await jukebox.message.delete()
        except KeyError:
            jukebox = Jukebox(ctx.guild)

        await ctx.send(embed=jukebox.embed, view=jukebox)
        await interaction.edit_original_message(content="Vibe Established 🎧")


def setup(bot: discord.Bot):
    """Entry point for loading cogs. Required for all cogs"""
    ffmpeg_path = os.getenv("FFMPEG_PATH") or ""
    if ffmpeg_path != "ffmpeg" and not os.path.isfile(ffmpeg_path):
        raise FileNotFoundError("Couldn't locate FFMPEG executable")

    bot.add_cog(Music(bot))
