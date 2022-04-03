import random
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
        self.p1 = playerone
        self.p2 = playertwo
        self.board = [[None] * 7 for _ in range(6)]
        self.cursor_position = 3
        self.turn = self.p1
        self.winner = None

    def __str__(self):
        string = f"{self.cursor_row}\n\n"
        for row in self.displayboard:
            string += " ".join(row) + "\n"

        return string

    @property
    def players(self):
        return (self.p1, self.p2)

    @property
    def cursor_row(self):
        """Generates a string representing the cursor row."""
        row = [Emoji.EMPTY] * 7
        row[self.cursor_position] = self.getpiece(self.turn)
        return " ".join(row)

    @property
    def displayboard(self):
        """Replaces board of players with emojis."""
        return [[self.getpiece(p) for p in row] for row in self.board]

    @property
    def headline(self):
        if self.winner:
            return f"{self.winner.name} Wins!"
        return f"{Emoji.RED} {self.p1.nick or self.p1.name} VS {Emoji.YELLOW} {self.p2.nick or self.p2.name}"

    @property
    def color(self):
        if self.turn == self.p1:
            return discord.Color.red()
        return discord.Color.yellow()

    @property
    def embed(self):
        """Formats the game into a discord Embed."""
        return discord.Embed(
            title=self.headline,
            description=str(self),
            color=self.color
        )

    @property
    def view(self):

        submitbutton = SubmitButton(self)
        submitbutton.disabled = bool(self.winner)

        leftbutton = LeftButton(self)
        leftbutton.disabled = bool(self.winner)

        rightbutton = RightButton(self)
        rightbutton.disabled = bool(self.winner)

        return discord.ui.View(
            leftbutton,
            rightbutton,
            submitbutton,
            timeout=900
        )

    def getplayer(self, piece: Emoji):
        """Get player from an Emoji"""
        return self.p1 if piece == Emoji.RED else self.p2

    def getpiece(self, player: discord.Member | None):
        match player:
            case self.p1:
                return Emoji.RED
            case self.p2:
                return Emoji.YELLOW
            case _:
                return Emoji.WHITE

    def column(self, index: int):
        """Returns a column of the board."""
        return [row[index] for row in self.board]

    def row(self, index: int):
        """Returns a row of the board."""
        return self.board[index]

    def swap_turn(self):
        """Switches the current player whose turn it is."""
        self.turn = self.p2 if self.turn == self.p1 else self.p1
        if self.turn.bot:
            self.automove()

    def column_is_full(self, index: int):
        """Check if a column is full of pieces"""
        return all(self.column(index))

    def find_open_row_index(self, column: int):
        """Find the first row index with an empty spot within a column"""
        # Work way up from bottom of board to find open slot
        for i in range(5, -1, -1):
            if self.board[i][column]:
                continue

            return i

    def automove(self):

        options = list(range(7))
        random.shuffle(options)

        for i in options:
            if self.column_is_full(i):
                continue

            self.submit_move(i)
            break

    def submit_move(self, column: int | None = None):
        """Processes where the piece should go."""

        column = self.cursor_position if column == None else column

        if self.column_is_full(column):
            return

        row = self.find_open_row_index(column)
        self.board[row][column] = self.turn

        self.check_win()
        if not self.winner:
            self.swap_turn()

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
