import discord
from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutError import LayoutError

class OthersConfigsLayout(discord.ui.LayoutView):
    def __init__(self, database_id: str):
        super().__init__(timeout=None)

        from src.components.Buttons.Database.OthersConfigs.Snapshot.ManageSnapshotsDatabase import ManageSnapshotsDatabase
        from src.components.Buttons.BackButton import BackButton

        async def return_func(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)

            from src.components.LayoutView.Database.ManageOnlyDatabase import ManageOnlyDatabase

            # STATUS REQ

            req_status = await squarecloud_request.get_database_status(database_id)

            if isinstance(req_status, SquareErrorModel):
                code = req_status.code
                msg = code if code else "Erro ao buscar status do database."

                return await interaction.followup.send(view=LayoutError(msg))

            # INFO REQ

            req_info = await squarecloud_request.get_me()

            if isinstance(req_info, SquareErrorModel):
                code = req_info.code
                msg = code if code else "Erro ao buscar informações do database."

                return await interaction.followup.send(view=LayoutError(msg))

            databases = req_info.get("databases", [])

            database_info = next(
                (db for db in databases if db.get("id") == database_id),
                None
            )

            if not database_info:
                return await interaction.followup.send(
                    view=LayoutError("DATABASE_NOT_FOUND"),
                    ephemeral=True
                )

            database_status = req_status

            await interaction.edit_original_response(
                view=ManageOnlyDatabase(database_info, database_status)
            )

        container1 = discord.ui.Container(
            discord.ui.TextDisplay(content=f"## {emoji.menu} | Outras Configurações"),
            discord.ui.TextDisplay(content="Aqui, você poderá gerenciar configurações secundárias de sua aplicação. \nSelecione o que deseja configurar a baixo."),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.Section(
                discord.ui.TextDisplay(content=f"### {emoji.snapshot} Snapshot\n- Gerencie seus snapshots, crie um snapshot e restaure um snapshot."),
                accessory=ManageSnapshotsDatabase(database_id)
            ),
            discord.ui.Separator(),
            discord.ui.ActionRow(
                BackButton(return_func)
            ),
            accent_colour=discord.Colour(34047),
        )
        self.add_item(container1)