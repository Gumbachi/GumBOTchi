"""Runs the discord bot"""
import os
from pathlib import Path
from common.cfg import bot


@bot.listen()
async def on_ready():
    """Bot is now ready to rumble."""
    print("Ready to go")

# .py files in cogs that are not cogs
ignored = [
    "cogs.music.buttons",
    "cogs.music.player",
    "cogs.music.song"
]

if __name__ == '__main__':
    # find all .py files in ./cogs
    for ext in Path("./cogs").glob("**/*.py"):
        try:
            # extensions must be in cogs.general format
            ext = str(ext).replace("/", ".").replace("\\", ".")
            ext = ext[:-3]  # trim .py extension

            # skip ignored extensions
            if ext in ignored:
                continue

            bot.load_extension(ext)
            print(f"LOADED: {ext}")

        except Exception as e:
            print(f"Couldnt load {ext} because {e}")

bot.run(os.getenv("TOKEN"))  # runs the bot
