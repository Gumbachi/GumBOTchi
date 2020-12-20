"""Runs the discord bot"""
import os

import discord

from cfg import bot, extensions


@bot.event
async def on_ready():
    """Change presence and report ready."""
    activity = discord.Game(name=f"with your feelings")
    await bot.change_presence(activity=activity)
    print("Ready to go")


@bot.event
async def on_message(message):
    """Message listener."""
    # make sure it doesnt run when bot writes message
    if message.author == bot.user:
        return

    # shows prefix if bot is mentioned
    if message.mentions and message.mentions[0].id == bot.user.id:
        await message.channel.send(f"Type `{bot.command_prefix}`help for help.")

    await bot.process_commands(message)

########### PUT EXTRA EVENT REFERENCES HERE ###########
# https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#event-reference

# loads extensions(cogs) listed in vars.py
if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f"Couldnt load {extension}")
            print(e)

bot.run(os.getenv("TOKEN"))  # runs the bot
