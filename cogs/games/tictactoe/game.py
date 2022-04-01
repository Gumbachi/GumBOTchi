import discord
from discord.ui import View


class Game:
    def __init__(self, p1: discord.Member, p2: discord.Member):
        self.p1 = p1
        self.p2 = p2
        self.board = [TicTacToeButton(i, self) for i in range(9)]
        self.turn = p1
        self.winner = None

    @property
    def headline(self):
        if not self.winner:
            return f"{self.turn.nick or self.turn.name}'s Turn"
        else:
            return f"{self.winner} Wins"

    @property
    def embed(self):
        return discord.Embed(title=self.headline)

    @property
    def view(self):
        return View(*self.board)

    def changeturn(self):
        if self.turn == self.p1:
            self.turn = self.p2
        else:
            self.turn = self.p1

    def checkwin(self):
        """Checks to see if there is a winner."""
        board = [btn.owner for btn in self.board]
        winner = None

        # Horizontals
        for i in [0, 3, 6]:
            if all(player == self.p1 for player in [board[0+i], board[1+i], board[2+i]]):
                winner = self.p1
            elif all(player == self.p2 for player in [board[0+i], board[1+i], board[2+i]]):
                winner = self.p2

        # Verticals
        for i in range(3):
            if all(player == self.p1 for player in [board[0+i], board[3+i], board[6+i]]):
                winner = self.p1
            elif all(player == self.p2 for player in [board[0+i], board[3+i], board[6+i]]):
                winner = self.p2

        # Diagonals
        if all(player == self.p1 for player in [board[0], board[4], board[8]]):
            winner = self.p1
        elif all(player == self.p2 for player in [board[0], board[4], board[8]]):
            winner = self.p2

        if all(player == self.p1 for player in [board[2], board[4], board[6]]):
            winner = self.p1
        elif all(player == self.p2 for player in [board[2], board[4], board[6]]):
            winner = self.p2

        self.winner = winner

        if winner:
            self.end()

    def end(self):
        for button in self.board:
            button.disabled = True


class TicTacToeButton(discord.ui.Button):
    def __init__(self, index, game):
        super().__init__(label="\u200b", row=index // 3)
        self.game = game
        self.index = index
        self.owner = None

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.game.turn:
            return

        self.owner = interaction.user
        self.label = "X" if interaction.user == self.game.p1 else "O"
        self.disabled = True

        self.game.checkwin()

        await interaction.response.edit_message(embed=self.game.embed, view=self.game.view)
        self.game.changeturn()
