import discord
from discord import Option, OptionChoice

from .components.poll_form import PollCreationForm


class Polls(discord.Cog):
    """Holds poll commands and listeners."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="poll")
    async def create_poll(
        self, ctx: discord.ApplicationContext,
        timeout: Option(int, "Close the poll if nobody answers in this amount of time (in minutes)"),
        votes: Option(
            int, "How many answers can each person choose? (defaults to 1)",
            default=1, choices=[OptionChoice(x) for x in range(1, 5)]
        ),
        live: Option(
            bool, "Show votes while poll is open (defaults to False)", default=False)
    ):
        """Create a poll with your preferred settings. Provides a form for questions and answers."""
        poll_form = PollCreationForm(timeout * 60, votes, live)
        await ctx.send_modal(poll_form)


def setup(bot: discord.Bot):
    bot.add_cog(Polls(bot))
