"""Module holds buttons for connect four."""
import discord
from discord.enums import ButtonStyle
from discord.ui import Button

# This is here for typing to avoid cyclic import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cogs.games.connectfour.game import Game


class RightButton(Button):
    def __init__(self, game: 'Game'):
        super().__init__(emoji="▶️")
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        if self.game.cursor_position == 6:
            return
        self.game.cursor_position += 1
        await interaction.response.edit_message(embed=self.game.embed)


class LeftButton(Button):
    def __init__(self, game: 'Game'):
        super().__init__(emoji="◀️")
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        if self.game.cursor_position == 0:
            return
        self.game.cursor_position -= 1
        await interaction.response.edit_message(embed=self.game.embed)


class SubmitButton(Button):
    def __init__(self, game: 'Game'):
        super().__init__(emoji="✅", style=ButtonStyle.green)
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        # Check if move is legal
        if all(self.game.column(self.game.cursor_position)):
            return

        self.game.submit_move()

        await interaction.response.edit_message(embed=self.game.embed, view=self.game.view)
