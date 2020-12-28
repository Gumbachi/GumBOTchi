import os
import re
import json
from pprint import pprint
import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandError
import requests
from common.cfg import bot
import matplotlib.pyplot as plt
from io import BytesIO


class UnknownSymbolError(CommandError):
    """Raise for unknown symbol."""
    pass


class SbonkCommands(commands.Cog):
    """Hold and executes all sbonk commands."""

    def __init__(self, bot):
        self.bot = bot
        self.iexcloud_key = os.getenv("IEXCLOUD_KEY")

    def fetch_stock_data(self, symbol):
        """Fetch stock data from iexcloud based on a symbol given"""
        symbol = symbol.upper()

        # Request quote from iex cloud
        response = requests.get(
            f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={self.iexcloud_key}")
        content = response.content.decode("utf-8")

        # process unknown symbol
        if content == "Unknown symbol":
            return None

        data = json.loads(content)  # api response in dict form

        # Make change data presentable
        change = round(data["change"], 2)
        change_symbol = "⬆️ " if change >= 0 else "⬇️ "
        change_symbol += f"{change:.2f}"
        change_percent = round(data["changePercent"]*100, 2)
        is_guh = change_percent <= -5
        is_moon = not is_guh and change_percent >= 5

        # generate and send sbonk embed
        sbonk_embed = discord.Embed(
            title=f"{symbol}: ${data['latestPrice']}",
            description=f"{change_symbol} ({change_percent}%)",
            color=discord.Color.green() if change >= 0 else discord.Color.red()
        )
        sbonk_embed.set_footer(text=data["latestTime"])

        # check if guh or moonS
        if is_guh:
            sbonk_embed.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/755546594446671963.png?v=1")
        elif is_moon:
            sbonk_embed.set_thumbnail(
                url="https://melmagazine.com/wp-content/uploads/2019/07/Screen-Shot-2019-07-31-at-5.47.12-PM.png")

        return sbonk_embed

    def create_graph(self, symbol):
        """Create a graph based on stock intraday prices and return as an image."""
        average_list, label_list = list(), list()

        response = requests.get(f"https://cloud.iexapis.com/stable/stock/{symbol}/intraday-prices/quote?token={self.iexcloud_key}")
        content = json.loads((response.content.decode("utf-8")))

        for i, x in enumerate(content):
            if (x['average']):
                average_list.append(x['average'])
            elif (average_list[-1]) and content[i+1]['average']:
                next = content[i+1]['average']
                prev = average_list[-1]
                average_list.append((next + prev)/2)
            else:
                j = i + 1
                prev = average_list[-1]
                while not content[j]['average']:
                    j += 1
                m = (content[j]['average'] - prev) / j
                next = m * j + prev
                average_list.append((next + prev)/2)

        plt.clf()
        plt.plot(label_list, average_list)
        plt.xticks([])

        ax = plt.axes()
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer = buffer.getvalue()
        buffer = BytesIO(buffer)

        return buffer

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listens for sbonks"""

        # ignore the bot user
        if message.author.id == bot.user.id:
            return

        # sort out symbols from message
        text = message.content + " "
        pattern = r"[$][a-zA-Z]{1,4}[^a-zA-Z]"
        prefixed_symbols = re.findall(pattern, text)

        # strip $ and 1 character off the strings
        symbols = [s[1:-1] for s in prefixed_symbols]

        for symbol in symbols:
            embed = self.fetch_stock_data(symbol)

            # Send weirdchamp if unrecognized symbol
            if not embed:
                weirdchamp = bot.get_emoji(746570904032772238)
                await message.channel.send(str(weirdchamp))
            else:
                graph = self.create_graph(symbol)
                file = discord.File(graph, filename=f"{symbol.upper()}.png")
                await message.channel.send(embed=embed)  # send sbonk embed
                await message.channel.send(file=file)


def setup(bot):
    bot.add_cog(SbonkCommands(bot))
