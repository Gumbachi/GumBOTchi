"""Holds the main Poll object that contains votes and manages buttons and the embed."""

import itertools

import discord


class StandardPoll(discord.ui.View):
    def __init__(self, question: str, options: list[str], timeout: float, max_votes: int, live: bool,  owner: discord.Member):
        self.question = question
        self.options = options
        self.live = live

        self.owner = owner
        self.closed = False
        self.last_action = "Nothing has happened with this poll yet"

        # dict to keep track of who voted and what for
        self.voters: dict[discord.User: list[str]] = {}

        super().__init__(timeout=timeout)

        # Modify select to reflect options
        options_select: discord.ui.Select = self.children[0]
        options_select.max_values = max_votes if max_votes <= len(options) else len(options)
        options_select.options = [discord.SelectOption(label=opt) for opt in options]

    def count_votes(self, option: str) -> tuple[int, int]:
        """Counts votes for an options and also returns total ex. (4, 10)"""
        flattened = list(itertools.chain.from_iterable(self.voters.values()))
        return flattened.count(option), len(flattened)

    @property
    def embed(self) -> discord.Embed:
        status = "CLOSED 🔴" if self.closed else "OPEN 🟢"
        embed_color = discord.Color.red() if self.closed else discord.Color.blue()

        fields = []
        for opt, color in zip(self.options, ("🟥", "🟦", "🟩", "🟨")):
            count, total = self.count_votes(opt)

            if self.live or self.closed:
                percentage = 0.0 if total == 0 else count / total
                blocks = int(percentage * 20)
                fields.append(
                    discord.EmbedField(
                        name=f"{opt}  •  {count} votes  •  {percentage:.1%}",
                        value=f"{color * blocks}{'⬛' * (20 - blocks)}"
                    )
                )
            else:
                fields.append(
                    discord.EmbedField(
                        name=f"{opt}",
                        value="⬛" * 20
                    )
                )

        embed = discord.Embed(
            title=self.question,
            description=f"Poll Status: {status}  •  {total} Votes",
            fields=fields,
            color=embed_color
        )

        embed.set_footer(text=self.last_action)
        return embed

    async def on_timeout(self) -> None:
        """Close the poll on view timeout."""
        self.closed = True
        self.last_action = "Time's up. Poll's closed"
        await self.message.edit(embed=self.embed, view=None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Permit only dropdown to be used by everyone."""
        dropdown: discord.ui.Select = self.children[0]

        # Dropdown accessible to anyone
        if interaction.custom_id == dropdown.custom_id:
            return True

        # Admin buttons only accessible by owner
        if interaction.user != self.owner:
            return False

        return True

    @discord.ui.select(placeholder="Select your answers here...")
    async def history_select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        """The callback function for the poll option select."""
        if interaction.user in self.voters:
            self.last_action = f"{interaction.user.display_name} has changed their vote"
        else:
            self.last_action = f"{interaction.user.display_name} has voted"

        self.voters[interaction.user] = select.values

        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label="Close Poll", style=discord.ButtonStyle.red)
    async def close_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Callback for the close poll button."""
        self.closed = True
        self.last_action = f"{interaction.user.display_name} has closed the poll"
        await interaction.response.edit_message(embed=self.embed, view=None)

    @discord.ui.button(label="Resend Poll")
    async def resend_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Callback for the resend poll button."""
        message = await interaction.channel.send(embed=self.embed, view=self)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="This poll has been moved.",
                description=message.jump_url
            ),
            view=None
        )
