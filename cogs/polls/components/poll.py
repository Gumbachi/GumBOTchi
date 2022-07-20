"""Holds the main Poll object that contains votes and manages buttons and the embed."""

import itertools

import discord
from discord import EmbedField, Interaction
from discord.ui import View

from .buttons import ClosePollButton, ResendPollButton
from .dropdown import OptionsDropdown


class Poll(View):
    def __init__(self, question: str, options: list[str], timeout: float, max_votes: int, live: bool,  owner: discord.Member):
        self.question = question
        self.options = options
        self.live = live
        self.interaction: None | Interaction = None

        self.max_votes = max_votes
        if max_votes > len(options):
            self.max_votes = len(options)

        self.owner = owner
        self.open = True
        self.last_action = "Nothing has happened with this poll yet"

        # dict to keep track of who voted and what for
        self.voters: dict[discord.User: list[str]] = {}

        super().__init__(
            OptionsDropdown(self),
            ClosePollButton(self),
            ResendPollButton(self),
            timeout=timeout
        )

    def count_votes(self, option: str) -> tuple[int, int]:
        """Counts votes for an options and also returns total ex. (4, 10)"""
        flattened = list(itertools.chain.from_iterable(self.voters.values()))
        return flattened.count(option), len(flattened)

    @property
    def embed(self) -> discord.Embed:

        status = "OPEN 🟢" if self.open else "CLOSED 🔴"

        fields = []
        for opt, color in zip(self.options, ("🟥", "🟦", "🟩", "🟨")):
            count, total = self.count_votes(opt)

            if self.live or not self.open:
                percentage = 0.0 if total == 0 else count / total
                blocks = int(percentage * 20)
                fields.append(
                    EmbedField(
                        name=f"{opt}  •  {count} votes  •  {percentage * 100:.1f}%",
                        value=f"{color * blocks}{'⬛' * (20 - blocks)}"
                    )
                )
            else:
                fields.append(
                    EmbedField(
                        name=f"{opt}  •  ?? votes  •  ??.?%",
                        value="⬛" * 20
                    )
                )

        embed = discord.Embed(
            title=self.question,
            description=f"Poll Status: {status}  •  {total} Votes",
            fields=fields
        )

        embed.set_footer(text=self.last_action)
        return embed

    async def on_timeout(self) -> None:
        self.last_action = "Time's up. Poll's closed"
        self.close()
        await self.interaction.edit_original_message(embed=self.embed, view=None)

    def close(self):
        self.open = False
        self.stop()
