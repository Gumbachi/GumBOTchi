"""Draws sbonks for the people. Styling found is res/sbonks.mplstyle ."""
import re

import discord
from discord import Option, slash_command, ApplicationContext
from cogs.sbonks.components import ApiKeyModal
from cogs.sbonks.iexapi import IEXAPI, IEXAPIError

from common.cfg import Tenor, Emoji
from common.database import db


class SbonkCommands(discord.Cog):
    """Holds all sbonk related commands/listeners."""

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def extract_symbols(string: str):
        """Extract valid symbols from a string."""
        string += " "  # needed because ticker must be followed by non alpha
        pattern = r"[$][a-zA-Z]{1,4}[^a-zA-Z]"
        prefixed_symbols = re.findall(pattern, string)

        # Format string as "NVDA", rather than "$nVdA,". 10 symbol limit
        return [s.replace("$", "")[:-1].upper() for s in prefixed_symbols][:10]

    @slash_command(name="set-sbonks-apikey")
    @discord.default_permissions(administrator=True)
    async def set_sbonks_apikey(self, ctx: ApplicationContext):
        """Set your publishable IEX Cloud API key to enable sbonks."""
        modal = ApiKeyModal()
        await ctx.send_modal(modal)

    @slash_command(name="sbonk")
    async def get_sbonk_chart(
        self, ctx: ApplicationContext,
        symbol: Option(str, "The symbol to search for"),
        timeframe: Option(
            str,
            description="Choose how hard you want to hit our allowance",
            choices=["1D", "1W", "1M", "3M", "6M", "1Y", "2Y", "5Y", "MAX"],
            default="1D"
        ),
        message: Option(str, "Because weed is the future") = None,
        mock: Option(bool, "bEcAuSe WeEd Is ThE fUtuRe") = False
    ):
        """Show a sbonk chart for a specific timeframe"""

        symbol = symbol.upper().replace("$", "")

        await ctx.defer()

        # Fetch data from iex and check if there is any
        try:
            api = IEXAPI(ctx.guild.id)
        except IEXAPIError:
            return await ctx.respond("No API Key set. You should fix that with `/set-sbonks-apikey` if you want sbonks.")

        try:
            if timeframe == "1D":
                data = await api.get_intraday([symbol])
                data = data[0]
                precision = 5

            elif timeframe == "1W":
                data = await api.get_week(symbol=symbol)
                precision = 1

            elif timeframe == "1M":
                data = await api.get_month(symbol=symbol)
                precision = 1

            elif timeframe == "3M":
                data = await api.get_three_month(symbol=symbol)
                precision = 1

            elif timeframe == "6M":
                data = await api.get_six_month(symbol=symbol)
                precision = 1

            elif timeframe == "1Y":
                data = await api.get_year(symbol=symbol)
                precision = 1

            elif timeframe == "2Y":
                data = await api.get_two_year(symbol=symbol)
                precision = 1

            elif timeframe == "5Y":
                data = await api.get_five_year(symbol=symbol)
                precision = 1

            elif timeframe == "MAX":
                data = await api.get_max(symbol=symbol)
                precision = 1

        except IEXAPIError:
            return await ctx.respond(Emoji.WEIRDCHAMP)

        if not data:
            return await ctx.respond(Emoji.WEIRDCHAMP)

        await ctx.respond(file=data.graph(precision, message, mock))

    @discord.Cog.listener("on_message")
    async def quick_responses(self, message: discord.Message):
        """Process quick responses."""
        if message.author.bot:
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
    async def parse_symbols(self, message: discord.Message):
        """Listens for sbonks."""
        if message.author.bot:
            return

        # Parse symbols from message and check if there are any
        symbols = self.extract_symbols(message.content)
        if not symbols:
            return

        # Fetch data from iex and check if there is any
        try:
            api = IEXAPI(message.guild.id)
        except IEXAPIError:
            return  # ignore implicit sbonks call if key is not set

        data = await api.get_intraday(symbols)
        if not data:
            return await message.channel.send(Emoji.WEIRDCHAMP)

        async with message.channel.typing():
            await message.reply(files=[symbol.graph() for symbol in data])


def setup(bot):
    bot.add_cog(SbonkCommands(bot))
