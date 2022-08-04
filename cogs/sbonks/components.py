import discord
from discord.ui import Modal, InputText
from common.database import db


class ApiKeyModal(Modal):
    def __init__(self):
        super().__init__(title="Set Sbonks API Key")
        self.add_item(InputText(
            label="Publishable API Key",
            placeholder="Please make sure this is the publishable iex key and not the secret iex key"
        ))

    async def callback(self, interaction: discord.Interaction):

        key = self.children[0].value

        success = db.set_sbonk_key(interaction.guild.id, key)
        if success:
            await interaction.response.send_message("Successfully set API key")
        else:
            await interaction.response.send_message("Failed to set API key")
