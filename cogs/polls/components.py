import itertools

import discord
from discord import EmbedField, Interaction, SelectOption
from discord.ui import Button, Select, View, InputText


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
        print(self.voters)
        self.last_action = "Time's up. Poll's closed"
        self.close()
        await self.interaction.edit_original_message(embed=self.embed, view=None)

    def close(self):
        self.open = False
        self.stop()


class ClosePollButton(Button):

    def __init__(self, poll: Poll):
        self.poll = poll
        super().__init__(style=discord.ButtonStyle.red, label="X")

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.poll.owner:
            self.poll.last_action = f"{interaction.user.name} tried to grief but failed"
            await interaction.response.edit_message(embed=self.poll.embed, view=self.poll)
        else:
            self.poll.close()
            self.poll.last_action = f"{interaction.user.name} has closed the poll"
            await interaction.response.edit_message(embed=self.poll.embed, view=None)


class OptionsDropdown(Select):
    def __init__(self, poll: Poll):
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
            embed=self.poll.embed, view=self.poll)


class PollCreationForm(discord.ui.Modal):
    def __init__(self, timeout: float, max_votes: int, live: bool):
        self.view_timeout = timeout
        self.max_votes = max_votes
        self.live = live

        question = InputText(
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
            InputText(
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

        poll = Poll(
            question=question,
            options=options,
            timeout=self.view_timeout,
            max_votes=self.max_votes,
            live=self.live,
            owner=interaction.user
        )

        sent_interaction = await interaction.response.send_message(embed=poll.embed, view=poll)
        poll.interaction = sent_interaction
