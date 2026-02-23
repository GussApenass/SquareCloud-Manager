from typing import Dict, Any
import discord
from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.Buttons.BackButton import BackButton
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.ListApplications import ListApplications
from datetime import datetime
import re

class ManageOnlyApplications(discord.ui.LayoutView):
    def __init__(self, application_info: Dict[str, Any], application_status: Dict[str, Any]):
        super().__init__(timeout=None)

        from src.components.Buttons.TogglerStartOuPauseApplication import TogglerStartOuPauseApplication
        from src.components.Buttons.RestartApplicationButton import RestartApplicationButton
        from src.components.Buttons.GetApplicationLogs import GetApplicationsLogs
        from src.components.Buttons.RefreshApplicationStatus import RefreshApplicationStatus
        from src.components.Buttons.CreateApplicationSnapshot import CreateApplicationSnapshot
        from src.components.Buttons.CommitApplicationButton import CommitApplicationButton
        from src.components.Buttons.DeletApplicationButton import DeleteApplicationButton
        from src.components.Buttons.OutrasConfigsApplication import OutrasConfigsApplication

        # info
    
        application_name = application_info.get("name", "N/A")
        application_id = application_info.get("id", "N/A")
        application_ram_total = application_info.get("ram", "N/A")
        application_created_at = application_info.get("created_at", "N/A")
        application_language = application_info.get("language", "N/A")
        application_tem_dominio = bool(application_info.get("domain"))
        application_dominio = application_info.get("domain", "N/A") if application_tem_dominio else "Nenhum domínio configurado"
    
        dt = datetime.fromisoformat(application_created_at.replace("Z", "+00:00"))
        timestamp_created_at = int(dt.timestamp())
    
        # status
        application_cpu = application_status.get("cpu", "N/A")
        application_network_total = application_status.get("network", {}).get("total", "N/A")
        application_network_now = application_status.get("network", {}).get("now", "N/A")
        application_uptime = application_status.get("uptime", 0) #ms
        is_running = application_status.get("running", False)
    
        raw_ram = application_status.get("ram", "0")
    
        match = re.search(r"[\d.]+", str(raw_ram))
        application_ram_usage = match.group() if match else "0"
    
        if is_running:
            final_text = f"{emoji.online} **Status**: Online\n"
        else:
            final_text = f"{emoji.offline} **Status**: Offline\n"
    
        timestamp_uptime = None
    
        if application_uptime is not None:
            timestamp_uptime = int(application_uptime / 1000)
    
        info_text = (
          f"- {emoji.dados_config} **|** Dados da aplicação:\n"
          f"  - {final_text}"
          f"  - {emoji.date} **Criado em**: <t:{timestamp_created_at}:F> (<t:{timestamp_created_at}:R>)\n"
          f"  - {emoji.application} **Linguagem**: {application_language}\n"
          f"  - {emoji.memory_ram} **Ram**: `{application_ram_usage}/{application_ram_total}MB`\n"
          f"  - {emoji.cpu} **CPU**: `{application_cpu}`\n"
        )
    
        if application_tem_dominio:
          info_text += f"  - {emoji.web} **Domínio**: {application_dominio}\n"
    
        info_text += (
          f"  - {emoji.network} **Network Total**: {application_network_total}\n"
          f"  - {emoji.network} **Network Now**: {application_network_now}\n"
        )
    
        if timestamp_uptime:
            info_text += f"  - {emoji.clock} **Uptime**: <t:{timestamp_uptime}:F> (<t:{timestamp_uptime}:R>)"

        async def return_func(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)

            data = await squarecloud_request.get_me()

            if isinstance(data, SquareErrorModel):
                code = data.code if data.code else "Erro ao buscar aplicações."
                return await interaction.edit_original_response(
                    view=LayoutError(code)
                )

            applications = data["applications"]

            return await interaction.edit_original_response(
                view=ListApplications(applications)
            )
        
        container1 = discord.ui.Container(
            discord.ui.TextDisplay(content=f"## {emoji.rocket} | Gerenciando {application_name}!"),
            discord.ui.TextDisplay(content=f"-# {emoji.id} {application_id}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.Section(
                info_text,
                accessory=RefreshApplicationStatus(application_id)
            ),
            discord.ui.ActionRow(
                    TogglerStartOuPauseApplication(application_info, application_status),
                    RestartApplicationButton(application_info, application_status),
                    GetApplicationsLogs(application_info)
            ),
            discord.ui.ActionRow(
                    CreateApplicationSnapshot(application_info),
                    CommitApplicationButton(application_id),
                    DeleteApplicationButton(application_id),
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.Section(
                discord.ui.TextDisplay(content=f"## {emoji.menu} | Outras Configurações\n- Acesse **configurações secundárias** de sua aplicação."),
                accessory=OutrasConfigsApplication(application_id)
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                BackButton(return_func)
            ),
            accent_colour=discord.Colour(303101),
        )
        self.add_item(container1)