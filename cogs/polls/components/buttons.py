from typing import TYPE_CHECKING

import discord
from discord.ui import Button

if TYPE_CHECKING:
    from .poll import Poll


class ClosePollButton(Button):
    def __init__(self, poll: 'Poll'):
        self.poll = poll
        super().__init__(style=discord.ButtonStyle.red, label="X")

    async def callback(self, interaction: discord.Interaction):
        """If owner, close the poll. Otherwise mock."""
        if interaction.user != self.poll.owner:
            self.poll.last_action = f"{interaction.user.name} tried to grief but failed"
            await interaction.response.edit_message(embed=self.poll.embed, view=self.poll)
        else:
            self.poll.close()
            self.poll.last_action = f"{interaction.user.name} has closed the poll"
            await interaction.response.edit_message(embed=self.poll.embed, view=None)


class ResendPollButton(Button):
    def __init__(self, poll: 'Poll'):
        self.poll = poll
        super().__init__(emoji="⏬")

    async def callback(self, interaction: discord.Interaction):
        """Delete old message and send new message at bottom of channel."""

        if interaction.user != self.poll.owner:
            self.poll.last_action = f"{interaction.user.name} tried to grief but failed"
            await interaction.response.edit_message(embed=self.poll.embed, view=self.poll)
        else:
            message = await interaction.channel.send(embed=self.poll.embed, view=self.poll)
            await interaction.response.edit_message(content=message.jump_url, embed=None, view=None)
