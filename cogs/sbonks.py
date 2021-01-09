import json
import os
import re
import io

import common.cfg as cfg
import common.database as db
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

    # @commands.command(name="add_to_watchlist")
    # async def add_to_watchlist(self, ctx, *, symbol_str):
    #     """add a symbol to the watch list"""
    #     symbols = SbonkCommands.extract_symbols(
    #         symbol_str, sbonk_notation=False)
    #     symbols = [s.upper() for s in symbols]

    #     # check for user
    #     data = db.usercoll.find_one({"_id": ctx.author.id})
    #     if not data:
    #         # check for watchlimit
    #         if len(symbols) > cfg.watchlimit:
    #             symbols = symbols[:50]

    #         db.usercoll.insert_one({"_id": ctx.author.id,
    #                                 "watchlist": symbols})
    #     else:
    #         watchlist_length = len(data["watchlist"])
    #         if len(symbols) + watchlist_length > cfg.watchlimit:
    #             symbols = symbols[:50-watchlist_length]

    #         db.usercoll.update_one(
    #             {"_id": ctx.author.id},
    #             {"$addToSet": {"watchlist": {"$each": symbols}}}
    #         )

    #     embed = discord.Embed(
    #         title=f"Added {len(symbols)} symbols to your watchlist",
    #         description="",
    #         color=discord.Color.green()
    #     )
    #     await ctx.send(embed=embed)

    # @commands.command(name="watchlist", aliases=["wl"])
    # async def show_watchlist(self, ctx):
    #     """add a symbol to the watch list"""

    #     # check for user
    #     data = db.usercoll.find_one({"_id": ctx.author.id})
    #     if not data:
    #         data = {"_id": ctx.author.id, "watchlist": []}
    #         db.usercoll.insert_one(data)

    #     wl = data["watchlist"]
    #     sbonk_data = self.get_stock_data(wl, "quote")
    #     embed = discord.Embed(
    #         title=f"{ctx.author.name}'s watchlist ({len(wl)}/{cfg.watchlimit})"
    #     )

    #     for symbol in wl:
    #         if symbol not in sbonk_data.keys():
    #             continue

    #         quote = sbonk_data[symbol]["quote"]
    #         embed.add_field(
    #             name=quote["symbol"],
    #             value=quote["latestPrice"]
    #         )
    #     await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listens for sbonks"""
        # ignore bot
        if message.author.id == bot.user.id:
            return

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
