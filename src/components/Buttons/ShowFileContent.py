import discord
import io
from base import emoji, squarecloud_request
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutLoading import LayoutLoading

class ShowFileContent(discord.ui.Button):
    def __init__(self, application_id: str, path: str, name: str):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji.file
        )
        self.application_id = application_id
        self.path = path
        self.file_name = name

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        loading_msg = await interaction.followup.send(
            view=LayoutLoading("Buscando conteúdo do arquivo..."),
            ephemeral=True
        )

        result = await squarecloud_request.get_app_file_content(
            self.application_id, 
            self.path
        )

        if result["type"] == "error":
            return await loading_msg.edit(
                view=LayoutError(f"Não consegui baixar o arquivo: {result['content'].code}"),
                ephemeral=True
            )

        if result["type"] == "image":
            await loading_msg.delete()
            
            await interaction.followup.send(
                content=f"{emoji.img} **|** Aqui está a sua imagem!",
                file=result["content"],
                ephemeral=True
            )
        else:
            content_to_send = result["content"]

            data = content_to_send.encode("utf-8") if isinstance(content_to_send, str) else content_to_send

            file_to_send = discord.File(
                io.BytesIO(data), 
                filename=self.file_name
            )

            await loading_msg.delete()

            await interaction.followup.send(
                content=f"{emoji.check} **|** Arquivo gerado com sucesso!",
                file=file_to_send,
                ephemeral=True
            )