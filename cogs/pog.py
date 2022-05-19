import random
import discord
from discord import slash_command

from common.cfg import poggers_activation_phrases

from common.database import db


class PogCommands(discord.Cog):
    """Handles pog related commands and listeners."""

    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="pogify")
    async def pogify(self, ctx: discord.ApplicationContext, response: str):
        """Add a pog response"""
        # Admin check
        if not ctx.author.guild_permissions.manage_messages:
            return await ctx.respond("Sure, but where are your permissions")

        result = db.add_pog_response(ctx.guild.id, response)

        # Check for success
        if result == True:
            await ctx.respond(f"Added `{response}` to pog responses")
        else:
            await ctx.respond("Something went wrong. Try again or something")

    @slash_command(name="unpogify")
    async def unpogify(self, ctx: discord.ApplicationContext, response: str):
        """Delete a pog response"""
        # Admin check
        if not ctx.author.guild_permissions.manage_messages:
            return await ctx.respond("Sure, but where are your permissions")

        # attempts to delete a pog response
        result = db.remove_pog_response(ctx.guild.id, response)

        # Check for success
        if result == True:
            await ctx.respond(f"Deleted `{response}` from pog responses")
        else:
            await ctx.respond("Could not find pog response.")

    @slash_command(name="poglist")
    async def poglist(self, ctx: discord.ApplicationContext):
        """Displays a list of pog responses"""

        responses = db.get_pogresponses(ctx.guild.id)

        # check for pog responses
        if not responses:
            return await ctx.respond("This is not pog at all. Consider `pogify`ing")

        embed = discord.Embed(
            title="Pog Responses",
            description='\n'.join(responses[:20])
        )

        # pog responses are cut off to avoid discord limit
        if len(responses) > 20:
            embed.set_footer(text="only showing the first 20")

        await ctx.respond(embed=embed)

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
