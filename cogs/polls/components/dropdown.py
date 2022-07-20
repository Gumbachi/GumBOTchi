from typing import TYPE_CHECKING

import discord
from discord import SelectOption
from discord.ui import Select

if TYPE_CHECKING:
    from .poll import Poll


class OptionsDropdown(Select):
    def __init__(self, poll: 'Poll'):
        self.poll = poll

        super().__init__(
            placeholder="Select your answers here...",
            min_values=1,
            max_values=poll.max_votes,
            options=[SelectOption(label=opt) for opt in poll.options],
        )

    async def callback(self, interaction: discord.Interaction):
        """Called when a user places a vote."""
        selected = self.values

        if interaction.user in self.poll.voters:
            self.poll.last_action = f"{interaction.user} has changed their vote"
        else:
            self.poll.last_action = f"{interaction.user} has voted"

        self.poll.voters[interaction.user] = selected

        await interaction.response.edit_message(
            embed=self.poll.embed,
            view=self.poll
        )
