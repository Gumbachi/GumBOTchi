from enum import Enum


class Move:
    def __init__(self, type, emoji):
        self.type = type
        self.emoji = emoji

    def __str__(self):
        return self.emoji

    def __gt__(self, other):
        if self.type == "Rock" and other.type == "Scissors":
            return True
        if self.type == "Paper" and other.type == "Rock":
            return True
        if self.type == "Scissors" and other.type == "Paper":
            return True
        return False


class RPSMove():
    ROCK = Move("Rock", "🪨")
    PAPER = Move("Paper", "🧻")
    SCISSORS = Move("Scissors", "✂️")


class RPSState(Enum):
    ONGOING = 0
    PLAYERONEWIN = 1
    PLAYERTWOWIN = 2
    TIE = 3
