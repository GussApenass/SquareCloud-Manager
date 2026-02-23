import discord
from discord import ui
from typing import Dict, Any
from io import BytesIO
import aiohttp

from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutLoading import LayoutLoading

class ConnectionGetButton(ui.Button):
    def __init__(self, db_id: str):
        self.db_id = db_id

        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji.connection
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        msg_loading = await interaction.followup.send(
            view=LayoutLoading("Obtendo dados do banco de dados..."),
            ephemeral=True
        )

        req = await squarecloud_request.get_database(self.db_id)

        if isinstance(req, SquareErrorModel):
            return await interaction.followup.send(
                view=LayoutError(req.code or "Erro ao obter conexão."),
                ephemeral=True
            )

        db_type = req.get("type", "").lower()
        db_id = req.get("id")
        db_port = req.get("port")

        schemes = {
            "postgres": ("postgresql", "squarecloud"),
            "mongodb": ("mongodb", "default"),
            "mysql": ("mysql", "squarecloud"),
            "redis": ("redis", "default")
        }

        scheme, default_user = schemes.get(db_type, ("connection", "user"))
        
        # {scheme}://{user}:<password>@square-cloud-db-{db_id}.squareweb.app:{port}
        connection_url = (
            f"**String de Conexão ({db_type.capitalize()}):**\n"
            f"`{scheme}://{default_user}:<password>@square-cloud-db-{db_id}.squareweb.app:{db_port}`"
        )

        await msg_loading.edit(
            view=LayoutInfo(f"{emoji.security} | Aqui está sua URL de conexão:\n\n{connection_url}\n-# {emoji.warn} Substitua `<password>` pela senha do banco de dados.")
        )