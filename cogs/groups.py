import sys
import traceback

import discord
from discord.ext import commands

import common.database as db


class GroupCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="creategroup", aliases=["cg"])
    async def create_group(self, ctx, groupname,  members: commands.Greedy[discord.Member]):
        """Creates a group of members."""
        if not groupname.isalnum():
            raise commands.CommandError("Group name must be alphanumeric.")

        # isolate group member ids
        ids = [x.id for x in members]
        if not ids:
            raise commands.CommandError("Group must have members.")

        # add to database
        group = {
            "name": groupname,
            "members": ids
        }
        db.guilds.update_one(
            {"_id": ctx.guild.id},
            {"$push": {"groups": group}}
        )

    @commands.command(name="summon", aliases=["call, assemble"])
    async def summon_group(self, ctx, *, name):
        """Summons a group of members."""
        groups = db.get(ctx.guild.id, "groups")

        for group in groups:
            if group["name"].lower() == name.lower():
                members = [ctx.guild.get_member(x) for x in group["members"]]
                mentions = [m.mention for m in filter(None, members)]
                return await ctx.send(f"Summoning {name}: {', '.join(mentions)}")

        raise commands.UserInputError("Couldn't find group.")


def setup(bot):
    bot.add_cog(GroupCommands(bot))
