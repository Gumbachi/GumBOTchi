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
