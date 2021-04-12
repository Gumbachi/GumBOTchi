"""Runs the discord bot"""
import os

import discord

from cogs.craigslister import Craigslister
from common.cfg import bot, extensions, get_prefix, supermuted_users
import common.cfg as cfg


@bot.event
async def on_ready():
    """Change presence and report ready."""
    await bot.change_presence(activity=next(cfg.activities))
    print("Ready to go")

@bot.event
async def on_message(message):
    """Message listener."""
    # make sure it doesnt run when bot writes message
    if message.author == bot.user:
        return

    # shows prefix if bot is mentioned
    if message.mentions and message.mentions[0].id == bot.user.id:
        await message.channel.send(f"Type `{get_prefix(bot, message)}`help for help.")

    if message.author.id in supermuted_users:
        return await message.delete()

    await bot.process_commands(message)

# loads extensions(cogs) listed in vars.py
if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f"Couldnt load {extension}")
            print(e)

bot.run(os.getenv("TOKEN"))  # runs the bot
