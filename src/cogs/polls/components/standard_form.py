"""Holds the form/Modal Dialog used to create a standard poll."""

import discord

from ..standard_poll import StandardPoll


class StandardPollForm(discord.ui.Modal):
    def __init__(self, timeout: float, max_votes: int, live: bool):
        self.view_timeout = timeout
        self.max_votes = max_votes
        self.live = live

        question = discord.ui.InputText(
            label="The Question",
            placeholder="Is GumBOTchi the best bot ever made?",
            min_length=2
        )

        placeholders = [
            "Yes, and he is incredibly handsome",
            "Well I dont see any other bots saying howdy",
            "GumBOTchi is bussin, no cap fr fr (hi didna)",
            "No, GumBOTchi sucks (its April 1st)"
        ]

        options = [
            discord.ui.InputText(
                label=f"Option {i}",
                placeholder=placeholder,
                min_length=1,
                max_length=99,
                required=i < 3
            ) for i, placeholder in enumerate(placeholders, 1)
        ]

        super().__init__(*[question, *options], title="Create Your Poll")

    async def callback(self, interaction: discord.Interaction):

        question = self.children[0].value
        options = [child.value for child in self.children[1:] if child.value]

        poll = StandardPoll(
            question=question,
            options=options,
            timeout=self.view_timeout,
            max_votes=self.max_votes,
            live=self.live,
            owner=interaction.user
        )

        await interaction.response.send_message(embed=poll.embed, view=poll)
