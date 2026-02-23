from base.discord import Modal, FileUpload, Label
import discord
from base import emoji
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.LayoutLoading import LayoutLoading
import aiohttp
from base import squarecloud_request
from src.components.LayoutView.ListApplications import ListApplications

class UploadApplication(Modal):
  def __init__(self):
      super().__init__(title="Upload da Aplicação")

      self.app_upload = Label(
          text="Upload da Aplicação",
          description="Faça o Upload de uma aplicação (arquivo .zip, obrigatoriamente tendo o squarecloud.config)",
          component=FileUpload(
              min_values=1,
              max_values=1,
              required=True
          )
      )

  async def on_submit(self, interaction: discord.Interaction):
    await self._parse_custom_interaction(interaction)
    await interaction.response.defer(ephemeral=True)

    loading_message = await interaction.followup.send(
        view=LayoutLoading("Enviando aplicação..."),
    )

    attachments = self.app_upload.values

    if not attachments:
        return await loading_message.edit(
            f"{emoji.xred} **|** Nenhum arquivo enviado."
        )
        
    try:
        arquivo = attachments[0]
    
        if not arquivo.filename.lower().endswith(".zip"):
            return await loading_message.edit(
                f"{emoji.xred} **|** Apenas arquivos `.zip` são permitidos."
            )
    
        file_bytes = await arquivo.read()
    
        form = aiohttp.FormData()
        form.add_field(
            "file",
            file_bytes,
            filename=arquivo.filename,
            content_type="application/zip"
        )
    
        result = await squarecloud_request.upload_app(file_bytes, arquivo.filename)

        if isinstance(result, SquareErrorModel):
            code = result.code
            msg = code if code else "Erro ao enviar aplicação..."
            
            return await loading_message.edit(view=LayoutError(msg))

        # REQUEST ME

        req_me = await squarecloud_request.get_me()

        if isinstance(req_me, SquareErrorModel):
            code = req_me.code
            msg = code if code else "Erro ao enviar aplicação..."

            return await loading_message.edit(view=LayoutError(msg))

        applications = req_me.get("applications", [])

        await interaction.edit_original_response(
            view=ListApplications(applications)
        )
        
        await loading_message.edit(
            view=LayoutInfo(f"{emoji.check} **|** Aplicação enviada com sucesso!")
        )
        
    except Exception as e:
        await loading_message.edit(view=LayoutError(str(e)))
