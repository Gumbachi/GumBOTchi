"""Draws sbonks for the people. Styling found is res/sbonks.mplstyle ."""

import io
import os
import re

import aiohttp
import discord
from discord.commands import slash_command
from cogs.sbonks.model.iexapi import IEXAPI

from common.cfg import Tenor, Emoji, devguilds
import matplotlib.pyplot as plt
import numpy as np


class SbonkCommands(discord.Cog):
    """Holds all sbonk related commands/listeners."""

    def __init__(self, bot):
        self.bot = bot

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
    async def parse_symbols(self, message: discord.Message):
        """Listens for sbonks."""
        # ignore bot
        if message.author.id == self.bot.user.id:
            return

        # Parse symbols from message and check if there are any
        symbols = self.extract_symbols(message.content)
        if not symbols:
            return

        # Fetch data from iex and check if there is any
        data = await IEXAPI().get_intraday(symbols)
        if not data:
            return await message.channel.send(Emoji.WEIRDCHAMP)

        async with message.channel.typing():
            await message.reply(files=[symbol.graph() for symbol in data])


def setup(bot):
    bot.add_cog(SbonkCommands(bot))
