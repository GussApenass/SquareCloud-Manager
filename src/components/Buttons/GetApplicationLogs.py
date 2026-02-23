import discord
from discord import ui
from typing import Dict, Any
from io import BytesIO
from datetime import datetime

from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutError import LayoutError

class GetApplicationsLogs(ui.Button):
    def __init__(self, application_info: Dict[str, Any]):
        self.application_info = application_info

        super().__init__(
            style=discord.ButtonStyle.primary,
            emoji=emoji.terminal
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        app_id = self.application_info.get("id")
        app_name = self.application_info.get("name", "application")

        req = await squarecloud_request.get_app_logs(app_id)

        if isinstance(req, SquareErrorModel):
            code = req.code
            msg = code if code else "Erro ao buscar logs."
            
            return await interaction.followup.send(view=LayoutError(msg), ephemeral=True)

        logs = req.get("logs", "Sem logs disponíveis no momento.")

        now = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{app_name}_{app_id}_{now}.txt"

        buffer = BytesIO(logs.encode("utf-8"))
        buffer.seek(0)

        ArquivoLogs = discord.File(buffer, filename=filename)

        await interaction.followup.send(
            file=ArquivoLogs,
            ephemeral=True
        )
