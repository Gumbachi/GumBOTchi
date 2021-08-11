import io
import json
import os
import re

import common.cfg as cfg
import common.utils as utils
import discord
import matplotlib.pyplot as plt
import numpy as np
import requests
from discord.ext import commands


class SbonkCommands(commands.Cog):
    """Hold and executes all sbonk commands."""

    def __init__(self, bot):
        self.bot = bot
        self.iexcloud_key = os.getenv("IEXCLOUD_KEY")

    def get_stock_data(self, symbol, timeframe):
        """A more refined stock quote function."""
        # Request stock quotes from iex cloud
        request = ("https://cloud.iexapis.com/stable/stock/market/batch?"
                   f"symbols={symbol}&types=chart,quote&"
                   f"range={timeframe}&token={self.iexcloud_key}")

        response = requests.get(request)

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            if response.status_code == 402:
                return {"error": 402}
            return {}

    @staticmethod
    def draw_symbol_chart(symbol_data, timeframe):
        """
        Draw image for ONE symbol and return image
        Args:
            symbol_data(dict): dict must contain "chart" and "quote"
        """
        minutes = True if timeframe == "1d" else False
        chart_timeframe = "Today" if minutes else f"{timeframe} chart"
        key = "average" if minutes else "close"
        quote = symbol_data["quote"]
        chart = symbol_data["chart"]

        # pull average price for each minute
        prices = [x[key] if x[key] else 0
                  for x in symbol_data["chart"]]

        def find_last(i):
            for i in range(i, 0, -1):
                if prices[i]:
                    return prices[i]
            return prices[i] if prices[i] else quote["previousClose"]
        prices = [find_last(i) for i in range(len(prices))]

        close = chart[0]["close"]
        extend_list = []
        if minutes:
            # Extends data with null values in case its the middle of the day
            extend_list = [np.nan] * (390 - len(prices))
            close = quote["previousClose"]

        average_list = prices + extend_list
        color = "lime" if quote["latestPrice"] >= close else "red"
        pct_change = (quote["latestPrice"]/close) - 1
        change = quote["latestPrice"] - close
        data_len = len(average_list)

        # plot graph
        plt.ioff()  # ignore exception
        plt.clf()
        plt.style.use('dark_background')
        plt.xlim((0, data_len))
        plt.plot(list(range(data_len)), average_list, color=color)
        plt.hlines(close, 0, data_len,
                   colors="grey", linestyles="dotted")

        # remove extraneous lines
        plt.xticks([])
        plt.yticks([])
        ax = plt.gca()
        for side in ("left", "right", "top", "bottom"):
            ax.spines[side].set_visible(False)

        # add Symbol and price text
        price = quote["extendedPrice"] if quote["extendedPrice"] else quote["latestPrice"]
        text = f"{quote['symbol']} ${price:.2f}"
        plt.text(0, 1.1, text, va="bottom", ha="left",
                 size=30, c="white", transform=ax.transAxes)

        # add change text
        change_emoji = "⬆️" if pct_change >= 0 else "⬇️"
        change_text = f"{change_emoji}{abs(change):.2f} ({pct_change*100:.2f}%)"
        color = "lime" if pct_change >= 0 else "red"
        plt.text(0, 1, change_text, va="bottom", ha="left",
                 size=20, c=color, transform=ax.transAxes)
        plt.text(1, 1.15, f"{chart_timeframe}", va="bottom", ha="right",
                 size=12, c="grey", transform=ax.transAxes)

        # convert the chart to a bytes object Discord can read
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
        buffer = buffer.getvalue()
        return io.BytesIO(buffer)

    @staticmethod
    def extract_symbols(string):
        """Extract valid symbols from a string."""
        string += " "
        pattern = r"[$][a-zA-Z]{1,4}[^a-zA-Z]"
        prefixed_symbols = re.findall(pattern, string)

        ticker_list = [s[:-1] for s in prefixed_symbols]
        ticker_dict = {}

        # Finds ticker arguments and stores them in a dict
        for ticker in ticker_list:
            index = string.find(ticker)
            location = index+len(ticker)
            if string[location] == "[":
                start = location + 1
                end = location + string[location:].find("]")
                args = string[start:end].split("|") + ["", "", "", ""]

                ticker_dict[ticker[1:]] = {
                    "range": args[0],
                    "message": args[1],
                    "mock": args[2],
                    "delete": args[3],
                }
            else:
                ticker_dict[ticker[1:]] = {
                    "range": "1d",
                    "message": None,
                    "mock": None,
                    "delete": None,
                }

        return ticker_dict

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listens for sbonks"""
        # ignore bot
        if message.author.id == self.bot.user.id or message.author.id in cfg.supermuted_users:
            return

        # He Bought and He Sold
        if message.content.lower() in ("he bought", "he bought?"):
            return await message.channel.send("https://www.youtube.com/watch?v=61Q6wWu5ziY")
        elif message.content.lower() in ("he sold", "he sold?"):
            return await message.channel.send("https://www.youtube.com/watch?v=TRXdxiot5JM")

        ticker_info = SbonkCommands.extract_symbols(message.content)

        for ticker, args in ticker_info.items():
            data = self.get_stock_data(ticker, args['range'])
            ticker = ticker.upper()
            # weirdchamp for unknown symbol
            if ticker not in data.keys():
                if data.get("error") == 402:
                    await message.channel.send("Out of juice :peepoSad:")
                    continue
                await message.channel.send(utils.weirdchamp())
                continue

            # Send chart
            async with message.channel.typing():
                chart = SbonkCommands.draw_symbol_chart(
                    data[ticker], args['range'])
                file = discord.File(chart, filename=f"{ticker}.png")
                await message.channel.send(file=file)  # send stock chart
                if args['message']:
                    if args['mock']:
                        await message.channel.send(utils.mock(args['message']))
                    else:
                        await message.channel.send(args['message'])
                if args['delete']:
                    await message.delete()


def setup(bot):
    bot.add_cog(SbonkCommands(bot))
