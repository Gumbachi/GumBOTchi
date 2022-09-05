"""Runs the discord bot"""
import os

import discord

# Create bot based on environment
if os.getenv("ENV") == "testing":
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
async def on_ready():
    """Bot is now ready to rumble."""
    print("Ready to go")

# .py files to load up
cogs = [
    "cogs.general",
    "cogs.music.music",
    "cogs.pog",
    "cogs.roast",
    "cogs.sbonks.sbonks",
    "cogs.games.rps.rps",
    "cogs.games.tictactoe.tictactoe",
    "cogs.games.connectfour.connectfour",
    "cogs.craigslister.craigslister",
    "cogs.emojifier.emojifier",
    "cogs.soundboard.soundboard",
    "cogs.polls.polls",
]

if __name__ == '__main__':
    bot.load_extensions(*cogs)

bot.run(os.getenv("TOKEN"))  # runs the bot
