import discord


class DatabaseError(Exception):

    @property
    def embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="Database Error",
            color=discord.Color.red()
        )
        match self.args:
            case [title, description]:
                embed.title = title
                embed.description = description
            case [title]:
                embed.title = title

        return embed


class PogDatabaseError(DatabaseError):
    pass
