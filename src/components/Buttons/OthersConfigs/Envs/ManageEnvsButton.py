import discord
from discord import ui
from typing import Dict, Any
from base import emoji, squarecloud_request
from src.components.LayoutView.OthersConfigs.Envs.LayoutManagerEnvs import LayoutManagerApplicationsEnvs
from src.components.LayoutView.LayoutError import LayoutError
from base.request.models import SquareErrorModel

class ManageEnvsButtons(ui.Button):
    def __init__(self, application_id: str):
        self.application_id = application_id

        super().__init__(
            emoji=emoji.menu2,
            style=discord.ButtonStyle.secondary
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        request = await squarecloud_request.get_app_envs(self.application_id)

        if isinstance(request, SquareErrorModel):
            code = request.code
            msg = code if code else "Erro ao buscar variáveis de ambiente."
            return await interaction.followup.send(view=LayoutError(msg))

        envs_dict = request

        await interaction.edit_original_response(
            view=LayoutManagerApplicationsEnvs(self.application_id, envs_dict)
        )