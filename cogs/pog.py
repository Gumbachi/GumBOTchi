import random
import discord
from discord.commands import slash_command
from discord.ext.commands import MissingPermissions

from common.cfg import poggers_activation_phrases


class PogCommands(discord.Cog):
    """Handles pog related commands and listeners."""

    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="pogify")
    async def pogify(self, ctx, pogresponse: str):
        """Add a pog response"""
        # Admin check
        if not ctx.author.guild_permissions.manage_messages:
            raise MissingPermissions()

        # add pog response to database. document added if not exists
        response = await db.guilds.update_one(
            {"_id": ctx.guild.id},
            {"$push": {"pogresponses": pogresponse}},
            upsert=True
        )

        # Check for success
        if response.modified_count == 1:
            await ctx.respond(f"Added `{pogresponse}` to pog responses")
        else:
            await ctx.respond("Something went wrong on my end")

    @slash_command(name="unpogify")
    async def unpogify(self, ctx, pogresponse: str):
        """Delete a pog response"""
        # Admin check
        if not ctx.author.guild_permissions.manage_messages:
            raise MissingPermissions()

        # attempts to delete a pog response
        response = await db.guilds.update_one(
            {"_id": ctx.guild.id},
            {"$pull": {"pogresponses": pogresponse}}
        )

        # Check for success
        if response.modified_count == 1:
            await ctx.respond(f"Deleted `{pogresponse}` from pog responses`")
        else:
            await ctx.respond("Could not find pog response.")

    @slash_command(name="poglist")
    async def poglist(self, ctx):
        """Displays a list of pog responses"""

        response = await db.guilds.find_one(
            {"_id": ctx.guild.id},
            {"_id": 0, "pogresponses": 1}
        )

        pog_responses = response.get("pogresponses", [])

        embed = discord.Embed(
            title="Pog Responses",
            description='\n'.join(pog_responses[:20])
        )

        # check for pog responses
        if not pog_responses:
            embed.description = "This is not pog at all. Consider `/pogify`ing"

        # pog responses are cut off to avoid discord limit
        if len(pog_responses) > 20:
            embed.set_footer("Some pog responses are not shown")

        await ctx.respond(embed=embed)

    @discord.Cog.listener()
    async def on_message(self, message):
        """Listen to messages."""
        # ignore the bot user
        if message.author.id == self.bot.user.id:
            return

        # f listener
        if message.content.lower() in poggers_activation_phrases:

            # get pog responses and check if there are any
            pog_responses = await fetch_pog_responses(message.guild.id)
            if not pog_responses:
                return

            await message.channel.send(random.choice(pog_responses))


def setup(bot):
    """Entry point for loading cogs."""
    raise Exception("NOT YET IMPLEMENTED")
    bot.add_cog(PogCommands(bot))


async def fetch_pog_responses(id):
    """Fetches pog responses from mongodb."""
    response = await db.guilds.find_one(
        {"_id": id},
        {"_id": 0, "pogresponses": 1}
    )
    return response.get("pogresponses", [])
