import discord
from discord import option

from .components import PollCreationForm


class Polls(discord.Cog):
    """Holds poll commands and listeners."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="poll")
    @option(name="timeout", description="Close the poll if nobody answers in this amount of time (in minutes)")
    @option(name="votes", description="How many answers can each person choose? (default: 1)", default=1, choices=[1, 2, 3, 4])
    @option(name="live", description="Show vote counts while poll is open (default: True)", default=True)
    async def create_poll(
        self, ctx: discord.ApplicationContext,
        timeout: int,
        votes: int,
        live: bool
    ):
        """Create a poll with your preferred settings. Provides a form for questions and answers."""
        poll_form = PollCreationForm(timeout * 60, votes, live)
        await ctx.send_modal(poll_form)


def setup(bot: discord.Bot):
    bot.add_cog(Polls(bot))
