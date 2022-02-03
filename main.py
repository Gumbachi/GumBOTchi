"""Runs the discord bot"""
import os
from pathlib import Path
from common.cfg import bot


@bot.listen()
async def on_ready():
    """Bot is now ready to rumble."""
    print("Ready to go")

# load extensions from the cogs dir
if __name__ == '__main__':

    for ext in Path("./cogs").glob("**/*.py"):
        try:
            # parse string to correct format
            ext = str(ext).replace("/", ".").replace("\\", ".")
            ext = ext[:-3]  # trim .py extension
            bot.load_extension(ext)
            print(f"LOADED: {ext}")

        except Exception as e:
            print(f"Couldnt load {ext} because {e}")

bot.run(os.getenv("TOKEN"))  # runs the bot
