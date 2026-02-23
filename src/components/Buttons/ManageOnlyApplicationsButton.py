
import discord
from discord import ui
from base import emoji, squarecloud_request
from src.components.LayoutView.ManageOnlyApplications import ManageOnlyApplications
from src.components.LayoutView.LayoutError import LayoutError
from base.request.models import SquareErrorModel

class ManageOnlyApplicationButton(ui.Button):
    def __init__(self, application_id: str):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji.menu2
        )
        self.application_id = application_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # STATUS REQ

        req_status = await squarecloud_request.get_app_status(self.application_id)

        if isinstance(req_status, SquareErrorModel):
            code = req_status.code
            msg = code if code else "Erro ao buscar status da aplicação."
            
            return await interaction.followup.send(view=LayoutError(msg))

        # INFO REQ

        req_info = await squarecloud_request.get_app_info(self.application_id)

        if isinstance(req_info, SquareErrorModel):
            msg = req_info.code if req_info.code else "Erro ao buscar informações da aplicação."
            
            return await interaction.followup.send(view=LayoutError(msg))

        # ===

        application_status = req_status
        application_info = req_info

        await interaction.edit_original_response(
            view=ManageOnlyApplications(application_info, application_status)
        )