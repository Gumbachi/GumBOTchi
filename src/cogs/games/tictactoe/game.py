import random
from collections.abc import Sequence

import discord


class TicTacToeButton(discord.ui.Button):

    view: "Game"  # Tell intellisense View is a game obj

    def __init__(self, index: int):
        super().__init__(label="\u200b", row=index // 3)
        self.index = index
        self.owner = None

    def reset(self):
        """Reset the data the button holds."""
        self.disabled = False
        self.style = discord.ButtonStyle.gray
        self.label = "\u200b"

    async def callback(self, interaction: discord.Interaction):
        self.owner = interaction.user
        self.label = self.view.labels[interaction.user]

        winner = self.view.checkwin()

        # Bot Auto Move
        if not winner and self.view.p2.bot:
            unused_moves = [b.index for b in self.view.children if not b.owner]
            if unused_moves:
                choice = random.choice(unused_moves)
                self.view.children[choice].owner = self.view.p2
                self.view.children[choice].label = self.view.labels[self.view.p2]

                winner = self.view.checkwin()

        await interaction.response.edit_message(embed=self.view.embed, view=self.view)


# class RematchButton(discord.ui.Button):

#     view: "Game"  # Tell intellisense View is a game obj

#     def __init__(self):
#         super().__init__(label="Rematch", style=discord.ButtonStyle.blurple, row=3)

#     async def callback(self, interaction: discord.Interaction):

#         print("Entering Callback")

#         for button in self.view.children[:-1]:
#             button.reset()

#         self.view.headline = f"{self.view.p1.display_name} VS {self.view.p2.display_name}"
#         # self.view.remove_item(self.view.children[-1])

#         print("here")

#         await interaction.response.edit_message(embed=self.view.embed, view=self.view)


class Game(discord.ui.View):

    children: list["TicTacToeButton"]

    def __init__(self, p1: discord.Member, p2: discord.Member):
        self.p1 = p1
        self.p2 = p2
        self.headline = f"{p1.display_name} VS {p2.display_name}"
        self.labels = {p1: "X", p2: "O"}
        self.score = [0, 0]

        super().__init__(*[TicTacToeButton(i) for i in range(9)])

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only allow the player whose turn it is"""
        return interaction.user == self.turn

    @property
    def turn(self) -> discord.Member:
        """Calculate who's turn it is."""
        moves = [0 for b in self.children if isinstance(b, TicTacToeButton) and b.owner].count(0)
        return self.p2 if moves % 2 else self.p1

    @property
    def embed(self):
        return discord.Embed(
            title=f"{self.headline} • {self.score[0]} - {self.score[1]}",
            description=f"{self.turn.display_name}'s Turn",
            color=discord.Color.blue()
        )

    def checkwin(self) -> discord.Member | None:
        """Checks to see if there is a winner. Sets winner and highlights path as needed."""
        p1_moves = {b.index for b in self.children if b.owner == self.p1}
        p2_moves = {b.index for b in self.children if b.owner == self.p2}
        all_moves = p1_moves.union(p2_moves)

        index_sets = [
            {0, 1, 2}, {3, 4, 5}, {6, 7, 8},  # Horizontal
            {0, 3, 6}, {1, 4, 7}, {2, 4, 8},  # Vertical
            {0, 4, 8}, {2, 4, 6}  # Diagonal
        ]

        for iset in index_sets:
            if iset.issubset(p1_moves):
                self.highlight(iset)
                self.end(winner=self.p1)
                return self.p1

            if iset.issubset(p2_moves):
                self.highlight(iset)
                self.end(winner=self.p2)
                return self.p2

        if len(all_moves) == 9:
            self.highlight(all_moves, discord.ButtonStyle.red)
            self.end(winner=None)
            return

    def highlight(
        self, indexes: Sequence[int],
        style: discord.ButtonStyle = discord.ButtonStyle.green
    ):
        """Change the style of the buttons based on index."""
        for i in indexes:
            self.children[i].style = style

    def end(self, winner: discord.Member | None):
        """Wrap up the game and disabled all of the buttons."""
        match winner:
            case self.p1:
                self.headline = f"{self.p1.display_name} Wins!"
                self.score[0] += 1
            case self.p2:
                self.headline = f"{self.p2.display_name} Wins!"
                self.score[1] += 1
            case None:
                self.headline = "It's a Tie :("

        for button in self.children:
            button.disabled = True

        # self.add_item(RematchButton())
