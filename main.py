"""Runs the discord bot"""
import os
import discord

# Create the bot
bot = discord.Bot(
    description="Multi-purpose chadbot",
    activity=discord.Activity(
        name="Just Woke Up",
        type=discord.ActivityType.playing
    ),
    status=discord.Status.dnd,
    owner_id=128595549975871488,
    # debug_guilds=[565257922356051973],  # uncomment this line when testing
    intents=discord.Intents.all()
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
    "cogs.soundboard.soundboard"
]

if __name__ == '__main__':
    for cog in cogs:
        try:
            bot.load_extension(cog)
            print(f"LOADED: {cog}")

        except Exception as e:
            print(f"Couldnt load {cog} because {e}")

bot.run(os.getenv("TOKEN"))  # runs the bot
