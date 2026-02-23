from base.discord import Modal, FileUpload, Label, CheckBox
import discord
import aiohttp
from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.ManageOnlyApplications import ManageOnlyApplications
from src.components.LayoutView.LayoutLoading import LayoutLoading

class CommitApplication(Modal):
    def __init__(self, application_id: str):
        super().__init__(title="Commit da Aplicação")

        self.application_id = application_id

        self.commit_upload = Label(
            text="Arquivo do Commit",
            description="Envie um arquivo ou zip para commitar na aplicação",
            component=FileUpload(
                min_values=1,
                max_values=1,
                required=True
            )
        )

        self.restart_app = Label(
            text="Deseja Reiniciar a aplicação?",
            description="Selecione esta caixa caso queira que a aplicação seja reiniciada.",
            component=CheckBox(
                default=False
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        await self._parse_custom_interaction(interaction)
        await interaction.response.defer(ephemeral=True)

        loading_message = await interaction.followup.send(
            view=LayoutLoading("Enviando commit para a aplicação..."),
            ephemeral=True
        )

        attachments = self.commit_upload.values

        if not attachments:
            return await loading_message.edit(
                view=LayoutError(f"{emoji.xred} **|** Nenhum arquivo enviado.")
            )

        try:
            arquivo: discord.Attachment = attachments[0]

            if not arquivo.filename.lower().endswith(".zip"):
                return await loading_message.edit(
                    view=LayoutError("Apenas arquivos .zip são permitidos para commit.")
                )
            
            file_bytes = await arquivo.read()

            # REQ COMMIT

            result = await squarecloud_request.commit_app(self.application_id, file_bytes, arquivo.filename)

            if isinstance(result, SquareErrorModel):
                code = result.code
                msg = code if code else "Ocorreu um erro ao realizar o commit..."
                
                return await loading_message.edit(
                    view=LayoutError(msg)
                )

            # STATUS REQ

            req_status = await squarecloud_request.get_app_status(self.application_id)

            if isinstance(req_status, SquareErrorModel):
                code = req_status.code
                msg = code if code else "Erro ao buscar status da aplicação."
                return await loading_message.edit(view=LayoutError(msg))

            # INFO REQ

            req_info = await squarecloud_request.get_app_info(self.application_id)

            if isinstance(req_info, SquareErrorModel):
                code = req_info.code
                msg = code if code else "Erro ao buscar informações da aplicação."
                
                return await loading_message.edit(view=LayoutError(msg))

            # RESTART REQ
            
            if self.restart_app.checked:
                loading_restart_message = await interaction.followup.send(
                    view=LayoutLoading("Reiniciando aplicação..."),
                    ephemeral=True
                )

                restart = await squarecloud_request.restart_app(self.application_id)

                if isinstance(restart, SquareErrorModel):
                    code = restart.code
                    msg = code if code else "Erro ao reiniciar aplicação."
                    return await loading_restart_message.edit(view=LayoutError(msg))

                await loading_restart_message.edit(
                    view=LayoutInfo(f"{emoji.check} Aplicação reiniciada com sucesso!")
                )

            # ===

            await interaction.edit_original_response(
                view=ManageOnlyApplications(req_info, req_status)
            )
            
            await loading_message.edit(
                view=LayoutInfo(
                    f"{emoji.check} **|** Commit realizado com sucesso!"
                ),
            )

        except Exception as e:
            await loading_message.edit(
                view=LayoutError(str(e))
            )