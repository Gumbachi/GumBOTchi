import discord
from cogs.games.rps.enums import RPSMove, RPSState
from cogs.games.rps.player import Player

import cogs.games.rps.buttons as buttons


class Game():

    def __init__(self, playerone: discord.Member, playertwo: discord.Member):
        self.p1 = Player(playerone)
        self.p2 = Player(playertwo)

        self.buttons = [
            buttons.RockButton(self),
            buttons.PaperButton(self),
            buttons.ScissorButton(self)
        ]

        self.state: RPSState = RPSState.ONGOING

    @property
    def embed(self):
        return discord.Embed(
            title=self.headline,
            description=self.playbyplay,
            color=discord.Color.blue()
        )

    @property
    def view(self):
        return discord.ui.View(*self.buttons)

    @property
    def headline(self):
        """Generates the string to be the title of the game embed."""
        # Player one wins
        if self.state == RPSState.PLAYERONEWIN:
            return f"{self.p1} Wins!"

        # Player two wins
        if self.state == RPSState.PLAYERTWOWIN:
            return f"{self.p2} Wins!"

        # Its a tie
        if self.state == RPSState.TIE:
            return f"It's a tie :("

        # Default
        return f"{self.p1} vs {self.p2}"

    @property
    def playbyplay(self):
        """Generates the string that represents the game events."""
        if self.state == RPSState.ONGOING:
            return

        return f"{self.p1} plays {self.p1.move}\n{self.p2} counters with {self.p2.move}"

    @property
    def players(self):
        return (self.p1, self.p2)

    def check_win(self):
        """Check the game status for a win."""

        if self.p1.choice is None or self.p2.choice is None:
            print(self.p1.choice, self.p2.choice)
            return

        win_conditions = {
            # Player One win conditions
            (RPSMove.ROCK, RPSMove.SCISSORS): RPSState.PLAYERONEWIN,
            (RPSMove.PAPER, RPSMove.ROCK): RPSState.PLAYERONEWIN,
            (RPSMove.SCISSORS, RPSMove.PAPER): RPSState.PLAYERONEWIN,

            # Player two win conditions
            (RPSMove.SCISSORS, RPSMove.ROCK): RPSState.PLAYERTWOWIN,
            (RPSMove.PAPER, RPSMove.SCISSORS): RPSState.PLAYERTWOWIN,
            (RPSMove.ROCK, RPSMove.PAPER): RPSState.PLAYERTWOWIN,

            # Tie conditions
            (RPSMove.ROCK, RPSMove.ROCK): RPSState.TIE,
            (RPSMove.PAPER, RPSMove.PAPER): RPSState.TIE,
            (RPSMove.SCISSORS, RPSMove.SCISSORS): RPSState.TIE
        }

        # set game state
        self.state = win_conditions[(self.p1.choice, self.p2.choice)]

        # end game and disable buttons
        self.end()

    def end(self):
        for button in self.buttons:
            button.disabled = True
