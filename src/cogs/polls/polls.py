import discord
from discord import option

from .components import FreePollForm, StandardPollForm


class Polls(discord.Cog):
    """Holds poll commands and listeners."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="poll")
    @option(name="type", description="What type of poll is this?", choices=["Standard", "Write-In"])
    @option(name="timeout", description="Close the poll if nobody answers in this amount of time (in minutes)")
    @option(name="votes", description="How many answers can each person choose? (Only applies to standard poll)", choices=[1, 2, 3, 4], default=1)
    @option(name="live", description="Show vote counts while poll is open (Only applies to standard poll)", default=False)
    async def create_poll(
        self, ctx: discord.ApplicationContext,
        type: str,
        timeout: int,
        votes: int,
        live: bool
    ):
        """Create a poll with your preferred settings. Provides a form for questions and answers."""

        if type == "Write-In":
            poll_form = FreePollForm(timeout * 60)
        else:
            poll_form = StandardPollForm(timeout * 60, votes, live)

        await ctx.send_modal(poll_form)


def setup(bot: discord.Bot):
    bot.add_cog(Polls(bot))
