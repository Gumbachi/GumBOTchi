"""Class for a Craigslist Query."""

from dataclasses import dataclass

import discord


@dataclass(slots=True)
class CraigslistQuery:
    owner: discord.User

    zipcode: int
    searchstring: str
