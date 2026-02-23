import discord
from discord import ui
from typing import Dict, Any
from io import BytesIO
import aiohttp

from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutLoading import LayoutLoading
from src.components.LayoutView.LayoutSnapshotDownload import LayoutSnapshotDownload

MAX_DISCORD_FILE = 10 * 1024 * 1024

class CreateApplicationSnapshot(ui.Button):
    def __init__(self, application_info: Dict[str, Any]):
        self.application_info = application_info

        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji.download
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        app_id = self.application_info["id"]

        loading_msg = await interaction.followup.send(
            view=LayoutLoading("Criando snapshot..."),
            ephemeral=True
        )

        req = await squarecloud_request.create_app_snapshot(app_id)

        if isinstance(req, SquareErrorModel):
            code = req.code
            msg = str(code) if code else "Erro ao criar snapshot."
            
            return await loading_msg.edit(
                view=LayoutError(msg)
            )

        url = req.get("url", None)

        if not url:
            await loading_msg.edit(
                view=LayoutError("URL do snapshot não encontrada.")
            )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    size = int(resp.headers.get("Content-Length", 0))

                    if size > MAX_DISCORD_FILE:
                        return await loading_msg.edit(
                            view=LayoutSnapshotDownload(url)
                        )

                    data = await resp.read()

        except Exception:
            return await loading_msg.edit(
                view=LayoutSnapshotDownload(url)
            )

        filename = f"snapshot_{app_id}.zip"

        file = discord.File(
            BytesIO(data),
            filename=filename
        )

        await loading_msg.edit(
            view=LayoutSnapshotDownload(url, filename),
            attachments=[file]
        )