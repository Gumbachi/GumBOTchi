"""Draws sbonks for the people. Styling found is res/sbonks.mplstyle ."""

import io
import os
import re

import aiohttp
import discord
from discord.commands import slash_command

from common.cfg import Tenor, Emoji, devguilds
import matplotlib.pyplot as plt
import numpy as np


class SbonkCommands(discord.Cog):
    """Holds all sbonk related commands/listeners."""

    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("IEXCLOUD_KEY")

    async def get_stock_data(self, symbols: list[str], *endpoints: str):
        """A more refined stock quote function."""
        # Request stock quotes from iex cloud
        params = {
            "types": ','.join(endpoints),
            "symbols": ','.join(symbols),
            "displayPercent": "true",
            "token": self.api_key
        }
        url = f"https://cloud.iexapis.com/stable/stock/market/batch"

        # Make web request asynchronously
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {}

    async def get_historical_data(symbol: str, timeframe: str):
        """
        Get close data for multiple days.

        timeframe can be 1w, 

        """
        pass

    async def get_credit_usage(self):
        params = {"token": self.api_key}
        url = f"https://cloud.iexapis.com/stable/account/usage/credits"

        # Make web request asynchronously
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("monthlyUsage")

    @staticmethod
    def draw_symbol_chart(symbol_data):
        """Draw day chart for one symbol."""

        quote = symbol_data["quote"]
        intraday = symbol_data["intraday-prices"]
        data_length = 390

        prices = [x['close'] for x in intraday]

        def find_last(i):
            """Fills in price gaps with previous data point"""
            for i in range(i, 0, -1):
                if prices[i]:
                    return prices[i]
            return prices[i] or quote["previousClose"]

        # format data for graphing
        prices = [find_last(i) for i in range(len(prices))]
        prices += [np.nan] * (data_length - len(prices))
        prices = prices[::5]

        # set text and arrow
        if quote["latestPrice"] >= quote["previousClose"]:
            color = "lime"
            arrow = '▲'
        else:
            color = "red"
            arrow = '▼'

        change = quote['change']
        change_pct = quote["changePercent"]

        # plot graph
        plt.style.use('./res/sbonks.mplstyle')  # use defined style
        plt.clf()  # Reset so graphs dont overlap. This must be after plt.style.use
        plt.axis('off')  # disable labels maybe could move this to .mplstyle
        plt.xlim(0, len(prices))
        plt.plot(list(range(len(prices))), prices, color=color)
        plt.axhline(y=quote['previousClose'], color="grey", linestyle="dotted")
        ax = plt.gca()  # get current axes for transform

        # add Symbol and price text
        price = quote["extendedPrice"] or quote["latestPrice"]
        text = f"{quote['symbol']} ${price:.2f}"
        plt.text(x=0, y=1.1, s=text, va="bottom", ha="left",
                 size=35, c="white", transform=ax.transAxes)

        # add change text
        change_text = f"{arrow} {abs(change):.2f} ({change_pct:.2f}%)"
        plt.text(x=0, y=1, s=change_text, va="bottom", ha="left",
                 size=25, c=color, transform=ax.transAxes)

        # convert the chart to a bytes object Discord can read
        buffer = io.BytesIO()
        plt.savefig(buffer)
        buffer = buffer.getvalue()
        return io.BytesIO(buffer)

    @staticmethod
    def extract_symbols(string):
        """Extract valid symbols from a string."""
        string += " "  # needed because ticker must be followed by non alpha
        pattern = r"[$][a-zA-Z]{1,4}[^a-zA-Z]"
        prefixed_symbols = re.findall(pattern, string)

        # Format string as "NVDA", rather than "$nVdA,". 10 symbol limit
        return [s.replace("$", "")[:-1].upper() for s in prefixed_symbols][:10]

    @slash_command(name="credits")
    async def get_credits(self, ctx):
        credits_used = await self.get_credit_usage()
        usage_percent = credits_used/50000 * 100
        color = discord.Color.green() if credits_used < 50000 else discord.Color.red()
        emb = discord.Embed(
            title=f"{usage_percent:.2f}%",
            description=f"({credits_used}/50,000)",
            color=color
        )
        await ctx.respond(embed=emb)

    @discord.Cog.listener("on_message")
    async def quick_responses(self, message):
        """Process quick responses."""
        # ignore bot
        if message.author.id == self.bot.user.id:
            return

        # guh listener
        if message.content.lower() == "guh":
            return await message.channel.send(Emoji.GUH)

        # He Bought listener
        if message.content.lower() in ("he bought", "he bought?"):
            return await message.channel.send(Tenor.HE_BOUGHT)

        # He Sold listener
        if message.content.lower() in ("he sold", "he sold?"):
            return await message.channel.send(Tenor.HE_SOLD)

    @discord.Cog.listener("on_message")
    async def parse_symbols(self, message):
        """Listens for sbonks."""
        # ignore bot
        if message.author.id == self.bot.user.id:
            return

        # Parse symbols from message and check if there are any
        symbols = self.extract_symbols(message.content)
        if not symbols:
            return

        # Fetch data from iex and check if there is any
        data = await self.get_stock_data(symbols, 'quote', 'intraday-prices')
        if not data:
            return await message.channel.send(Emoji.WEIRDCHAMP)

        if data.get("error") == 402:
            return await message.channel.send("Ran out of juice :peepoSad:")

        files = []
        for symbol in symbols:
            symbol_data = data.get(symbol, None)

            # Check that symbol data exists
            if not symbol_data:
                await message.channel.send(f"{Emoji.WEIRDCHAMP} **{symbol}** {Emoji.WEIRDCHAMP}")
                continue

            # Draw and send the chart
            async with message.channel.typing():
                chart = self.draw_symbol_chart(symbol_data)
                file = discord.File(chart, filename=f"{symbol}.png")
                files.append(file)

        await message.reply(files=files)


def setup(bot):
    bot.add_cog(SbonkCommands(bot))
