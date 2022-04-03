import random
import discord
from typing import Optional

from cogs.games.rps.enums import Move, RPSMove


class Player:
    def __init__(self, user: discord.Member):
        self.user = user
        self.choice: Optional[Move] = None

        # Set default if bot is playing
        if self.user.bot:
            self.choice = random.choice([
                RPSMove.ROCK,
                RPSMove.PAPER,
                RPSMove.SCISSORS
            ])

    def __str__(self):
        return self.user.nick or self.user.name

    def __eq__(self, other):
        return self.user.id == other.id

    @property
    def move(self):
        return self.choice
