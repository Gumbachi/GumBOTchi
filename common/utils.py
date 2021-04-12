"""Helper functions."""
import io
import discord
from common.cfg import bot


def emojify(emoji_id):
    """Sends a custom emoji given an int id."""
    return str(bot.get_emoji(emoji_id))


def image_to_file(img, name="image"):
    # Convert PIL Image to discord File
    img = img.copy()
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer = buffer.getvalue()
    img = io.BytesIO(buffer)
    return discord.File(img, filename=f"{name}.png")
