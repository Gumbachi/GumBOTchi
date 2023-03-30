
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from ..free_poll import FreePoll


class AddOptionModal(discord.ui.Modal):
    def __init__(self, poll: "FreePoll"):
        self.poll = poll

        question = discord.ui.InputText(
            label="Your Answer",
            placeholder="GumBOTchi is just too good",
            min_length=2
        )

        super().__init__(question, title="Add your option to the poll")

    async def callback(self, interaction: discord.Interaction):

        option = self.children[0].value

        self.poll.options[option] = {interaction.user}

        self.poll.update_options_select()

        await interaction.response.edit_message(embed=self.poll.embed, view=self.poll)
