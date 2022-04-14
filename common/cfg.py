import itertools
import discord
from discord import Activity
from discord.enums import Status
from discord import ActivityType as ActType

# Create the bot
bot = discord.Bot(
    description="Multi-purpose chadbot",
    activity=Activity(name="Just Woke Up", type=ActType.playing),
    status=Status.dnd,
    owner_id=128595549975871488,
    intents=discord.Intents.all()
)


class Vip():
    DIDNA = 235902262168256515
    GUM = 128595549975871488
    SALMON = 244574519027564544
    SWEET = 224506294801793025
    BRAIDED = 187273639874396160
    RABBIT = 193517510958514177


class Emoji():
    CHECK = "✅"
    CROSS = "❌"
    WEIRDCHAMP = "<:weirdchamp:891567122285735977>"
    GUH = "<:guh:924116109651746816>"


class Tenor():
    F = "https://tenor.com/view/press-f-pay-respect-coffin-burial-gif-12855021"
    KERMIT_LOST = "https://tenor.com/view/kermit-the-frog-looking-for-directions-navigate-is-lost-gif-11835765"
    HE_BOUGHT = "https://tenor.com/view/bogdanoff-dump-it-stocks-crypto-gif-20477588"
    HE_SOLD = "https://tenor.com/view/bogdanoff-he-sold-pump-it-gif-23606817"


class Role():
    RAINBOW = 853368252474196018


admins = [Vip.GUM, Vip.SALMON, Vip.SWEET]
devguilds = [565257922356051973]

activities = itertools.cycle([
    Activity(name="with your feelings", type=ActType.playing),
    Activity(name="your cries for help", type=ActType.listening),
    Activity(name="Salm's color change", type=ActType.watching),
    Activity(name="18 poggers gifs at once", type=ActType.watching),
    Activity(name="XPEV's Downfall", type=ActType.watching),
    Activity(name="The Poggers Olympics", type=ActType.competing),
    Activity(name="Derk try to craigslist", type=ActType.watching),
    Activity(name="Salmon kill the economy", type=ActType.watching),
    Activity(name="Roses 50 times in one day", type=ActType.listening),
    Activity(name="hard to get", type=ActType.playing),
    Activity(name="my weight", type=ActType.watching),
    Activity(name="THREES?!?!?!", type=ActType.playing),
    Activity(name="for LGMA Esports", type=ActType.playing),
    Activity(name="4D Quantum Chess", type=ActType.playing),
])

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
    "pogflip"
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
