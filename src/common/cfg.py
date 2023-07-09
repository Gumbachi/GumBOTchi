import itertools

import discord
from discord import Activity
from discord import ActivityType as ActType
from discord.enums import Status


class Vip:
    DIDNA = 235902262168256515
    GUM = 128595549975871488
    SALMON = 244574519027564544
    SWEET = 224506294801793025
    BRAIDED = 187273639874396160
    RABBIT = 193517510958514177


class Emoji:
    CHECK = "✅"
    CROSS = "❌"
    WEIRDCHAMP = "<:weirdchamp:891567122285735977>"
    GUH = "<:guh:924116109651746816>"


class Tenor:
    F = "https://tenor.com/view/press-f-pay-respect-coffin-burial-gif-12855021"
    KERMIT_LOST = "https://tenor.com/view/kermit-the-frog-looking-for-directions-navigate-is-lost-gif-11835765"
    HE_BOUGHT = "https://tenor.com/view/bogdanoff-dump-it-stocks-crypto-gif-20477588"
    HE_SOLD = "https://tenor.com/view/bogdanoff-he-sold-pump-it-gif-23606817"
    MY_MAN = "https://tenor.com/view/woody-toy-story-buzz-dab-me-up-dab-up-gif-26395273"


class Role:
    RAINBOW = 853368252474196018


admins = [Vip.GUM, Vip.SALMON, Vip.SWEET]
devguilds = [565257922356051973]

activities = itertools.cycle([
    Activity(name="with your feelings", type=ActType.playing),
    Activity(name="your cries for help", type=ActType.listening),
    Activity(name="Salm's color change", type=ActType.watching),
    Activity(name="18 poggers gifs at once", type=ActType.watching),
    Activity(name="nonstop vibes", type=ActType.listening),
    Activity(name="XPEV's Downfall", type=ActType.watching),
    Activity(name="The Poggers Olympics", type=ActType.competing),
    Activity(name="Derk try to craigslist", type=ActType.watching),
    Activity(name="bangers only", type=ActType.playing),
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