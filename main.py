"""Runs the discord bot"""
import os
from pathlib import Path
from common.cfg import bot


@bot.listen()
async def on_ready():
    """Bot is now ready to rumble."""
    print("Ready to go")

# .py files to load up
cogs = [
    "cogs.general",
    # "cogs.music.music",
    # "cogs.pog",
    # "cogs.roast",
    # "cogs.sbonks",
    # "cogs.games.rps.rps",
    "cogs.games.tictactoe.tictactoe"
]

if __name__ == '__main__':
    for cog in cogs:
        try:
            bot.load_extension(cog)
            print(f"LOADED: {cog}")

        except Exception as e:
            print(f"Couldnt load {cog} because {e}")

bot.run(os.getenv("TOKEN"))  # runs the bot
