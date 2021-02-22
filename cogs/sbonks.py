import json
import os
import re
import io

import common.cfg as cfg
import discord
import matplotlib.pyplot as plt
import numpy as np
import requests
from common.cfg import bot
from discord.ext import commands


class SbonkCommands(commands.Cog):
    """Hold and executes all sbonk commands."""

    def __init__(self, bot):
        self.bot = bot
        self.iexcloud_key = os.getenv("IEXCLOUD_KEY")

    def get_stock_data(self, symbols, *endpoints):
        """A more refined stock quote function."""
        # Request stock quotes from iex cloud
        request = ("https://cloud.iexapis.com/stable/stock/market/batch"
                   f"?types={','.join(endpoints)}&symbols={','.join(symbols)}"
                   f"&displayPercent=true&token={self.iexcloud_key}")
        response = requests.get(request)
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def draw_symbol_chart(symbol_data):
        """
        Draw image for ONE symbol and return image
        Args:
            symbol_data(dict): dict must contain "intraday-prices" and "quote"
        """
        quote = symbol_data["quote"]

        # pull average price for each minute
        average_list = [x["average"] if x["average"] else 0
                        for x in symbol_data["intraday-prices"]]
        average_list = list(filter((0).__ne__, average_list))  # remove 0s
        average_list += [np.nan] * (390 - len(average_list))  # extend list

        color = "lime" if quote["latestPrice"] >= quote["previousClose"] else "red"

        # plot graph
        plt.clf()
        plt.style.use('dark_background')
        plt.xlim((0, 390))
        plt.plot(list(range(390)), average_list, color=color)
        plt.hlines(quote["previousClose"], 0, 390,
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
        change_emoji = "⬆️" if quote["change"] >= 0 else "⬇️"
        change_text = f"{change_emoji}{abs(quote['change']):.2f} ({quote['changePercent']:.2f}%)"
        color = "lime" if quote["change"] >= 0 else "red"
        plt.text(0, 1, change_text, va="bottom", ha="left",
                 size=20, c=color, transform=ax.transAxes)

        # convert the chart to a bytes object Discord can read
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
        buffer = buffer.getvalue()
        return io.BytesIO(buffer)

    @staticmethod
    def extract_symbols(string, sbonk_notation=True):
        """Extract valid symbols from a string."""
        string += " "
        pattern = r"[a-zA-Z]{1,4}[^a-zA-Z]"
        if sbonk_notation:
            pattern = "[$]" + pattern
        prefixed_symbols = re.findall(pattern, string)

        # strip $ and 1 character off the strings
        if not sbonk_notation:
            return [s[:-1] for s in prefixed_symbols]
        return [s[1:-1] for s in prefixed_symbols]

    @commands.command(name='hebought')
    async def howdy(self, ctx):
        """Says howdy!"""
        await ctx.send(f"Howdy, {ctx.message.author.mention}!")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listens for sbonks"""
        # ignore bot
        if message.author.id == bot.user.id:
            return

        # Salm aint gonna hurt my feelings anymore
        if message.author.id == 244574519027564544 and message.content.lower() == "$xpev":
            return await message.channel.send("Yeah, I think the fuck not")

        if message.content.lower() in ("he bought", "he bought?"):
            return await message.channel.send("https://www.youtube.com/watch?v=61Q6wWu5ziY")
        elif message.content.lower() in ("he sold", "he sold?"):
            return await message.channel.send("https://www.youtube.com/watch?v=TRXdxiot5JM")

        symbols = SbonkCommands.extract_symbols(message.content)
        data = self.get_stock_data(symbols, "quote", "intraday-prices")
        for symbol in symbols:
            symbol = symbol.upper()
            # weirdchamp for unknown symbol
            if symbol not in data.keys():
                weirdchamp = bot.get_emoji(746570904032772238)
                await message.channel.send(str(weirdchamp))
                continue

            # Send chart
            async with message.channel.typing():
                chart = SbonkCommands.draw_symbol_chart(data[symbol])
                file = discord.File(chart, filename=f"{symbol}.png")
                await message.channel.send(file=file)  # send stock chart


def setup(bot):
    bot.add_cog(SbonkCommands(bot))
