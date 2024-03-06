import discord

import database as db

class ApiKeyModal(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(title="Set Sbonks API Key")
        self.add_item(
            discord.ui.InputText(
                label="API Key",
                placeholder="Alpha Vantage API Key"
            )
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        key = self.children[0].value
        db.set_alphavantage(id=interaction.guild.id, key=key)
        await interaction.response.send_message("Successfully set API key")
