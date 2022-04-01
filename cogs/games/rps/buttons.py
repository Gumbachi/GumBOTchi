import discord

from cogs.games.rps.enums import RPSMove


class RockButton(discord.ui.Button):
    def __init__(self, game):
        """Plays Rock"""
        super().__init__(emoji="🪨")
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        if interaction.user not in self.game.players:
            return

        # Set the player choice to rock
        if self.game.p1 == interaction.user:
            self.game.p1.choice = RPSMove.ROCK
        else:
            self.game.p2.choice = RPSMove.ROCK

        self.game.check_win()
        await interaction.response.edit_message(embed=self.game.embed, view=self.game.view)


class PaperButton(discord.ui.Button):
    def __init__(self, game):
        """Play Paper"""
        super().__init__(emoji="🧻")
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        if interaction.user not in self.game.players:
            return

        # Set the player choice to paper
        if self.game.p1 == interaction.user:
            self.game.p1.choice = RPSMove.PAPER
        else:
            self.game.p2.choice = RPSMove.PAPER

        self.game.check_win()
        await interaction.response.edit_message(embed=self.game.embed, view=self.game.view)


class ScissorButton(discord.ui.Button):
    def __init__(self, game):
        """Play Scissors"""
        super().__init__(emoji="✂️")
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        if interaction.user not in self.game.players:
            return

        # Set the player choice to scissors
        if self.game.p1 == interaction.user:
            self.game.p1.choice = RPSMove.SCISSORS
        else:
            self.game.p2.choice = RPSMove.SCISSORS

        self.game.check_win()
        await interaction.response.edit_message(embed=self.game.embed, view=self.game.view)
