class DatabaseError(Exception):
    @property
    def embed(self):
        import discord

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
