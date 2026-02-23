import discord
from discord import ui
from io import BytesIO
import base64
from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutLoading import LayoutLoading
from src.components.LayoutView.Database.CertificateDownload import CertificateDownload

class CertificateGetButton(ui.Button):
    def __init__(self, db_id: str):
        self.db_id = db_id

        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji.notebook
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        msg_loading = await interaction.followup.send(
            view=LayoutLoading("Obtendo certificado do banco de dados..."),
            ephemeral=True
        )

        request_certificate = await squarecloud_request.get_db_credenciais(self.db_id)

        if isinstance(request_certificate, SquareErrorModel):
            code = request_certificate.code
            msg = code if code else "Erro ao obter credencial."

            return await msg_loading.edit(
                view=LayoutError(msg)
            )

        base64_cert = request_certificate.get("certificate", None)

        if not base64_cert:
            code = "ERROR_DECODE"

            return await msg_loading.edit(
                view=LayoutError(code)
            )

        decoded_bytes = base64.b64decode(base64_cert)

        filename = "certificate.pem"

        file = discord.File(
            BytesIO(decoded_bytes),
            filename=filename
        )

        await msg_loading.edit(
            view=CertificateDownload(filename),
            attachments=[file]
        )