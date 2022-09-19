import random

import database as db
import discord
from common.utils import chunk
from database.errors import PogDatabaseError
from discord import SlashCommandGroup, message_command, option
from discord.ext.pages import Paginator

from .responses import *


class PogCommands(discord.Cog):
    """Handles pog related commands and listeners."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    pog = SlashCommandGroup(
        name="pog",
        description="Edit the way pog functionality behaves",
        guild_only=True,
        default_member_permissions=discord.Permissions(manage_messages=True)
    )

    response = pog.create_subgroup(
        name="response",
        description="pog response commands."
    )

    activator = pog.create_subgroup(
        name="activator",
        description="pog activator commands."
    )

    async def response_autocomplete(self, ctx: discord.AutocompleteContext):
        """Autocomplete pog responses"""
        responses = db.get_pogresponses(id=ctx.interaction.guild.id)

        def ac_predicate(response: str) -> bool:
            response = response.lower()
            value = ctx.value.lower()
            return response.startswith(value) or value in response

        return [response for response in responses if ac_predicate(response)]

    async def activator_autocomplete(self, ctx: discord.AutocompleteContext):
        """Autocomplete pog responses"""
        activators = db.get_pogactivators(id=ctx.interaction.guild.id)

        def ac_predicate(activator: str) -> bool:
            activator = activator.lower()
            value = ctx.value.lower()
            return activator.startswith(value) or value in activator

        return [activator for activator in activators if ac_predicate(activator)]

    @response.command(name="add")
    @option(name="response", description="The automated response to add to the list")
    async def add_pogresponse(self, ctx: discord.ApplicationContext, response: str):
        """Add an automated response to pog activation phrases"""
        db.add_pogresponse(id=ctx.guild.id, response=response)
        await ctx.respond(embed=POGRESPONSE_ADDED)

    @response.command(name="remove")
    @option(name="response", description="The response to remove", autocomplete=response_autocomplete)
    async def remove_pogresponse(self, ctx: discord.ApplicationContext, response: str):
        """Remove a pog response"""
        db.remove_pogresponse(id=ctx.guild.id, response=response)
        await ctx.respond(embed=POGRESPONSE_REMOVED)

    @response.command(name="list")
    async def list_pogresponses(self, ctx: discord.ApplicationContext):
        """Displays a list of pog responses"""

        responses = db.get_pogresponses(id=ctx.guild.id)

        # check for pog responses
        if not responses:
            return await ctx.respond(embed=MISSING_POGRESPONSES)

        embeds = [
            discord.Embed(
                title="Pog Responses",
                description='\n'.join(chunk)
            ) for chunk in chunk(responses, chunksize=8)
        ]

        paginator = Paginator(pages=embeds)
        paginator.remove_button("first")
        paginator.remove_button("last")
        await paginator.respond(ctx.interaction)

    @message_command(name="Add as Pog Response")
    async def context_add_pogresponse(self, ctx: discord.ApplicationContext, message: discord.Message):
        """Add Pog Respond through message context menu command."""
        db.add_pogresponse(id=ctx.guild.id, response=message.content)
        await ctx.respond(embed=POGRESPONSE_ADDED)

    @activator.command(name="add")
    @option(name="phrase", description="The activator phrase")
    async def add_pogactivator(self, ctx: discord.ApplicationContext, phrase: str):
        """Add a pog activation phrase"""
        db.add_pogactivator(id=ctx.guild.id, activator=phrase)
        await ctx.respond(embed=POGACTIVATOR_ADDED)

    @activator.command(name="remove")
    @option(name="phrase", description="The activation phrase to remove", autocomplete=activator_autocomplete)
    async def remove_pogactivator(self, ctx: discord.ApplicationContext, phrase: str):
        """Remove a pog activation phrase"""
        db.remove_pogactivator(id=ctx.guild.id, activator=phrase)
        await ctx.respond(embed=POGACTIVATOR_REMOVED)

    @activator.command(name="list")
    async def list_pogactivators(self, ctx: discord.ApplicationContext):
        """Displays a list of pog activators"""
        activators = db.get_pogactivators(id=ctx.guild.id)

        # check for pog responses
        if not activators:
            return await ctx.respond(embed=MISSING_POGACTIVATORS)

        await ctx.respond(
            embed=discord.Embed(
                title="Pog Activators",
                description=','.join([f"`{a}`" for a in activators])
            )
        )

    @message_command(name="Add as Pog Activator")
    async def context_add_pogactivator(self, ctx: discord.ApplicationContext, message: discord.Message):
        """Add Pog Activator through message context menu command."""
        db.add_pogactivator(id=ctx.guild.id, activator=message.content)
        await ctx.respond(embed=POGACTIVATOR_ADDED)

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: Exception):
        """Cog error handler for Pog related errors."""

        if isinstance(error, discord.ApplicationCommandInvokeError):
            error = error.original

        if isinstance(error, PogDatabaseError):
            return await ctx.respond(embed=error.embed)

        raise error

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listen to messages."""
        # ignore the bot user
        if message.author.id == self.bot.user.id or isinstance(message.channel, discord.DMChannel):
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
