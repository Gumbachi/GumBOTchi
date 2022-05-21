import random
import discord
from discord import SlashCommandGroup
from common.cfg import poggers_activation_phrases
from common.database import db
import common.utils as utils
from discord.ext import pages


class PogCommands(discord.Cog):
    """Handles pog related commands and listeners."""

    def __init__(self, bot):
        self.bot = bot

    pog = SlashCommandGroup("pog", "Edit the way pog functionality behaves")

    @pog.command()
    async def add(self, ctx: discord.ApplicationContext, response: str):
        """Add a pog response"""
        # Admin check
        if not ctx.author.guild_permissions.manage_messages:
            return await ctx.respond("Sure, but where are your permissions")

        success = db.add_pog_response(ctx.guild.id, response)

        # Check for success
        if success:
            await ctx.respond(f"Added `{response}` to pog responses")
        else:
            await ctx.respond("Something went wrong. Try again or something")

    @pog.command()
    async def remove(self, ctx: discord.ApplicationContext, response: str):
        """Delete a pog response"""
        # Admin check
        if not ctx.author.guild_permissions.manage_messages:
            return await ctx.respond("Sure, but where are your permissions")

        # attempts to delete a pog response
        success = db.remove_pog_response(ctx.guild.id, response)

        # Check for success
        if success:
            await ctx.respond(f"Deleted `{response}` from pog responses")
        else:
            await ctx.respond("Could not find pog response.")

    @pog.command()
    async def list(self, ctx: discord.ApplicationContext):
        """Displays a list of pog responses"""

        responses = db.get_pogresponses(ctx.guild.id)

        # check for pog responses
        if not responses:
            return await ctx.respond("This is not pog at all. Consider `pogify`ing")

        embeds = [
            discord.Embed(
                title=f"Pog Responses",
                description='\n'.join(chunk)
            ) for chunk in utils.chunk(responses, chunksize=8)
        ]

        paginator = pages.Paginator(pages=embeds, show_disabled=False)
        await paginator.respond(ctx.interaction, ephemeral=False)

    @discord.Cog.listener()
    async def on_message(self, message):
        """Listen to messages."""
        # ignore the bot user
        if message.author.id == self.bot.user.id:
            return

        # pog listener
        if message.content.lower() in poggers_activation_phrases:

            # get pog responses and check if there are any
            responses = db.get_pogresponses(message.guild.id)
            if responses:
                await message.channel.send(random.choice(responses))


def setup(bot):
    """Entry point for loading cogs."""
    bot.add_cog(PogCommands(bot))
