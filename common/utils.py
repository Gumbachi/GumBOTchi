"""Helper functions."""
from common.cfg import bot


def emojify(emoji_id):
    """Sends a custom emoji given an int id."""
    return str(bot.get_emoji(emoji_id))