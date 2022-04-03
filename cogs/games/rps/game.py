import discord
from cogs.games.rps.enums import Move, RPSMove, RPSState
from cogs.games.rps.player import Player


class Game():
    """Holds data for a RockPaperScissors Game."""

    def __init__(self, playerone: discord.Member, playertwo: discord.Member):
        self.p1 = Player(playerone)
        self.p2 = Player(playertwo)

        self.buttons = [
            RPSButton(self, RPSMove.ROCK),
            RPSButton(self, RPSMove.PAPER),
            RPSButton(self, RPSMove.SCISSORS),
        ]

        self.state = RPSState.ONGOING

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
        match self.state:
            case RPSState.PLAYERONEWIN:
                return f"{self.p1} Wins!"
            case RPSState.PLAYERTWOWIN:
                return f"{self.p2} Wins!"
            case RPSState.TIE:
                return f"It's a tie :("
            case _:
                return f"{self.p1} VS {self.p2}"

    @property
    def playbyplay(self):
        """Generates the string that represents the game events."""
        if not self.state == RPSState.ONGOING:
            return f"{self.p1} plays {self.p1.move}\n{self.p2} counters with {self.p2.move}"

    @property
    def players(self):
        return (self.p1, self.p2)

    def check_win(self):
        """Check the game status for a win."""

        if self.p1.choice is None or self.p2.choice is None:
            return

        # Determine game result
        if self.p1.choice == self.p2.choice:
            self.state = RPSState.TIE
        elif self.p1.choice > self.p2.choice:
            self.state = RPSState.PLAYERONEWIN
        else:
            self.state = RPSState.PLAYERTWOWIN

        # end game and disable buttons
        self.end()

    def end(self):
        for button in self.buttons:
            button.disabled = True


class RPSButton(discord.ui.Button):
    def __init__(self, game: Game, move: Move):
        super().__init__(emoji=move.emoji)
        self.game = game
        self.move = move

    async def callback(self, interaction: discord.Interaction):
        if interaction.user not in self.game.players:
            return

        # Set the player choice to the move made
        if self.game.p1 == interaction.user:
            self.game.p1.choice = self.move
        else:
            self.game.p2.choice = self.move

        self.game.check_win()
        await interaction.response.edit_message(embed=self.game.embed, view=self.game.view)
