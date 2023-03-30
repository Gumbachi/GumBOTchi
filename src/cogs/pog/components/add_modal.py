from typing import TYPE_CHECKING

import database as db
import discord

if TYPE_CHECKING:
    from .pog_manager import PogManager

from .pog_type import PogType


class PogAddModal(discord.ui.Modal):
    def __init__(self, manager: "PogManager") -> None:
        self.manager = manager

        super().__init__(
            discord.ui.InputText(label="Phrase"),
            title=f"Add a pog {manager.pogtype.value}"
        )

    async def callback(self, interaction: discord.Interaction):

        match self.manager.pogtype:
            case PogType.RESPONSE:
                db.add_pogresponse(id=interaction.guild.id, response=self.children[0].value)
            case PogType.ACTIVATOR:
                db.add_pogactivator(id=interaction.guild.id, activator=self.children[0].value)

        self.manager.update()
        await interaction.response.edit_message(embed=self.manager.embed, view=self.manager)

    async def on_error(self, error: Exception, interaction: discord.Interaction):

        if isinstance(error, db.PogDatabaseError):
            return await interaction.response.send_message(embed=error.embed, ephemeral=True)

        raise error
