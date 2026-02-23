import discord
from base import emoji, squarecloud_request
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutLoading import LayoutLoading
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.OthersConfigs.Snapshot.LayoutManageSnapshot import LayoutManagerSnapshot
from base.request.models import SquareErrorModel

class RestaurarAppSnapshotModal(discord.ui.Modal):
    def __init__(self, application_id: str, user_id: int, snapshot_id: str, version_id: str):
        super().__init__(timeout=None, title="Confirmação de Restauração")

        self.confirm = discord.ui.TextDisplay(
            content=f" {emoji.delete} Tem certeza que deseja restaurar esta snapshot? Está ação é **IRREVERSÍVEL**. Ao ser restaurar, você não poderá voltar atrás. Pense antes de fazer isto.",
        )

        self.add_item(self.confirm)
        
        self.application_id = application_id
        self.snapshot_id = snapshot_id
        self.version_id = version_id
        self.user_id = user_id

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        loading_msg = await interaction.followup.send(
            view=LayoutLoading("Restaurando snapshot..."),
        )

        result = await squarecloud_request.restore_app_snapshot(self.application_id, self.snapshot_id, self.version_id)

        if isinstance(result, SquareErrorModel):
            code = result.code
            msg = code if code else "Erro ao restaurar snapshot da aplicação."
            return await loading_msg.edit(
                view=LayoutError(msg)
            )

        await loading_msg.edit(
            view=LayoutInfo(f"{emoji.check} **|** Snapshot restaurada com sucesso!")
        )

        # GET SNAPSHOT

        req = await squarecloud_request.get_app_snapshots(self.application_id)

        if isinstance(req, SquareErrorModel):
            code = req.code
            msg = code if code else "Erro ao buscar snapshots."
            return await interaction.followup.send(
                view=LayoutError(msg),
                ephemeral=True
            )

        snapshot_list = req

        await interaction.edit_original_response(
            view=LayoutManagerSnapshot(self.application_id, self.user_id, snapshot_list)
        )
