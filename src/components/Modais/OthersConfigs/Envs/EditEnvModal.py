import discord
from base.discord import Modal, TextInput, Label, CheckBox
from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.OthersConfigs.Envs.LayoutManageOnlyEnv import LayoutManageOnlyEnv
from src.components.LayoutView.LayoutLoading import LayoutLoading

class EditEnvModal(Modal):
    def __init__(self, application_id: str, chave_env_antiga: str, valor_env_antigo: str):
        super().__init__(title="Editar Variável")

        self.application_id = application_id
        self.chave_env_antiga = chave_env_antiga
        self.valor_env_antigo = valor_env_antigo

        self.chave_env = Label(
            text="Nome da variável",
            description="O Novo nome da variável, ex: BOT_TOKEN",
            component=TextInput(
                required=False,
                default=chave_env_antiga
            )
        )
        
        self.value_var = Label(
            text="Novo valor da variável",
            description="O novo valor da variáve, ex: MTMQ3M982...",
            component=TextInput(
                required=False,
                default=valor_env_antigo
            )
        )

        self.restart_app = Label(
            text="Deseja Reiniciar a aplicação?",
            description="Selecione esta caixa caso queira que a aplicação seja reiniciada.",
            component=CheckBox(
                default=False
            )
        )
        
    async def on_submit(self, interaction: discord.Interaction):
        await self._parse_custom_interaction(interaction)
        await interaction.response.defer(ephemeral=True)

        if not self.chave_env.text_value and not self.value_var.text_value:
            return await interaction.followup.send(
                view=LayoutError("Você não alterou nada!"),
            )

        nova_chave = self.chave_env.text_value.strip()
        novo_valor = self.value_var.text_value.strip()

        loading_message = await interaction.followup.send(
            view=LayoutLoading("Salvando variáveis..."),
            ephemeral=True
        )

        if not nova_chave and not novo_valor:
            return await loading_message.edit(view=LayoutError("Ué? Como você não quer alterar nada? Era só ter clicado em 'Cancelar'..."))

        if nova_chave != self.chave_env_antiga and nova_chave != "":
            current_envs_res = await squarecloud_request.get_app_envs(self.application_id)

            if isinstance(current_envs_res, SquareErrorModel):
                code = current_envs_res.code
                msg = code if code else "Erro ao buscar variáveis da aplicação."
                
                return await loading_message.edit(
                    view=LayoutError(msg)
                )

            envs_dict = current_envs_res.variables

            if self.chave_env_antiga in envs_dict:
                del envs_dict[self.chave_env_antiga]

            valor_final = novo_valor if novo_valor != "" else self.valor_env_antigo
            envs_dict[nova_chave] = valor_final

            result = await squarecloud_request.update_app_envs(self.application_id, envs_dict)

        elif novo_valor != self.valor_env_antigo and novo_valor != "":
            chave_final = nova_chave if nova_chave != "" else self.chave_env_antiga
            result = await squarecloud_request.set_app_envs(self.application_id, {chave_final: novo_valor})

        else:
            
            return await loading_message.edit(
                view=LayoutError("Ixi... Eu não vi nenhum alteração...")
            )

        if isinstance(result, SquareErrorModel):
            code = result.code
            msg = code if code else "Erro ao ao salvar variáveis da aplicação."

            return await loading_message.edit(
                view=LayoutError(msg)
            )

        await loading_message.edit(
            view=LayoutInfo(f"{emoji.check} Variável **{nova_chave or self.chave_env_antiga}** atualizada com sucesso!")
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
            view=LayoutManageOnlyEnv(self.application_id, nova_chave or self.chave_env_antiga, novo_valor or self.valor_env_antigo)
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if interaction.response.is_done():
            await interaction.followup.send(view=LayoutError(str(error)))
        else:
            await interaction.response.send_message(view=LayoutError(str(error)))