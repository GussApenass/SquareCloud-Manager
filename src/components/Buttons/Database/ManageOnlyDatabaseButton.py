
from typing import Any, Dict
import discord
from discord import ui
from base import emoji, squarecloud_request
from src.components.LayoutView.Database.ManageOnlyDatabase import ManageOnlyDatabase
from src.components.LayoutView.LayoutError import LayoutError
from base.request.models import SquareErrorModel

class ManageOnlyDatabaseButton(ui.Button):
    def __init__(self, database_id: str, database_info: Dict[str, Any]):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji.menu2
        )
        self.database_id = database_id
        self.database_info = database_info

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # STATUS REQ

        req_status = await squarecloud_request.get_database_status(self.database_id)

        if isinstance(req_status, SquareErrorModel):
            code = req_status.code
            msg = code if code else "Erro ao buscar status da aplicação."

            return await interaction.followup.send(view=LayoutError(msg))

        # ===

        await interaction.edit_original_response(
            view=ManageOnlyDatabase(self.database_info, req_status)
        )