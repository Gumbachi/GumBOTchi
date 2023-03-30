"""Holds the main Poll object that contains votes and manages buttons and the embed."""

import discord

from .components import AddOptionModal


class FreePoll(discord.ui.View):
    def __init__(self, question: str, timeout: float, owner: discord.Member):
        self.owner = owner
        self.question = question
        self.options: dict[str, set[discord.Member]] = {}

        self.closed = False

        super().__init__(timeout=timeout)

    @ property
    def embed(self) -> discord.Embed:
        status = "CLOSED 🔴" if self.closed else "OPEN 🟢"
        color = discord.Color.red() if self.closed else discord.Color.blue()

        embed = discord.Embed(
            title=self.question,
            description=f"Poll Status: {status}",
            color=color
        )

        if not self.options:
            embed.add_field(
                name="There are currently no options",
                value="Write in your vote to add it to the list for others to vote for"
            )
        else:
            for option, voters in self.options.items():
                embed.add_field(
                    name=f"{option}",
                    value=f"{len(voters)} votes",
                    inline=False
                )

        return embed

    async def on_timeout(self) -> None:
        """Close the poll on view timeout."""
        self.closed = True
        await self.message.edit(embed=self.embed, view=None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Permit only dropdown to be used by everyone."""
        dropdown: discord.ui.Select = self.children[0]
        add_button: discord.ui.Button = self.children[1]

        # Dropdown/add vote accessible to anyone
        if interaction.custom_id in (dropdown.custom_id, add_button.custom_id):
            return True

        # Admin buttons only accessible by owner
        if interaction.user != self.owner:
            return False

        return True

    @ discord.ui.select(
        placeholder="Vote for answers you like here...",
        disabled=True,
        options=[
            discord.SelectOption(
                label="Easter Egg",
                description="You weren't supposed to find this"
            )
        ]
    )
    async def option_select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        """The callback function for the poll option select."""

        for value in select.values:
            if interaction.user in self.options[value]:
                self.options[value].discard(interaction.user)
            else:
                self.options[value].add(interaction.user)

        await interaction.response.edit_message(embed=self.embed, view=self)

    @ discord.ui.button(label="Add Option")
    async def add_option_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Callback for the add option poll button."""
        await interaction.response.send_modal(modal=AddOptionModal(self))

    @ discord.ui.button(label="Close Poll", style=discord.ButtonStyle.red)
    async def close_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Callback for the close poll button."""
        self.closed = True
        self.last_action = f"{interaction.user.display_name} has closed the poll"
        await interaction.response.edit_message(embed=self.embed, view=None)

    @ discord.ui.button(label="Resend Poll")
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

    def update_options_select(self):
        """Update the options dropdown."""
        if not self.options:
            return

        options_select: discord.ui.Select = self.children[0]

        options_select.options = [
            discord.SelectOption(label=option) for option in self.options.keys()
        ]
        options_select.disabled = False
