import discord
from discord import ui
from typing import Dict, Any
from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutLoading import LayoutLoading
from src.components.LayoutView.ManageOnlyApplications import ManageOnlyApplications

class TogglerStartOuPauseApplication(ui.Button):
    def __init__(self, application_info: Dict[str, Any], application_status: Dict[str, Any]):
        self.application_info = application_info
        self.application_status = application_status

        running = application_status.get("running", False)

        super().__init__(
            emoji=emoji.pause if running else emoji.play,
            style=discord.ButtonStyle.danger if running else discord.ButtonStyle.success
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        app_id = self.application_info.get("id")
        running = self.application_status.get("running", False)

        if running:
            msg = await interaction.followup.send(
                view=LayoutLoading("Parando aplicação..."),
                ephemeral=True
            )
            
            req = await squarecloud_request.stop_app(app_id)
            
        else:
            msg = await interaction.followup.send(
                view=LayoutLoading("Iniciando aplicação..."),
                ephemeral=True
            )
            
            req = await squarecloud_request.start_app(app_id)
            print(f"req running = false {req}")

        if isinstance(req, SquareErrorModel):
            code = req.code
            msg = code if code else "Erro ao alterar estado da aplicação. Verifique se a aplicação já está online ou offline."
            
            return await msg.edit(view=LayoutError(msg))

        # STATUS REQ

        req_status = await squarecloud_request.get_app_status(app_id)

        if isinstance(req_status, SquareErrorModel):
            code = req_status.code
            msg = code if code else "Erro ao buscar status da aplicação."
            
            return await msg.edit(view=LayoutError(msg))

        await msg.edit(
            view=LayoutInfo(f"{emoji.check} **|** Ação realizada com sucesso!")
        )

        await interaction.edit_original_response(
            view=ManageOnlyApplications(self.application_info, req_status)
        )