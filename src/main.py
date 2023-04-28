"""Runs the discord bot"""
import os

import uvicorn
import discord
import multiprocessing

from dotenv import load_dotenv
from cogs.claire.api.server import app

load_dotenv()

# Create bot based on environment
if os.getenv("DEBUG", None) is not None:
    print("DEBUG ENVIRONMENT")
    bot = discord.Bot(
        owner_id=128595549975871488,
        intents=discord.Intents.all(),
        debug_guilds=[565257922356051973]
    )
else:
    print("LIVE ENVIRONMENT")
    bot = discord.Bot(
        owner_id=128595549975871488,
        intents=discord.Intents.all(),
    )


@bot.listen()
async def on_ready() -> None:
    """Bot is now ready to rumble."""
    print("Ready to go")

# .py files to load up
cogs = [
    "cogs.general.general",
    "cogs.pog.pog",
    "cogs.roast.roast",
    "cogs.sbonks.sbonks",
    "cogs.games.rps.rps",
    "cogs.games.tictactoe.tictactoe",
    "cogs.games.connectfour.connectfour",
    "cogs.emojifier.emojifier",
    "cogs.polls.polls",
    "cogs.music.music",
    "cogs.soundboard.soundboard",
    "cogs.claire.claire",
]


def run_bot():
    bot.load_extensions(*cogs)
    bot.run(os.getenv("TOKEN"))  # runs the bot

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=80)

if __name__ == '__main__':
    bot_process = multiprocessing.Process(target=run_bot)
    server_process = multiprocessing.Process(target=run_server)

    bot_process.start()
    server_process.start()