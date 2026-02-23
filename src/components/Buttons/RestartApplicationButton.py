import discord
from discord import ui
from typing import Dict, Any
from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutLoading import LayoutLoading
from src.components.LayoutView.ManageOnlyApplications import ManageOnlyApplications

class RestartApplicationButton(ui.Button):
    def __init__(self, application_info: Dict[str, Any], application_status: Dict[str, Any]):
        self.application_info = application_info
        self.application_status = application_status

        running = application_status.get("running", False)
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

        msg = await interaction.followup.send(
            view=LayoutLoading("Reiniciando aplicação...")
        )

        app_id = self.application_info.get("id")

        req = await squarecloud_request.restart_app(app_id)

        if isinstance(req, SquareErrorModel):
            code = req.code
            msg = code if code else "Erro ao Reiniciar aplicação. Tente novamente mais tarde."
            
            return await msg.edit(view=LayoutError(msg))

        req_status = await squarecloud_request.get_app_status(app_id)

        if isinstance(req_status, SquareErrorModel):
            code = req_status.code
            msg = code if code else "Erro ao buscar status da aplicação."
            
            return await msg.edit(view=LayoutError(msg))

        await msg.edit(
            view=LayoutInfo(f"{emoji.check} **|** Aplicação reiniciado com sucesso!")
        )

        application_status = req_status

        await interaction.edit_original_response(
            view=ManageOnlyApplications(self.application_info, application_status)
        )