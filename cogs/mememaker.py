import common.cfg as cfg
from common.cfg import bot
from discord.ext import commands


class MemeMakerCommands(commands.Cog):
    """Hold and executes all sbonk commands."""

    def __init__(self, bot):
        self.bot = bot

    # @commands.command(name='howdy')
    # async def howdy(self, ctx):
    #     """Says howdy!"""
    #     await ctx.send(f"Howdy, {ctx.message.author.mention}!")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listens for sbonks"""
        # ignore bot
        if message.author.id == bot.user.id:
            return


def setup(bot):
    bot.add_cog(MemeMakerCommands(bot))
