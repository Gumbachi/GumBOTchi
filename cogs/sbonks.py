from json.decoder import JSONDecodeError
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
import numpy as np
from io import BytesIO


class SbonkError(CommandError):
    """Raise for unknown symbol."""
    pass


class RequestError(CommandError):
    """Error for handling api request errors"""
    pass


class SbonkCommands(commands.Cog):
    """Hold and executes all sbonk commands."""

    def __init__(self, bot):
        self.bot = bot
        self.iexcloud_key = os.getenv("IEXCLOUD_KEY")

    def get_stock_data(self, symbols):
        """A more refined stock quote function."""

        print(','.join(symbols))
        # Request stock quotes from iex cloud
        request = f"https://cloud.iexapis.com/stable/stock/market/batch?types=quote,intraday-prices&symbols={','.join(symbols)}&displayPercent=true&token={self.iexcloud_key}"
        response = requests.get(request)

        try:
            return json.loads(response.content)
        except JSONDecodeError:
            return {}

    @ staticmethod
    def draw_symbol_chart(symbol_data):
        """
        Draw image for ONE symbol and return image
        Args:
            symbol_data(dict): dict must contain "intraday-prices" and "quote"
        """
        quote = symbol_data["quote"]

        # remove null datapoints from averages for continuous graph
        average_list = [x["average"] if x["average"] else 0
                        for x in symbol_data["intraday-prices"]]
        graph_x = 390 - average_list.count(0)  # dont include null data points
        average_list = list(filter((0).__ne__, average_list))

        color = "lime" if quote["latestPrice"] >= quote["previousClose"] else "red"

        # plot graph
        plt.clf()

        # market hours
        if not quote["isUSMarketOpen"]:
            plt.style.use('dark_background')

        plt.xlim((0, graph_x))
        plt.plot(list(range(graph_x)), average_list, color=color)
        plt.hlines(quote["previousClose"], 0, graph_x,
                   colors="grey", linestyles="dotted")

        # remove extraneous lines
        plt.xticks([])
        plt.yticks([])
        ax = plt.axes()
        for side in ("left", "right", "top", "bottom"):
            ax.spines[side].set_visible(False)

        # add Symbol and price text
        color = "black" if quote["isUSMarketOpen"] else "white"
        price = quote["extendedPrice"] if quote["extendedPrice"] else quote["latestPrice"]
        text = f"{quote['symbol']} ${price:.2f}"
        plt.text(0, 1.1, text, alpha=0.7, va="bottom", ha="left",
                 size=30, c=color, transform=ax.transAxes)

        # add change text
        change_emoji = "⬆️" if quote["change"] >= 0 else "⬇️"
        change_text = f"{change_emoji}{abs(quote['change']):.2f} ({quote['changePercent']:.2f}%)"
        color = "lime" if quote["change"] >= 0 else "red"
        plt.text(0, 1, change_text, va="bottom", ha="left",
                 size=20, c=color, transform=ax.transAxes)

        # convert the chart to a bytes object Discord can read
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
        buffer = buffer.getvalue()
        return BytesIO(buffer)

    def create_graph(self, symbol):
        """Create a graph based on stock intraday prices and return as an image."""

        # Get previous day's closing price
        def get_previous_close(self, symbol):
            response = requests.get(
                f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={self.iexcloud_key}")
            content = json.loads((response.content.decode("utf-8")))
            return content["previousClose"]

        average_list, label_list = list(), list()
        previous_close = get_previous_close(self, symbol)

        # get list of intraday prices from iex cloud
        response = requests.get(
            f"https://cloud.iexapis.com/stable/stock/{symbol}/intraday-prices/quote?token={self.iexcloud_key}")
        content = json.loads((response.content.decode("utf-8")))

        # Iterate through iex cloud data, populate lists for prices and times
        for i, x in enumerate(content):
            try:
                if x['average']:
                    average_list.append(x['average'])
                # If there is no average for a time, average the previous and next
                # averages
                elif average_list[-1] and content[i+1]['average']:
                    next = content[i+1]['average']
                    prev = average_list[-1]
                    average_list.append((next + prev)/2)
                # if, the next point also does not have an average, keep looking
                # until a plot point is found, then do a regression to find the
                # current average
                else:
                    j = i + 1
                    prev = average_list[-1]
                    while not content[j]['average']:
                        j += 1
                    m = (content[j]['average'] - prev) / j
                    next = m * j + prev
                    average_list.append((next + prev)/2)
                label_list.append(x['label'])
            except IndexError:
                pass

        # color the line red if the stock is down, green if it's up
        color = "green" if previous_close - average_list[-1] < 0 else "red"

        # draw the chart
        plt.clf()
        plt.style.use('dark_background')
        plt.xlim([0, 390])
        plt.plot(label_list, average_list, color=color)
        plt.hlines(previous_close, 0, 390, colors='grey', linestyles="dotted")
        plt.xticks([])
        plt.yticks([])

        ax = plt.axes()
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)

        # convert the chart to a bytes object Discord can read
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=72)
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

        data = self.get_stock_data(symbols)
        pprint(data.keys())
        for symbol in symbols:
            symbol = symbol.upper()
            # weirdchamp for unknown symbol
            if symbol not in data.keys():
                weirdchamp = bot.get_emoji(746570904032772238)
                await message.channel.send(str(weirdchamp))
                continue

            # Send chart
            chart = SbonkCommands.draw_symbol_chart(data[symbol])
            file = discord.File(chart, filename=f"{symbol}.png")
            await message.channel.send(file=file)  # send stock chart


def setup(bot):
    bot.add_cog(SbonkCommands(bot))
