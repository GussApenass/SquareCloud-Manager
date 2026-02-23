import discord
from base import emoji, squarecloud_request
from base.discord import Modal, TextDisplay, Label, CheckBox
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.LayoutLoading import LayoutLoading
from src.components.LayoutView.OthersConfigs.Envs.LayoutManagerEnvs import LayoutManagerApplicationsEnvs
from base.request.models import SquareErrorModel

class ConfirmDeleteEnv(Modal):
    def __init__(self, application_id: str, chave: str):
        super().__init__(timeout=None, title="Confirmação de Exclusão")

        self.confirm = TextDisplay(
            content=f" {emoji.delete} Tem certeza que deseja esta variável de ambiente? Está ação é **IRREVERSÍVEL**. Ao ser deletado, você nunca mais poderá recuperar esta variável de ambiente.",
        )

        self.restart_app = Label(
            text="Deseja Reiniciar a aplicação?",
            description="Selecione esta caixa caso queira que a aplicação seja reiniciada.",
            component=CheckBox(
                default=False
            )
        )
        
        self.application_id = application_id
        self.chave = chave

    async def on_submit(self, interaction: discord.Interaction):
        await self._parse_custom_interaction(interaction)
        await interaction.response.defer()

        loading_message = await interaction.followup.send(
            view=LayoutLoading("Deletando variável..."),
        )

        list = [self.chave]

        req = await squarecloud_request.delete_app_envs(self.application_id, list)

        if isinstance(req, SquareErrorModel):
            code = req.code
            msg = code if code else "Erro ao deletar variável de ambiente."

            return await loading_message.edit(
                view=LayoutError(msg),
            )

        await loading_message.edit(
            view=LayoutInfo(f"{emoji.check} Variável **{self.chave}** deletada com sucesso!")
        )

        # REQ GET ENVS

        request = await squarecloud_request.get_app_envs(self.application_id)

        if isinstance(request, SquareErrorModel):
            code = request.code
            msg = code if code else "Erro ao buscar variáveis de ambiente."
            return await loading_message.edit(view=LayoutError(msg))

        # RESTART APPLICATION

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

        await interaction.edit_original_response(
            view=LayoutManagerApplicationsEnvs(self.application_id, request)
        )
