"""Helper functions."""
from common.cfg import bot
import random
from datetime import timedelta
import time


def weirdchamp():
    """U know what it does"""
    return str(bot.get_emoji(655466727441956865))


def mock(text):
    letters = list(text)
    updated_text = []
    for letter in letters:
        num = random.randint(0, 1)
        if num == 1:
            updated_text.append(letter.upper())
        else:
            updated_text.append(letter.lower())
    return "".join(updated_text)


def normalize_time(seconds):
    """Turns seconds into H:M:S"""
    if seconds < 3600:
        return time.strftime("%M:%S", time.gmtime(seconds))
    else:
        return time.strftime("%H:%M:%S", time.gmtime(seconds))
