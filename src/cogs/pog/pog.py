import random

import database as db
import discord
from database.errors import PogDatabaseError
from discord import SlashCommandGroup, message_command

from .components.pog_manager import PogManager


class PogCommands(discord.Cog):
    """Handles pog related commands and listeners."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    pog = SlashCommandGroup(
        name="pog",
        description="Edit the way pog functionality behaves",
        default_member_permissions=discord.Permissions(manage_messages=True),
    )

    @pog.command(name="manage")
    async def send_pogmanager(self, ctx: discord.ApplicationContext):
        """Send the pog manager message."""
        manager = PogManager(guild=ctx.guild)
        await ctx.respond(embed=manager.embed, view=manager)

    @message_command(name="Add as Pog Response")
    @discord.default_permissions(manage_messages=True)
    async def context_add_pogresponse(
        self, ctx: discord.ApplicationContext, message: discord.Message
    ):
        """Add Pog Respond through message context menu command."""
        db.add_pogresponse(id=ctx.guild.id, response=message.content)
        await ctx.respond(
            embed=discord.Embed(title="Response Added", color=discord.Color.green())
        )

    @message_command(name="Add as Pog Activator")
    @discord.default_permissions(manage_messages=True)
    async def context_add_pogactivator(
        self, ctx: discord.ApplicationContext, message: discord.Message
    ):
        """Add Pog Activator through message context menu command."""
        db.add_pogactivator(id=ctx.guild.id, activator=message.content)
        await ctx.respond(
            embed=discord.Embed(
                title="Activation Phrase Added", color=discord.Color.green()
            )
        )

    @discord.Cog.listener("on_application_command_error")
    async def on_application_command_error(
        self, ctx: discord.ApplicationContext, error: Exception
    ):
        """Global error handler because pog errors come from many places."""

        if isinstance(error, discord.ApplicationCommandInvokeError):
            error = error.original

        if isinstance(error, PogDatabaseError):
            return await ctx.interaction.response.send_message(
                embed=error.embed, ephemeral=True
            )

        raise error

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listen to messages."""
        # ignore the bot user
        if message.author.id == self.bot.user.id or isinstance(
            message.channel, discord.DMChannel
        ):
            return

        # pog listener
        if message.content.lower() in db.get_pogactivators(id=message.guild.id):
            # get pog responses and check if there are any
            responses = db.get_pogresponses(id=message.guild.id)
            if responses:
                await message.channel.send(random.choice(responses))


def setup(bot: discord.Bot):
    """Entry point for loading cogs."""
    bot.add_cog(PogCommands(bot))
