from base.discord import Modal, TextInput, Label, CheckBox
import discord
import aiohttp
from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.OthersConfigs.Envs.LayoutManageOnlyEnv import LayoutManageOnlyEnv
from src.components.LayoutView.LayoutLoading import LayoutLoading

class CreateNewEnvModal(Modal):
    def __init__(self, application_id: str):
        super().__init__(title="Criando uma VA")

        self.chave_env = Label(
            text="Nome da variável",
            description="O nome da variável, ex: BOT_TOKEN",
            component=TextInput(
                required=True
            )
        )

        self.value_env = Label(
            text="Valor da variável",
            description="O Valor da variável, ex: MTMQ873IU13A...",
            component=TextInput(
                required=True
            )
        )

        self.restart_app = Label(
            text="Deseja Reiniciar a aplicação?",
            description="Selecione esta caixa caso queira que a aplicação seja reiniciada.",
            component=CheckBox(
                default=False
            )
        )
        
        self.application_id = application_id

    async def on_submit(self, interaction: discord.Interaction):
        await self._parse_custom_interaction(interaction)
        await interaction.response.defer(ephemeral=True)

        loading_message = await interaction.followup.send(
            view=LayoutLoading("Criando variável de ambiente..."),
            ephemeral=True
        )

        chave = self.chave_env.text_value
        value = self.value_env.text_value

        if not chave or not value:
            return await loading_message.edit(
                view=LayoutError("Preencha todos os campos!")
            )

        dict = {
            chave: value
        }

        req = await squarecloud_request.set_app_envs(self.application_id, dict)

        if isinstance(req, SquareErrorModel):
            code = req.code
            msg =  code if code else "Erro ao criar variável de ambiente."
            return loading_message.edit(view=LayoutError(msg))

        await loading_message.edit(
            view=LayoutInfo(f"{emoji.check} Variável **{chave}** criada com sucesso!")
        )

        # APPLICATION RESTART

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
            view=LayoutManageOnlyEnv(self.application_id, chave, value)
        )