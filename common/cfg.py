import itertools
import discord
from discord.ext import commands
import common.database as db
from discord import ActivityType

extensions = [
    "cogs.general",
    "cogs.sbonks",
    "cogs.admin",
    "cogs.errors",
    "cogs.catalog",
    "cogs.craigslister",
    "cogs.games.mafia",
    "cogs.roast",
    "cogs.games.hangman",
    "cogs.music"
]


def get_prefix(bot, message):
    """Gets the prefix per server"""
    try:
        return db.guildget(message.guild.id, "prefix")
    except AttributeError:
        return "!"  # default


bot = commands.Bot(
    command_prefix=get_prefix, help_command=None, intents=discord.Intents.all()
)  # creates bot object

# GLOBAL DATA

# Gumbachi#0506  # SoloMan98#3426
admin_ids = {128595549975871488, 244574519027564544}

emojis = {
    "checkmark": "✅",
    "crossmark": "❌",
    "left_arrow": "⬅️",
    "right_arrow": "➡️",
    "home_arrow": "↩️",
    "double_down": "⏬",
    "updown_arrow": "↕️",
}

song_queues = {}

catalogs = {}
builders = {}
supermuted_users = set()

# Activities/status include (watching, playing, listening)
activities = itertools.cycle(
    [
        discord.Activity(name="with your feelings", type=ActivityType.playing),
        discord.Activity(name="your cries for help",
                         type=ActivityType.listening),
        discord.Activity(name="Salm's color change",
                         type=ActivityType.watching),
        discord.Activity(name="18 poggers gifs at once",
                         type=ActivityType.watching),
        discord.Activity(name="XPEV's Downfall", type=ActivityType.watching),
        discord.Activity(name="The Poggers Olympics",
                         type=ActivityType.competing),
        discord.Activity(
            name="Derk struggle with craigslisting", type=ActivityType.watching
        ),
        discord.Activity(name="Salmon kill the economy",
                         type=ActivityType.watching),
        discord.Activity(name="Roses 50 times in one day",
                         type=ActivityType.listening),
        discord.Activity(name="hard to get", type=ActivityType.playing),
        discord.Activity(name="my weight", type=ActivityType.watching),
        discord.Activity(name="THREES?!?!?!", type=ActivityType.playing),
        discord.Activity(name="for LGMA Esports", type=ActivityType.playing),
    ]
)

poggers_activation_phrases = {
    "pog",
    "poggers",
    "poggies",
    "pogchamp",
    "pongas",
    "pogchampius",
    "poggas",
    "pongies",
    "pogeroni",
    "pogu",
    "pogey",
    "poggaroo",
    "pogger",
    "pogchampo",
    "poggiewoggies",
    "pogchampion",
    "coggers",
    "poggie",
    "pongerino",
    "pogerino",
    "pogging",
    "poggeurs",
    "pawg",
    "pognut",
    "ponginos",
    "piggas",
    "ponggers",
    "poggiewoggie",
    "pogaroni",
    "pogaroni and cheese",
    "pogeroni and cheese",
    "pogflip",
    "poggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggers",
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
    "https://tenor.com/view/anime-poggers-anime-poggers-anime-gif-18290523",
    "https://tenor.com/view/pog-poggers-pogchamp-pogchamps-pogger-gif-18414191",
    "https://tenor.com/view/poggers-anime-gif-19842013",
    "https://tenor.com/view/marnie-pokemon-anime-pog-pogchamp-gif-19642089",
    "https://tenor.com/view/poggers-gif-19466277",
    "https://tenor.com/view/genshin-poggers-ningguang-cringe-anime-gif-18890744",
    "https://tenor.com/view/genshin-lumine-poggers-gif-18795348",
    "https://tenor.com/view/amber-poggers-genshin-impact-gif-18732929",
]

spam_words = [
    'Smartphones', 'iPhone', 'Samsung', 'LG', 'Android', 'Laptops',
    'Video Games', 'Drones', 'Speakers', 'Cameras',
    'Music Equipment', 'Headsets', 'Airpods', 'https://gameboxhero.com'
    'Top Buyer', 'Quote', 'Sprint', 'ATT', 'Verizon', 'TMobile',
]
