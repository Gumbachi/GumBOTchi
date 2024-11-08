import random
from itertools import chain

import discord


class Piece:
    RED = "🔴"
    EMPTY = "⚪"
    YELLOW = "🟡"


class Game(discord.ui.View):
    ROWS = 6
    COLS = 7

    def __init__(self, p1: discord.Member, p2: discord.Member):
        self.p1 = p1
        self.p2 = p2
        self.board = [[Piece.EMPTY] * self.COLS for _ in range(self.ROWS)]

        self.cursor_position = self.COLS // 2

        self.title = (
            f"{Piece.RED} {p1.display_name} VS {p2.display_name} {Piece.YELLOW}"
        )
        self.finished = False

        self.labels = {p1: Piece.RED, p2: Piece.YELLOW}
        self.players = {Piece.RED: p1, Piece.YELLOW: p2}

        super().__init__(timeout=None)

        self.left_button: discord.ui.Button = self.children[0]
        self.submit_button: discord.ui.Button = self.children[1]
        self.right_button: discord.ui.Button = self.children[2]

    def visual_board(self, draw_cursor=True) -> str:
        """A visual representation of the board."""
        board = "\n".join([" ".join(row) for row in self.board])
        if not draw_cursor:
            return board

        cursor_row = ["⚫"] * self.COLS
        cursor_row[self.cursor_position] = self.labels[self.turn]
        cursor_row = f"{' '.join(cursor_row)}"

        return f"{cursor_row}\n\n{board}"

    @property
    def turn(self) -> discord.Member:
        """Calculate whose turn it is to play"""
        unused_count = self.count_moves(Piece.EMPTY)
        return self.p1 if unused_count % 2 == 0 else self.p2

    @property
    def embed(self):
        """Formats the game into a discord Embed."""

        if not self.finished:
            color = (
                discord.Color.red() if self.turn == self.p1 else discord.Color.yellow()
            )
        else:
            color = (
                discord.Color.yellow() if self.turn == self.p1 else discord.Color.red()
            )

        return discord.Embed(
            title=self.title,
            description=self.visual_board(draw_cursor=not self.finished),
            color=color,
        )

    def count_moves(self, piece: str) -> int:
        """Count how many moves there are from a specific piece"""
        flattened = list(chain.from_iterable(self.board))
        return flattened.count(piece)

    def get_column(self, index: int) -> list[str]:
        """Returns a column of the board."""
        return [row[index] for row in self.board]

    def get_row(self, index: int) -> list[str]:
        """Returns a row of the board."""
        return self.board[index]

    def column_is_full(self, index: int) -> bool:
        """Check if a column is full of pieces"""
        return all([piece != Piece.EMPTY for piece in self.get_column(index=index)])

    def submit_move(self, column: int | None = None):
        """Processes where the piece should go and places it."""

        col = column or self.cursor_position

        if self.column_is_full(index=col):
            return

        # Place piece
        for row in range(self.ROWS - 1, -1, -1):
            if self.board[row][col] == Piece.EMPTY:
                self.board[row][col] = self.labels[self.turn]
                break

        finished, winner = self.check_win()
        if finished:
            return self.end(winner=winner)

        # Bot needs to auto move
        if self.turn.bot:
            options = list(range(self.COLS))
            random.shuffle(options)

            for i in options:
                if self.column_is_full(index=i):
                    continue

                self.submit_move(i)
                break

        finished, winner = self.check_win()
        if finished:
            return self.end(winner=winner)

    def check_win(self) -> tuple[bool, discord.Member | None]:
        """Determine if a player has won and if the game is finished."""
        # horizontal check
        for row in self.board:
            for i in range(len(row) - 3):
                if row[i] != Piece.EMPTY and row[i : i + 4].count(row[i]) == 4:
                    return True, self.players[row[i]]

        # vertical check
        for col in (self.get_column(x) for x in range(self.COLS)):
            for i in range(len(col) - 3):
                if col[i] != Piece.EMPTY and col[i : i + 4].count(col[i]) == 4:
                    return True, self.players[col[i]]

        # ascending diagonal check
        for row in range(3, self.ROWS):  # diagonal asc can only happen >3 rows down
            for col in range(self.COLS - 3):  # diagonal asc not possible in last 3 cols
                group = [
                    self.board[row][col],
                    self.board[row - 1][col + 1],
                    self.board[row - 2][col + 2],
                    self.board[row - 3][col + 3],
                ]
                if group[0] != Piece.EMPTY and group.count(group[0]) == 4:
                    return True, self.players[group[0]]

        # descending diagonal check
        for row in range(
            self.ROWS - 3
        ):  # diagonal desc cannot happen from bottom 3 rows
            for col in range(self.COLS - 3):  # diagonal asc not possible in last 3 cols
                group = [
                    self.board[row][col],
                    self.board[row + 1][col + 1],
                    self.board[row + 2][col + 2],
                    self.board[row + 3][col + 3],
                ]
                if group[0] != Piece.EMPTY and group.count(group[0]) == 4:
                    return True, self.players[group[0]]

        # Game is a tie check
        if self.count_moves(piece=Piece.EMPTY) == 0:
            return True, None

        return False, None

    def end(self, winner: discord.Member | None):
        """Finish the game and disable the buttons."""
        self.title = f"{winner.display_name} Wins!" if winner else "It's a Tie :("
        self.right_button.disabled = True
        self.submit_button.disabled = True
        self.left_button.disabled = True
        self.finished = True

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if len(self.children) > 3:
            return interaction.user in (self.p1, self.p2)
        return interaction.user == self.turn

    @discord.ui.button(emoji="◀️")
    async def left_button_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        """Moves the cursor left."""
        if self.cursor_position == 0:
            self.cursor_position = self.COLS - 1
        else:
            self.cursor_position -= 1

        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(emoji="✅")
    async def submit_button_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        """Submits the move and switches the turn."""

        self.submit_move(self.cursor_position)

        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(emoji="▶️")
    async def right_button_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        """Moves the cursor right."""
        if self.cursor_position >= self.COLS - 1:
            self.cursor_position = 0
        else:
            self.cursor_position += 1

        await interaction.response.edit_message(embed=self.embed, view=self)
