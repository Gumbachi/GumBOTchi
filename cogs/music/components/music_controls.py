from typing import TYPE_CHECKING

import discord

from ..errors import NoVoiceClient
from .add_button import AddButton
from .history_dropdown import HistoryDropdown
from .page_buttons import LeftButton, RightButton
from .play_button import PlayPauseButton
from .refresh_button import RefreshButton
from .repeat_button import RepeatButton
from .rewind_button import RewindButton
from .skip_button import SkipButton

if TYPE_CHECKING:
    from ..player import MusicPlayer


class MusicControls(discord.ui.View):
    def __init__(self, player: "MusicPlayer"):
        super().__init__(
            RepeatButton(player),
            PlayPauseButton(player),
            RewindButton(player),
            SkipButton(player),
            LeftButton(player),
            AddButton(player),
            RightButton(player),
            RefreshButton(player),
            timeout=None
        )

        self.player = player
        if player.history:
            self.add_item(HistoryDropdown(player))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:

        if not isinstance(interaction.user, discord.Member):
            return False

        if not interaction.user.voice:
            await interaction.response.send_message(
                content="My brother in christ you need to be in a voice channel to listen to music",
                ephemeral=True
            )
            return False

        if interaction.custom_id in ("HISTORY", "ADD"):
            return True

        try:
            vcc = self.player.voice_client
        except NoVoiceClient:
            return False

        if interaction.user.voice.channel != vcc.channel:
            print("User is not in same channel as bot")
            return False

        return True
