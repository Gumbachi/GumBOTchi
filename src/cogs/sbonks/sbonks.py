"""Draws sbonks for the people. Styling found is res/sbonks.mplstyle ."""
import re
import random

import discord
from .alpha_vantage import AlphaVantage, AlphaVantageError
from .components import ApiKeyModal
from .graphing import display
from .time_series import ChartLength, DataType
from common.cfg import Emoji, Tenor
from discord import guild_only, option, slash_command


class SbonkCommands(discord.Cog):
    """Holds all sbonk related commands/listeners."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @staticmethod
    def extract_symbols(string: str):
        """Extract valid symbols from a string."""
        string += " "  # needed because ticker must be followed by non alpha
        pattern = r"[$][a-zA-Z]{1,4}[^a-zA-Z]"
        prefixed_symbols: list[str] = re.findall(pattern, string)

        # Format string as "NVDA", rather than "$nVdA,". 10 symbol limit
        return [s.replace("$", "")[:-1].upper() for s in prefixed_symbols][:10]

    @slash_command(name="set-sbonks-apikey")
    @discord.default_permissions(administrator=True)
    @guild_only()
    async def set_sbonks_apikey(self, ctx: discord.ApplicationContext):
        """Set your publishable AlphaVantage API key to enable sbonks."""
        modal = ApiKeyModal()
        await ctx.send_modal(modal)

    @slash_command(name="sbonk")
    @option("symbol", description="The symbol to search for")
    @option(
        "timeframe",
        description="This one is pretty self-explanatory",
        choices=["1D", "1W", "1M", "3M", "6M", "1Y", "MAX"],
        default="1D"
    )
    @guild_only()
    async def get_sbonk_chart(
        self, ctx: discord.ApplicationContext,
        symbol: str,
        timeframe: str,
    ):
        """Show a sbonk chart for a specific timeframe"""

        symbol = symbol.upper().replace("$", "")

        await ctx.defer()

        # Fetch data from alpha vantage and check if there is any
        try:
            api = AlphaVantage(ctx.guild.id)
        except AlphaVantageError:
            return await ctx.respond("No API Key set. You should fix that with `/set-sbonks-apikey` if you want sbonks.")

        chart_length = ChartLength.from_str(timeframe)
        data_type = chart_length.get_data_type()

        url = api.get_url(
            ticker = symbol,
            data_type = data_type
        )

        try:
            data = api.get_data(
                url = url,
                data_type = data_type
            )
        except AlphaVantageError:
            return await ctx.respond(Emoji.WEIRDCHAMP)

        if not data:
            return await ctx.respond(Emoji.WEIRDCHAMP)
        
        chart = display(
            name = symbol,
            time_series_data = data,
            length = chart_length,
        )

        if not chart:
            await ctx.respond("No chart created??")

        await ctx.respond(
            file=chart
        )

    @discord.Cog.listener("on_message")
    async def sbonks_quick_responses(self, message: discord.Message):
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
        if message.author.bot or message.guild is None:
            return

        # Parse symbols from message and check if there are any
        symbols = self.extract_symbols(message.content)

        if not symbols and random.randint(0, 250) != 69:
            return


        # Fetch data from AV and check if there is any
        try:
            api = AlphaVantage(message.guild.id)
        except AlphaVantageError:
            return  # ignore implicit sbonks call if key is not set

        charts = []
        for symbol in symbols:

            url = api.get_url(
                ticker = symbol,
                data_type = DataType.INTRADAY
            )

            try:
                data = api.get_data(
                    url = url,
                    data_type = DataType.INTRADAY
                )
            except AlphaVantageError:
                continue

            if not data:
                continue
            
            chart = display(
                name = symbol,
                time_series_data = data,
                length = ChartLength.DAY,
            )

            if chart:
                charts.append(chart)

        async with message.channel.typing():
            if not charts:
                await message.reply(Emoji.WEIRDCHAMP)
            else:
                await message.reply(files=charts)


def setup(bot: discord.Bot):
    bot.add_cog(SbonkCommands(bot))
