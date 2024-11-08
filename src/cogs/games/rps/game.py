import random

import discord


class Game(discord.ui.View):
    """Holds data for a RockPaperScissors Game."""

    def __init__(self, p1: discord.Member, p2: discord.Member):
        self.p1 = p1
        self.p2 = p2
        self.moves = {p1: None, p2: None}

        self.score = [0, 0]
        self.headline = f"{p1.display_name} VS {p2.display_name}"

        super().__init__(timeout=300)

        self.rock_button: discord.ui.Button = self.children[0]
        self.paper_button: discord.ui.Button = self.children[1]
        self.scissors_button: discord.ui.Button = self.children[2]
        self.rematch_button: discord.ui.Button = self.children[3]

        # Auto Move
        if self.p2.bot:
            self.moves[p2] = random.choice(("rock", "paper", "scissors"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user in (self.p1, self.p2)

    @discord.ui.button(emoji="🪨")
    async def _rock_button_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        """Handle a player hitting rock."""
        self.moves[interaction.user] = "rock"
        self.check_win()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label="🧻")
    async def _paper_button_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        """Handle a player hitting paper."""
        self.moves[interaction.user] = "paper"
        self.check_win()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label="✂️")
    async def _scissors_button_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        """Handle a player hitting scissors."""
        self.moves[interaction.user] = "scissors"
        self.check_win()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label="Rematch", disabled=True)
    async def _rematch_button_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        """Handle a player hitting rematch."""

        # Reset buttons
        self.rock_button.style = discord.ButtonStyle.gray
        self.paper_button.style = discord.ButtonStyle.gray
        self.scissors_button.style = discord.ButtonStyle.gray
        self.rock_button.disabled = False
        self.paper_button.disabled = False
        self.scissors_button.disabled = False

        # Reset moves
        self.moves[self.p1] = None
        self.moves[self.p2] = (
            random.choice(("rock", "paper", "scissors")) if self.p2.bot else None
        )

        # Reset
        self.headline = f"{self.p1.display_name} VS {self.p2.display_name}"
        button.disabled = True

        await interaction.response.edit_message(embed=self.embed, view=self)

    @property
    def embed(self):
        return discord.Embed(
            title=f"{self.headline} \u2022 {self.score[0]} - {self.score[1]}",
            description=self.play_tracker,
            color=discord.Color.blue(),
        )

    @property
    def play_tracker(self) -> str:
        """Keeps track of who has moved and who hasn't"""
        match (self.moves[self.p1], self.moves[self.p2]):
            case (None, None):
                return f"🔴 {self.p1.display_name}\n🔴 {self.p2.display_name}"
            case (None, _):
                return f"🔴 {self.p1.display_name}\n🟢 {self.p2.display_name}"
            case (_, None):
                return f"🟢 {self.p1.display_name}\n🔴 {self.p2.display_name}"
            case _:
                return ""

    def check_win(self):
        """Check the game status for a win."""

        # Still waiting for everyone
        if not all(self.moves.values()):
            return

        match (self.moves[self.p1], self.moves[self.p2]):
            case ("rock", "scissors") | ("paper", "rock") | ("scissors", "paper"):
                self.headline = f"{self.p1.display_name} Wins!"
                self.score[0] += 1
                self.end(winner=self.p1)
            case ("scissors", "rock") | ("rock", "paper") | ("paper", "scissors"):
                self.headline = f"{self.p2.display_name} Wins!"
                self.score[1] += 1
                self.end(winner=self.p2)
            case _:
                self.headline = (
                    f"{self.p2.display_name} copied {self.p1.display_name}'s homework"
                )
                self.end(winner=None)

    def end(self, winner: discord.Member | None):
        """Highlight wining buttons and disable"""

        self.rock_button.disabled = True
        self.paper_button.disabled = True
        self.scissors_button.disabled = True
        self.rematch_button.disabled = False

        if not winner:
            return

        match self.moves[winner]:
            case "rock":
                self.rock_button.style = discord.ButtonStyle.green
                self.scissors_button.style = discord.ButtonStyle.red
            case "paper":
                self.paper_button.style = discord.ButtonStyle.green
                self.rock_button.style = discord.ButtonStyle.red
            case "scissors":
                self.scissors_button.style = discord.ButtonStyle.green
                self.paper_button.style = discord.ButtonStyle.red
