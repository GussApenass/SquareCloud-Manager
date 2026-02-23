from typing import Any, Dict
import discord
from base import emoji, squarecloud_request
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutLoading import LayoutLoading
from src.components.LayoutView.Database.ManageOnlyDatabase import ManageOnlyDatabase
from base.request.models import SquareErrorModel

class EditDatabaseInfoModal(discord.ui.Modal):
    def __init__(self, db_id: str, database_info: Dict[str, Any]):
        super().__init__(timeout=None, title="Confirmação de Exclusão")

        self.name = discord.ui.Label(
            text="Novo nome do banco de dados",
            description="Digite o novo nome do banco de dados.",
            component=discord.ui.TextInput(
                max_length=100,
                min_length=1,
                style=discord.TextStyle.short,
                required=False
            )
        )

        self.ram = discord.ui.Label(
            text="Nova ram do banco de dados",
            description="Digite a nova ram do banco de dados.",
            component=discord.ui.TextInput(
                max_length=100,
                min_length=1,
                style=discord.TextStyle.short,
                required=False
            )
        )

        self.add_item(self.name)
        self.add_item(self.ram)

        self.database_info = database_info
        self.database_id = db_id

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        name_raw = self.name.component.value.strip()
        ram_raw = self.ram.component.value.strip()

        loading_msg = await interaction.followup.send(
            view=LayoutLoading("Alterando informações do banco de dados..."),
        )

        if not name_raw and not ram_raw:
            return await loading_msg.edit(
                view=LayoutError(f"{emoji.xred} | Você deve preencher pelo menos **um** campo para editar (Nome ou RAM).")
            )
        
        if ram_raw:
            try:
                ram_value = int(ram_raw)
            except ValueError:
                return await loading_msg.edit(
                    view=LayoutError("A RAM deve ser um número inteiro (ex: 1024)."),
                )

            db_type_value = self.database_info.get("type", "").lower()

            if db_type_value == "redis":
                if ram_value < 512:
                    return await loading_msg.edit(
                        view=LayoutError("Para o **Redis**, o mínimo de RAM permitido é **512MB**.")
                    )
            else:
                if ram_value < 1024:
                    return await loading_msg.edit(
                        view=LayoutError(f"Para o banco {db_type_value.capitalize()}, o mínimo de RAM permitido é **1024MB**."),
                    )
                    
        else:
            ram_value = self.database_info.get("ram")

        db_name = name_raw if name_raw else self.database_info.get("name")

        result = await squarecloud_request.alter_db_info(
            self.database_id,
            db_name,
            ram_value
        )

        if isinstance(result, SquareErrorModel):
            code = result.code
            msg = code if code else "Erro ao alterar informações do banco de dados."
            
            return await loading_msg.edit(
                view=LayoutError(msg)
            )

        # REQ STATUS

        req_status = await squarecloud_request.get_database_status(self.database_id)

        if isinstance(req_status, SquareErrorModel):
            code = req_status.code
            msg = code if code else "Erro ao buscar status da aplicação."

            return await interaction.followup.send(view=LayoutError(msg))

        # REQ INFO

        req_info = await squarecloud_request.get_me()

        if isinstance(req_info, SquareErrorModel):
            code = req_info.code
            msg = code if code else "Erro ao buscar informações do database."
            
            return await interaction.followup.send(view=LayoutError(msg))

        databases = req_info.get("databases", [])

        database_info = next(
            (db for db in databases if db.get("id") == self.database_id),
            None
        )

        if not database_info:
            return await interaction.followup.send(
                view=LayoutError("DATABASE_NOT_FOUND"),
                ephemeral=True
            )

        await loading_msg.edit(
            view=LayoutInfo(f"{emoji.check} **|** Database alterado com sucesso!")
        )

        await interaction.edit_original_response(
            view=ManageOnlyDatabase(database_info, req_status)
        )