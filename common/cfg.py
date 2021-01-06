from discord.ext import commands

extensions = [
    "cogs.general",
    "cogs.sbonks",
    "cogs.error_handler",
    "cogs.admin"
]


def get_prefix(bot, message):
    """Gets the prefix per server"""
    # fill in logic for prefix changing if you want
    return '!'


bot = commands.Bot(command_prefix=get_prefix,
                   help_command=None)  # creates bot object

admin_ids = {
    128595549975871488,  # Gumbachi#0506
    187273639874396160,  # BraidedAxe#1818
    244574519027564544  # SoloMan98#3426
}

poggers_prefixes = {"pog", "pong", "pawg", "cog"}

poggers_activation_phrases = {
    "pog", "poggers", "poggies",
    "pogchamp", "pongas", "pogchampius",
    "poggas", "pongies", "pogeroni",
    "pogu", "pogey", "poggaroo",
    "pogger", "pogchampo", "poggiewoggies",
    "pogchampion", "coggers", "poggie",
    "pongerino", "pogerino", "pogging",
    "poggeurs", "pawg"
}

poggers_links = [
    "https://tenor.com/view/anime-poggers-anime-poggers-anime-gif-18290521",
    "https://tenor.com/view/anime-poggers-anime-poggers-anime-gif-18290518",
    "https://tenor.com/view/poggers-gif-18334778",
    "https://tenor.com/view/poggers-kiss-anime-kiss-honey-gif-18097318",
    "https://tenor.com/view/anime-poggers-sound-of-poggers-poggers-anime-yuru-yuri-gif-18409324",
    "https://tenor.com/view/poggers-anime-girls-kissing-pog-gif-18050577",
    "https://tenor.com/view/sound-of-poggers-poggers-anime-anime-poggers-charr-gif-18348699",
    "https://tenor.com/view/poggers-pog-pogchamp-anime-illya-gif-18054845",
    "https://tenor.com/view/poggers-based-lesbian-anime-gif-18956362",
    "https://tenor.com/view/poggers-gif-18334779",
    "https://tenor.com/view/poggers-anime-girls-mako-anime-girls-kiss-kiss-gif-17206802",
    "https://tenor.com/view/anime-poggers-anime-poggers-anime-gif-18290513",
    "https://tenor.com/view/poggers-anime-anime-poggers-poggers-anime-gif-18386348",
    "https://tenor.com/view/poggers-anime-kiss-girl-gif-18969493",
    "https://tenor.com/view/anime-poggers-anime-poggers-anime-gif-18290523"
]
