from typing import TYPE_CHECKING

import database as db
import discord
from discord import SelectOption

from .pog_type import PogType

if TYPE_CHECKING:
    from .pog_manager import PogManager


class PogRemovalDropdown(discord.ui.Select):
    def __init__(self, manager: "PogManager"):
        self.manager = manager

        if manager.pogtype == PogType.ACTIVATOR:
            options = manager.activators
        else:
            options = manager.responses

        super().__init__(
            custom_id="POGDROPDOWN",
            placeholder=f"Remove a pog {self.manager.pogtype.value}",
            options=[SelectOption(label=o) for o in options]
            or [SelectOption(label="0")],
            row=1,
            disabled=not options,  # if options enabled else disabled
        )

    async def callback(self, interaction: discord.Interaction):
        match self.manager.pogtype:
            case PogType.RESPONSE:
                db.remove_pogresponse(id=interaction.guild.id, response=self.values[0])
            case PogType.ACTIVATOR:
                db.remove_pogactivator(
                    id=interaction.guild.id, activator=self.values[0]
                )

        self.manager.update()
        await interaction.response.edit_message(
            embed=self.manager.embed, view=self.manager
        )
