import random
import discord


class Game:
    def __init__(self, p1: discord.Member, p2: discord.Member):
        self.p1 = p1
        self.p2 = p2
        self.turn = p1
        self.winner = None
        self.board = [TicTacToeButton(i, self) for i in range(9)]

    @property
    def headline(self):
        if self.winner:
            return f"{self.winner.nick or self.winner.name} Wins"
        return f"{self.p1.nick or self.p1.name} VS {self.p2.nick or self.p2.name}"

    @property
    def subline(self):
        if not self.winner:
            return f"({self.currentlabel}) {self.turn.nick or self.turn.name}'s Turn"

    @property
    def embed(self):
        return discord.Embed(
            title=self.headline,
            description=self.subline,
            color=discord.Color.blue()
        )

    @property
    def view(self):
        return discord.ui.View(*self.board, timeout=360)

    @property
    def currentlabel(self):
        """Retrieve the label for the current turn player"""
        if self.turn == self.p1:
            return "X"
        return "O"

    def highlight(self, *indexes):
        for i in indexes:
            self.board[i].style = discord.ButtonStyle.green

    def changeturn(self):
        """Swaps whose turn it is."""
        if self.turn == self.p1:
            self.turn = self.p2
        else:
            self.turn = self.p1

    # TODO This function could be better by removing duplicate code
    def checkwin(self):
        """Checks to see if there is a winner. Sets winner and highlights path as needed."""
        board = [btn.owner for btn in self.board]
        winner = None

        # Horizontals
        for i in [0, 3, 6]:
            if all(player == self.p1 for player in [board[0+i], board[1+i], board[2+i]]):
                winner = self.p1
                self.highlight(0+i, 1+i, 2+i)
            elif all(player == self.p2 for player in [board[0+i], board[1+i], board[2+i]]):
                winner = self.p2
                self.highlight(0+i, 1+i, 2+i)

        # Verticals
        for i in range(3):
            if all(player == self.p1 for player in [board[0+i], board[3+i], board[6+i]]):
                winner = self.p1
                self.highlight(0+i, 3+i, 6+i)
            elif all(player == self.p2 for player in [board[0+i], board[3+i], board[6+i]]):
                winner = self.p2
                self.highlight(0+i, 3+i, 6+i)

        # Diagonals
        if all(player == self.p1 for player in [board[0], board[4], board[8]]):
            winner = self.p1
            self.highlight(0, 4, 8)
        elif all(player == self.p2 for player in [board[0], board[4], board[8]]):
            winner = self.p2
            self.highlight(0, 4, 8)

        if all(player == self.p1 for player in [board[2], board[4], board[6]]):
            winner = self.p1
            self.highlight(2, 4, 6)
        elif all(player == self.p2 for player in [board[2], board[4], board[6]]):
            winner = self.p2
            self.highlight(2, 4, 6)

        self.winner = winner

    def automove(self):
        """The function called to make the bot move"""
        options = [b for b in self.board if not b.owner]
        choice = random.choice(options)
        self.makemove(choice.index)

    def makemove(self, index):
        """Places a move on the board"""
        button = self.board[index]
        button.owner = self.turn
        button.label = self.currentlabel
        button.disabled = True

        self.changeturn()

        # Bot needs to automove since it cannot click buttons
        if self.turn.bot:
            # Winner must be checked so bot doesnt move after a win
            self.checkwin()
            if not self.winner:
                self.automove()

    def end(self):
        for button in self.board:
            button.disabled = True


class TicTacToeButton(discord.ui.Button):
    def __init__(self, index: int, game: Game):
        super().__init__(label="\u200b", row=index // 3)
        self.game = game
        self.index = index
        self.owner = None

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.game.turn:
            return

        self.game.makemove(self.index)
        self.game.checkwin()

        if self.game.winner:
            self.game.end()

        await interaction.response.edit_message(embed=self.game.embed, view=self.game.view)
