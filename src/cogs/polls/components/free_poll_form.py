"""Holds the form/Modal Dialog used to create a write in poll."""

import discord

from ..free_poll import FreePoll


class FreePollForm(discord.ui.Modal):
    def __init__(self, timeout: float):
        self.view_timeout = timeout

        question = discord.ui.InputText(
            label="The Question",
            placeholder="Why is GumBOTchi the best bot ever made?",
            min_length=2
        )

        super().__init__(question, title="Create Your Poll")

    async def callback(self, interaction: discord.Interaction):

        question = self.children[0].value

        poll = FreePoll(
            question=question,
            timeout=self.view_timeout,
            owner=interaction.user
        )

        await interaction.response.send_message(embed=poll.embed, view=poll)
