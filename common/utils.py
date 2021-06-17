"""Helper functions."""
import io
import discord
from common.cfg import bot


def weirdchamp():
    """U know what it does"""
    return str(bot.get_emoji(655466727441956865))


def image_to_file(img, name="image"):
    # Convert PIL Image to discord File
    img = img.copy()
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer = buffer.getvalue()
    img = io.BytesIO(buffer)
    return discord.File(img, filename=f"{name}.png")
