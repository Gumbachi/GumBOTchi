import discord
from discord.ui import Button

from .poll import Poll


class ClosePollButton(Button):
    def __init__(self, poll: Poll):
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
    def __init__(self, poll: Poll):
        self.poll = poll
        super().__init__(emoji="⏬")

    async def callback(self, interaction: discord.Interaction):
        """Delete old message and send new message at bottom of channel."""
        await interaction.message.delete()
        await interaction.response.send_message(embed=self.poll.embed, view=self.poll)
