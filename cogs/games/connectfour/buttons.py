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
        if interaction.user != self.game.turn:
            return

        if self.game.cursor_position < 6:
            self.game.cursor_position += 1

        await interaction.response.edit_message(embed=self.game.embed)


class LeftButton(Button):
    def __init__(self, game: 'Game'):
        super().__init__(emoji="◀️")
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.game.turn:
            return

        if self.game.cursor_position > 0:
            self.game.cursor_position -= 1

        await interaction.response.edit_message(embed=self.game.embed)


class SubmitButton(Button):
    def __init__(self, game: 'Game'):
        super().__init__(emoji="✅", style=ButtonStyle.green)
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.game.turn:
            return

        if not self.game.column_is_full(self.game.cursor_position):
            self.game.submit_move()

        await interaction.response.edit_message(embed=self.game.embed, view=self.game.view)


class ResendButton(Button):
    def __init__(self, game: 'Game'):
        super().__init__(emoji="⏬")
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        if interaction.user not in self.game.players:
            return

        new_message = await interaction.channel.send(embed=self.game.embed, view=self.game.view)

        moved_embed = discord.Embed(
            title=f"{interaction.user.nick or interaction.user.name} has moved this game",
            description=f"[Jump]({new_message.jump_url})"
        )

        await interaction.response.edit_message(embed=moved_embed, view=None)
