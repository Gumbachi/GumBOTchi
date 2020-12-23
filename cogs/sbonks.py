import os
import re
import json
from pprint import pprint
import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandError
import requests
from common.cfg import bot


class UnknownSymbolError(CommandError):
    """Raise for unknown symbol."""
    pass


class SbonkCommands(commands.Cog):
    """Hold and executes all sbonk commands."""

    def __init__(self, bot):
        self.bot = bot
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_KEY")
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

        # generate and send sbonk embed
        sbonk_embed = discord.Embed(
            title=f"{symbol}: ${data['latestPrice']}",
            description=f"{change_symbol} ({change_percent}%)",
            color=discord.Color.green() if change >= 0 else discord.Color.red()
        )
        sbonk_embed.set_footer(text=data["latestTime"])
        return sbonk_embed

    # def fetch_stock(self, symbol):
    #     """Fetch stock data and form into embed"""
    #     symbol = symbol.upper()

    #     # API requests from https://www.alphavantage.co/
    #     response = requests.get(
    #         f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={self.api_key}")
    #     live_data = response.json()
    #     print(response.status_code)

    #     response = requests.get(
    #         f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={self.api_key}")
    #     daily_data = response.json()
    #     print(response.status_code)

    #     print(live_data)
    #     print(daily_data)

    #     # important minute data
    #     time = live_data["Meta Data"]["3. Last Refreshed"]
    #     price = live_data["Time Series (1min)"][time]["4. close"]

    #     # important daily data
    #     last_close_date = daily_data["Meta Data"]["3. Last Refreshed"]
    #     last_close_price = daily_data["Time Series (Daily)"][last_close_date]["4. close"]

    #     # Convert data to suit embed
    #     price_diff = round(float(price) - float(last_close_price), 2)
    #     is_printing = price_diff >= 0  # if current price is higher than close
    #     change = f"⬆️${price_diff}" if is_printing else f"⬇️${price_diff}"
    #     percent_change = round(price_diff/float(last_close_price)*100, 2)
    #     color = discord.Color.green() if is_printing else discord.Color.red()

    #     # generate and send sbonk embed
    #     sbonk_embed = discord.Embed(
    #         title=f"{symbol}: ${round(float(price), 2)}",
    #         description=f"{change} ({percent_change}%)",
    #         color=color
    #     )
    #     sbonk_embed.set_footer(text=time)
    #     return sbonk_embed

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
                await message.channel.send(embed=embed)  # send sbonk embed


def setup(bot):
    bot.add_cog(SbonkCommands(bot))
