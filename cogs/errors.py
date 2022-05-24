import discord


class CommandErrors(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.Cog.listener()
    async def on_command_error(self, ctx: discord.ApplicationContext, error):
        """The event triggered when an error is raised while invoking a command."""
        await ctx.respond(f"Houston we have a problem: \n{error}")


def setup(bot: discord.Bot):
    bot.add_cog(CommandErrors(bot))
