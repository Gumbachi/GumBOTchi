from enum import Enum


class RPSMove(Enum):
    ROCK = "Rock"
    PAPER = "Paper"
    SCISSORS = "Scissors"


class RPSState(Enum):
    ONGOING = 0
    PLAYERONEWIN = 1
    PLAYERTWOWIN = 2
    TIE = 3
