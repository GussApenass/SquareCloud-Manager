from io import BytesIO
from typing import Any, Dict
import discord
import aiohttp
from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutLoading import LayoutLoading
import base64
from src.components.LayoutView.Database.CertificateDownload import CertificateDownload
from src.components.LayoutView.Database.PasswordResetLayout import PasswordResetLayout

class ResetDbCredenciaisModal(discord.ui.Modal):
    def __init__(self, database_info: Dict[str, Any], db_id: str):
        super().__init__(title="Resetando Credenciais")

        self.type = discord.ui.Label(
            text="Selecione o que deseja Resetar",
            description="Selecione entre Senha do Database e Certificado.",
            component=discord.ui.Select(
                options=[
                    discord.SelectOption(label="Certificados", value="certificate", emoji=emoji.credencial, description="Resete o certificado do Banco de Dados"),
                    discord.SelectOption(label="Password", value="password", emoji=emoji.password, description="Resete a senha do Banco de Dados"),
                ],
                min_values=1,
                max_values=1,
                required=True
            )
        )

        self.add_item(self.type)
        self.db_id = db_id
        self.db_info = database_info

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        loading_msg = await interaction.followup.send(
            view=LayoutLoading("Resetando Credenciais..."),
            ephemeral=True
        )

        type_value = self.type.component.values[0]

        if type_value == "certificate":
            req_reset = await squarecloud_request.reset_db_credenciais(self.db_id, type_value)

            if isinstance(req_reset, SquareErrorModel):
                code = req_reset.code
                msg = code if code else "Erro ao resetar credenciais."

                return await loading_msg.edit(
                    view=LayoutError(msg)
                )

            # CERTIFICAT REQ

            request_certificate = await squarecloud_request.get_db_credenciais(self.db_id)

            if isinstance(request_certificate, SquareErrorModel):
                code = request_certificate.code
                msg = code if code else "Erro ao obter nova credencial."

                return await loading_msg.edit(
                    view=LayoutError(msg)
                )

            base64_cert = request_certificate.get("certificate", None)

            if not base64_cert:
                code = "ERROR_DECODE"

                return await loading_msg.edit(
                    view=LayoutError(code)
                )

            decoded_bytes = base64.b64decode(base64_cert)

            filename = "certificate.pem"

            file = discord.File(
                BytesIO(decoded_bytes),
                filename=filename
            )

            await loading_msg.edit(
                view=CertificateDownload(filename),
                attachments=[file]
            )

        else:
            req_reset = await squarecloud_request.reset_db_credenciais(self.db_id, "password")

            if isinstance(req_reset, SquareErrorModel):
                code = req_reset.code
                msg = code if code else "Erro ao resetar credenciais."

                return await loading_msg.edit(
                    view=LayoutError(msg)
                )

            password = req_reset.get("response", {}).get("password", None)

            if not password:
                code = "PASSWORD_NOT_FOUND"

                return await loading_msg.edit(
                    view=LayoutError(code)
                )

            db_type = self.db_info.get("type", "").lower()
            db_port = self.db_info.get("port")

            config = {
                "postgres": ("postgresql", "squarecloud"),
                "mongodb": ("mongodb", "default"),
                "mysql": ("mysql", "squarecloud"),
                "redis": ("redis", "default")
            }

            scheme, user = config.get(db_type, ("connection", "user"))

            connect_string = f"{scheme}://{user}:{password}@square-cloud-db-{self.db_id}.squareweb.app:{db_port}"

            await loading_msg.edit(
                view=PasswordResetLayout(connect_string, password)
            )