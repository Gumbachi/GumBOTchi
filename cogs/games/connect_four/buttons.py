"""Module holds buttons for connect four."""
import discord
from discord.enums import ButtonStyle
from discord.ui import Button


class Emoji:
    RIGHT = "▶️"
    LEFT = "◀️"
    BIGLEFT = "⏪"
    BIGRIGHT = "⏩"
    SUBMIT = "✅"


class RightButton(Button):
    def __init__(self, game):
        super().__init__(emoji=Emoji.RIGHT, style=ButtonStyle.gray)
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        if self.game.cursor_position == 6:
            return
        self.game.cursor_position += 1
        await interaction.response.edit_message(embed=self.game.embed)


class LeftButton(Button):
    def __init__(self, game):
        super().__init__(emoji=Emoji.LEFT, style=ButtonStyle.gray)
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        if self.game.cursor_position == 0:
            return
        self.game.cursor_position -= 1
        await interaction.response.edit_message(embed=self.game.embed)


class BigRightButton(Button):
    def __init__(self, game):
        super().__init__(emoji=Emoji.BIGRIGHT, style=ButtonStyle.gray)
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        if self.game.cursor_position == 6:
            return
        self.game.cursor_position = 6
        await interaction.response.edit_message(embed=self.game.embed)


class BigLeftButton(Button):
    def __init__(self, game):
        super().__init__(emoji=Emoji.BIGLEFT, style=ButtonStyle.gray)
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        if self.game.cursor_position == 0:
            return
        self.game.cursor_position = 0
        await interaction.response.edit_message(embed=self.game.embed)


class SubmitButton(Button):
    def __init__(self, game):
        super().__init__(emoji=Emoji.SUBMIT, style=ButtonStyle.green)
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        # Check if move is legal
        if all(self.game.get_column(self.game.cursor_position)):
            return

        self.game.submit_move()

        self.game.check_win()

        self.game.swap_turn()

        await interaction.response.edit_message(embed=self.game.embed)
