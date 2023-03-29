"""Runs the discord bot"""
import os

import discord

# Create bot based on environment
if os.getenv("ENV") == "testing":
    bot = discord.Bot(
        owner_id=128595549975871488,
        intents=discord.Intents.all(),
        debug_guilds=[565257922356051973]
    )
else:
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
    "cogs.craigslister.claire",
    "cogs.emojifier.emojifier",
    "cogs.soundboard.soundboard",
    "cogs.polls.polls",
]

if __name__ == '__main__':
    for cog in cogs:
        try:
            bot.load_extension(cog)
            print(f"LOADED: {cog.split('.')[-1]}")

        except Exception as e:
            print(f"Couldnt load {cog} because {e}")

bot.run(os.getenv("TOKEN"))  # runs the bot
