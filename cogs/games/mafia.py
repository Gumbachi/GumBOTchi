"""Module with mafia related cog and commands."""

import discord
from discord.ext import commands


class MafiaCommands(commands.Cog):
    """All mafia related commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mafia')
    async def begin_mafia_game(self, ctx):
        """Start mafia game"""
        await ctx.send("Please @ the players")

    @commands.command(name="scoreboard", aliases=["sb"])
    async def display_scoreboard(self, ctx):
        """Start mafia game"""
        sb_embed = discord.Embed(
            title="Derk's Game of Mafia",
            description="Put the next step/rules or edit to say who mafia was etc.",
            color=discord.Color.blurple()
        )
        sb_embed.add_field(name="Team 1", value="Goomba\nGoomba2")
        sb_embed.add_field(name="Team 2", value="Derk\nDerk2")

        sb_embed.add_field(name="Scoreboard",
                           value="Goomba: 10\nDerk2: 5\nGoomba2: 3\nDerk: -17",
                           inline=False)

        sb_embed.set_footer(
            text="You could put instructions down here if u want too :)")

        await ctx.send(embed=sb_embed)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Listen for reactions."""
        pass


def setup(bot):
    bot.add_cog(MafiaCommands(bot))
