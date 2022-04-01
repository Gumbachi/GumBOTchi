import discord
from .buttons import *


class Emoji:
    RED = "🔴"
    WHITE = "⚪"
    YELLOW = "🟡"
    DOWN = "⬇️"
    EMPTY = "⚫"


class Game:
    """Game object to facilitate game state and game actions."""

    def __init__(self, playerone: discord.Member, playertwo: discord.Member):
        self.playerone = playerone
        self.playertwo = playertwo
        self.board = [[None] * 7 for _ in range(6)]
        self.cursor_position = 3
        self.turn = playerone
        self.winner = None

    def __str__(self):
        string = f"{self.cursor_row}\n\n"
        for row in self.displayboard:
            string += "   ".join(row) + "\n"

        return string

    @property
    def cursor_row(self):
        """Generates a string representing the cursor row."""
        row = [Emoji.EMPTY] * 7
        row[self.cursor_position] = self.get_piece(self.turn)
        return "   ".join(row)

    @property
    def displayboard(self):
        """Replaces board of players with emojis."""
        return [[self.get_piece(p) for p in row] for row in self.board]

    @property
    def embed(self) -> discord.Embed:
        """Formats the game into a discord Embed."""
        title = f"{Emoji.RED} {self.playerone.name} VS {Emoji.YELLOW} {self.playertwo.name}"
        if self.winner:
            title = f"{self.winner.name} Wins!"

        color = discord.Color.yellow() if self.turn == self.playertwo else discord.Color.red()

        return discord.Embed(title=title, description=str(self), color=color)

    @property
    def view(self) -> discord.ui.View:

        sb = SubmitButton(self)
        sb.disabled = bool(self.winner)

        return discord.ui.View(
            BigLeftButton(self),
            LeftButton(self),
            RightButton(self),
            BigRightButton(self),
            sb,
            timeout=None
        )

    def get_player(self, piece: Emoji) -> discord.Member:
        return self.playerone if piece == Emoji.RED else self.playertwo

    def get_piece(self, player: discord.Member | None) -> Emoji:
        if player == self.playerone:
            return Emoji.RED
        if player == self.playertwo:
            return Emoji.YELLOW
        return Emoji.WHITE

    def get_column(self, index: int):
        return [row[index] for row in self.board]

    def swap_turn(self):
        """Switches the current player whose turn it is."""
        self.turn = self.playertwo if self.turn == self.playerone else self.playerone

    def submit_move(self):
        """Processes where the piece should go."""
        for i in range(5, -1, -1):
            if self.board[i][self.cursor_position]:
                continue

            self.board[i][self.cursor_position] = self.turn
            break

    def check_win(self):
        """Determine if a player has won."""
        # horizontal check
        for row in reversed(self.board):
            for i in range(4):
                if not row[i]:
                    continue
                group = row[i:i+4]
                if group.count(row[i]) == len(group):
                    self.winner = row[i]
                    return

        # vertical check
        for x in range(7):
            for y in range(3):
                if not self.board[y][x]:
                    continue

                if self.board[y][x] == self.board[y+1][x] == self.board[y+2][x] == self.board[y+3][x]:
                    print("WINNER")
                    self.winner = self.board[y][x]
                    return

        # ascendingDiagonalCheck
        for x in range(3, 7):
            for y in range(3):
                if not self.board[y][x]:
                    continue

                if self.board[y][x] == self.board[y+1][x-1] == self.board[y+2][x-2] == self.board[y+3][x-3]:
                    self.winner = self.board[y][x]
                    return

        # descendingDiagonalCheck
        for x in range(3, 7):
            for y in range(3, 6):

                # None check
                if not self.board[y][x]:
                    continue

                if self.board[y][x] == self.board[y-1][y-1] == self.board[y-2][x-2] == self.board[y-3][x-3]:
                    self.winner = self.board[y][x]
                    return
