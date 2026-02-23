from typing import Dict, Any
import discord
from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.Buttons.BackButton import BackButton
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.Database.ListDatabases import ListDatabases 
from datetime import datetime
import re

class ManageOnlyDatabase(discord.ui.LayoutView):
    def __init__(self, database_info: Dict[str, Any], database_status: Dict[str, Any]):
        super().__init__(timeout=None)

        from src.components.Buttons.Database.ToggleStartOuPauseDatabase import TogglerStartOuPauseDatabase
        from src.components.Buttons.Database.RestartDatabaseButton import RestartDatabaseButton
        from src.components.Buttons.Database.RefreshDatabaseStatus import RefreshDatabaseStatus
        from src.components.Buttons.Database.CreateDatabaseSnapshot import CreateDatabaseSnapshot
        from src.components.Buttons.Database.DeleteDatabaseButton import DeleteDatabaseButton
        from src.components.Buttons.Database.OthersConfigsDatabase import OthersConfigsDatabases
        from src.components.Buttons.Database.ConnectionGetButton import ConnectionGetButton
        from src.components.Buttons.Database.ResetDbCredenciais import ResetDbCredenciais
        from src.components.Buttons.Database.EditDatabaseInfo import EditDatabaseInfo
        from src.components.Buttons.Database.CertificateGetButton import CertificateGetButton

        db_name = database_info.get("name", "N/A")
        db_id = database_info.get("id", "N/A")
        db_ram_total = database_info.get("ram", "N/A")
        db_created_at = database_info.get("created_at", "N/A")
        db_type = database_info.get("type", "unknown").lower()
        db_cluster = database_info.get("cluster", "N/A")

        dt = datetime.fromisoformat(db_created_at.replace("Z", "+00:00"))
        timestamp_created_at = int(dt.timestamp())

        formatted_types = {
            "mongodb": f"{emoji.mongodb} MongoDB",
            "postgres": f"{emoji.postgres} Postgres",
            "redis": f"{emoji.redis} Redis",
            "mysql": f"{emoji.mysql} MySQL"
        }
        type_display = formatted_types.get(db_type, f"{db_type.capitalize()}")

        db_cpu = database_status.get("cpu", "N/A")
        db_storage = database_status.get("storage", "N/A")
        db_network_total = database_status.get("network", {}).get("total", "N/A")
        db_network_now = database_status.get("network", {}).get("now", "N/A")
        db_uptime_ms = database_status.get("uptime")
        is_running = database_status.get("running", False)

        raw_ram_usage = database_status.get("ram", "0")
        match = re.search(r"[\d.]+", str(raw_ram_usage))
        db_ram_usage = match.group() if match else "0"

        status_icon = emoji.online if is_running else emoji.offline
        status_text = "Online" if is_running else "Offline"

        timestamp_uptime = int(db_uptime_ms / 1000) if db_uptime_ms else None

        info_text = (
            f"- {emoji.dados_config} **|** Dados do Banco:\n"
            f"  - {status_icon} **Status**: {status_text}\n"
            f"  - {emoji.date} **Criado em**: <t:{timestamp_created_at}:F>\n"
            f"  - {emoji.type} **Tipo**: {type_display}\n"
            f"  - {emoji.cluster} **Cluster**: `{db_cluster}`\n"
            f"  - {emoji.memory_ram} **RAM**: `{db_ram_usage}/{db_ram_total}MB`\n"
            f"  - {emoji.cpu} **CPU**: `{db_cpu}`\n"
            f"  - {emoji.diskcard} **Storage**: `{db_storage}`\n"
            f"  - {emoji.network} **Network Total**: {db_network_total}\n"
            f"  - {emoji.network} **Network Atual**: {db_network_now}\n"
        )

        if timestamp_uptime:
            info_text += f"  - {emoji.clock} **Uptime**: <t:{timestamp_uptime}:F> (<t:{timestamp_uptime}:R>)"

        async def return_func(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            data = await squarecloud_request.get_me()

            if isinstance(data, SquareErrorModel):
                return await interaction.edit_original_response(
                    view=LayoutError(data.code or "Erro ao buscar bancos.")
                )

            dbs = data.get("databases", [])

            return await interaction.edit_original_response(
                view=ListDatabases(dbs)
            )

        container1 = discord.ui.Container(
            discord.ui.TextDisplay(content=f"## {emoji.database} | Gerenciando Database: {db_name}"),
            discord.ui.TextDisplay(content=f"-# {emoji.id} {db_id}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.Section(
                info_text,
                accessory=RefreshDatabaseStatus(db_id)
            ),
            discord.ui.ActionRow(
                TogglerStartOuPauseDatabase(database_info, database_status),
                RestartDatabaseButton(database_info, database_status),
                CreateDatabaseSnapshot(database_info),
                ConnectionGetButton(db_id),
                ResetDbCredenciais(db_id)
            ),
            discord.ui.ActionRow(
                EditDatabaseInfo(db_id, database_info),
                CertificateGetButton(db_id),
                DeleteDatabaseButton(db_id)
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.Section(
                discord.ui.TextDisplay(content=f"## {emoji.menu} | Configurações Adicionais\n- Gerencie snapshots do banco de dados"),
                accessory=OthersConfigsDatabases(db_id)
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                BackButton(return_func)
            ),
            accent_colour=discord.Colour(4519199),
        )
        self.add_item(container1)