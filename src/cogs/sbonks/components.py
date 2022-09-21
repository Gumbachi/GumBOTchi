import database as db
import discord
from discord.ui import InputText, Modal


class ApiKeyModal(Modal):
    def __init__(self):
        super().__init__(title="Set Sbonks API Key")
        self.add_item(InputText(
            label="Publishable API Key",
            placeholder="Please make sure this is the publishable iex key and not the secret iex key"
        ))

    async def callback(self, interaction: discord.Interaction):
        key = self.children[0].value
        db.set_iexkey(id=interaction.guild.id, key=key)
        await interaction.response.send_message("Successfully set API key")
