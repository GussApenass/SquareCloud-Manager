import discord
from discord import ui
from typing import Dict, Any
from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutLoading import LayoutLoading
from src.components.LayoutView.Database.ManageOnlyDatabase import ManageOnlyDatabase

class RestartDatabaseButton(ui.Button):
    def __init__(self, db_info: Dict[str, Any], db_status: Dict[str, Any]):
        self.db_info = db_info
        self.db_status = db_status

        running = db_status.get("running", False)
        if running:
            disabled = False
        else:
            disabled = True

        super().__init__(
            disabled=disabled,
            emoji=emoji.restart,
            style=discord.ButtonStyle.primary
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        db_id = self.db_info.get("id")
        
        msg_loading = await interaction.followup.send(
            view=LayoutLoading("Reiniciando database..."),
            ephemeral=True
        )

        req = await squarecloud_request.restart_db(db_id)

        if isinstance(req, SquareErrorModel):
            code = req.code
            msg = code if code else "Erro ao reiniciar database."

            return await msg_loading.edit(view=LayoutError(msg))

        # STATUS REQ

        req_status = await squarecloud_request.get_database_status(db_id)

        if isinstance(req_status, SquareErrorModel):
            code = req_status.code
            msg = code if code else "Erro ao buscar status do database."

            return await msg_loading.edit(view=LayoutError(msg))

        await msg_loading.edit(
            view=LayoutInfo(f"{emoji.check} **|** Database reiniciado com sucesso!")
        )

        await interaction.edit_original_response(
            view=ManageOnlyDatabase(self.db_info, req_status)
        )