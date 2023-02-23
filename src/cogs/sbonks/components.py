import discord

import database as db


class ApiKeyModal(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(title="Set Sbonks API Key")
        self.add_item(discord.ui.InputText(
            label="Publishable API Key",
            placeholder="Please make sure this is the publishable iex key and not the secret iex key"
        ))

    async def callback(self, interaction: discord.Interaction) -> None:
        key = self.children[0].value
        db.set_iexkey(id=interaction.guild.id, key=key)
        await interaction.response.send_message("Successfully set API key")
