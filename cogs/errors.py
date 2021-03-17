import sys
import traceback

import discord
from discord.ext import commands


class CommandErrors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command."""

        print("error caught")

        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.CommandError):
            return await ctx.send(embed=discord.Embed(title=str(error), color=discord.Color.red()))

        ################ CUSTOM ERROR HANDLING ################

        print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(CommandErrors(bot))