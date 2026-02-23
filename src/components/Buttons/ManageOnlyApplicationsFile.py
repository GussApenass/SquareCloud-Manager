import discord
from discord import ui
from base import emoji, squarecloud_request
from typing import Dict, Any
from base.request.models.SquareError import SquareErrorModel
from src.components.LayoutView.LayoutManageOnlyFile import LayoutManageOnlyFile
from src.components.LayoutView.LayoutError import LayoutError

class ManageOnlyApplicationFile(ui.Button):
    def __init__(self, application_id: str, file_data: Dict[str, Any], type_file: str, path: str):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji.file if type_file == "file" else emoji.files
        )
        self.application_id = application_id
        self.file_data = file_data
        self.path = path
        self.type_file = type_file

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if self.type_file == "directory":
            from src.components.LayoutView.LayoutManagerApplicationsFiles import LayoutManagerApplicationsFiles


            result = await squarecloud_request.get_app_files(self.application_id, self.path)

            if isinstance(result, SquareErrorModel):
                code = result.code
                msg = code if code else "Erro ao buscar arquivos."
                return await interaction.followup.send(view=LayoutError(msg), ephemeral=True)
                
            files_dict = [item.dict() for item in result]

            new_view = LayoutManagerApplicationsFiles(
                self.application_id, 
                files_dict, 
                self.path
            )
            
            return await interaction.edit_original_response(view=new_view)

        await interaction.edit_original_response(view=LayoutManageOnlyFile(self.application_id, self.file_data, self.path))