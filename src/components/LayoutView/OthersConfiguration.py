import discord
from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutError import LayoutError

class OthersConfiguration(discord.ui.LayoutView):
    def __init__(self, application_id: str):
        super().__init__(timeout=None)

        from src.components.Buttons.ManageApplicationFiles import ManageApplicationFiles
        from src.components.Buttons.BackButton import BackButton
        from src.components.Buttons.OthersConfigs.Envs.ManageEnvsButton import ManageEnvsButtons
        from src.components.Buttons.OthersConfigs.Snapshot.ManageSnapshotsApp import ManageSnapshotsApp
        
        async def return_func(interaction: discord.Interaction):
            await interaction.response.defer()

            from src.components.LayoutView.ManageOnlyApplications import ManageOnlyApplications

            # STATUS REQ

            req_status = await squarecloud_request.get_app_status(application_id)

            if isinstance(req_status, SquareErrorModel):
                code = req_status.code
                msg = code if code else "Erro ao buscar status da aplicação."

                return await interaction.followup.send(view=LayoutError(msg))

            # INFO REQ

            req_info = await squarecloud_request.get_app_info(application_id)

            if isinstance(req_info, SquareErrorModel):
                msg = req_info.code if req_info.code else "Erro ao buscar informações da aplicação."

                return await interaction.followup.send(view=LayoutError(msg))

            # ===

            application_status = req_status
            application_info = req_info

            await interaction.edit_original_response(
                view=ManageOnlyApplications(application_info, application_status)
            )
    
        container1 = discord.ui.Container(
            discord.ui.TextDisplay(content=f"## {emoji.menu} | Outras Configurações"),
            discord.ui.TextDisplay(content="Aqui, você poderá gerenciar configurações secundárias de sua aplicação. \nSelecione o que deseja configurar a baixo."),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.Section(
                discord.ui.TextDisplay(content=f"### {emoji.security} Envs\n- Gerencie as Variáveis de Ambiente de sua aplicação."),
                accessory=ManageEnvsButtons(application_id)
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.Section(
                discord.ui.TextDisplay(content=f"### {emoji.files} Arquivos\n- Gerencie os arquivos de sua aplicação. "),
                accessory=ManageApplicationFiles(application_id)
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.Section(
                discord.ui.TextDisplay(content=f"### {emoji.snapshot} Snapshot\n- Gerencie seus snapshots, crie um snapshot e restaure um snapshot."),
                accessory=ManageSnapshotsApp(application_id)
            ),
            discord.ui.Separator(),
            discord.ui.ActionRow(
                BackButton(return_func)
            ),
            accent_colour=discord.Colour(34047),
        )
        self.add_item(container1)