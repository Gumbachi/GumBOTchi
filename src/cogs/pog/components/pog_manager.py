import database as db
import discord

from .add_modal import PogAddModal
from .pog_type import PogType
from .remove_dropdown import PogRemovalDropdown


class PogManager(discord.ui.View):

    def __init__(self, guild: discord.Guild) -> None:

        self.pogtype = PogType.ACTIVATOR  # type is taken by discord.Component
        self.responses = db.get_pogresponses(id=guild.id)
        self.activators = db.get_pogactivators(id=guild.id)

        super().__init__(
            PogRemovalDropdown(manager=self),
            timeout=None
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check permissions to use the manager"""
        if not interaction.user.guild_permissions.manage_messages and interaction.custom_id in ("POGADDBUTTON", "POGDROPDOWN"):
            await interaction.response.send_message("With what permissions?", ephemeral=True)
            return False

        return True

    @discord.ui.button(label="ADD", style=discord.ButtonStyle.blurple, custom_id="POGADDBUTTON")
    async def add_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(modal=PogAddModal(self))

    @discord.ui.button(label="REFRESH", style=discord.ButtonStyle.blurple, custom_id="POGREFRESHBUTTON")
    async def refresh_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.responses = db.get_pogresponses(id=interaction.guild.id)
        self.activators = db.get_pogactivators(id=interaction.guild.id)
        self.update()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label="POGFLIP", style=discord.ButtonStyle.blurple, custom_id="POGFLIPBUTTON")
    async def flip_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.flip()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @property
    def embed(self):
        match self.pogtype:
            case PogType.ACTIVATOR:
                return discord.Embed(
                    title="Activators",
                    description=", ".join([f"`{a}`" for a in self.activators])
                ).set_footer(text="Hint: Hit the pogflip button to see responses")
            case PogType.RESPONSE:
                return discord.Embed(
                    title="Responses",
                    description="\n".join(self.responses)
                ).set_footer(text="Hint: Hit the pogflip button to see activators")

    def flip(self):
        """Flips the manager from responses to activators or vice versa."""
        if self.pogtype == PogType.ACTIVATOR:
            self.pogtype = PogType.RESPONSE
        else:
            self.pogtype = PogType.ACTIVATOR

        self.update()

    def update(self):
        """Update the managers components."""
        self.remove_item(self.children[-1])
        self.add_item(PogRemovalDropdown(manager=self))
