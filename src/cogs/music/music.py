import shutil

import discord
from discord import option, slash_command

from .components.jukebox import Jukebox

class Music(discord.Cog):
    """Handles simple commands and listeners."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.players: dict[int, discord.Message] = {}

    @slash_command(name="jukebox")
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
        except discord.NotFound:
            pass  # ignore failed deletion

        await ctx.send(embed=jukebox.embed, view=jukebox)
        await interaction.edit_original_response(content="Vibe Established 🎧")


def setup(bot: discord.Bot):
    """Entry point for loading cogs. Required for all cogs"""

    if shutil.which("ffmpeg") is None:
        raise FileNotFoundError("FFMPEG is not available. Make sure it's added to path")

    bot.add_cog(Music(bot))
