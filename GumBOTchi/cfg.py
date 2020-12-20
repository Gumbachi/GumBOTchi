from discord.ext import commands

extensions = [
    "cogs.general"
]


def get_prefix(bot, message):
    """Gets the prefix per server"""
    # fill in logic for prefix changing if you want
    return '!'


bot = commands.Bot(command_prefix=get_prefix,
                   help_command=None)  # creates bot object
