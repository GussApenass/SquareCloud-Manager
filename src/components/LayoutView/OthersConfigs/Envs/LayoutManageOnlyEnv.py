import discord
from base import emoji, squarecloud_request
from src.components.LayoutView.LayoutError import LayoutError
from base.request.models import SquareErrorModel

class LayoutManageOnlyEnv(discord.ui.LayoutView):
    def __init__(self, application_id: str, env_key: str, env_value: str):
        super().__init__(timeout=None)

        self.application_id = application_id
        self.env_key = env_key
        self.env_value = env_value

        self.render()

    def render(self):
        from src.components.Buttons.OthersConfigs.Envs.EditEnvButton import EditEnvButton
        from src.components.Buttons.OthersConfigs.Envs.DeleteEnvButton import DeleteEnvButton
        from src.components.LayoutView.OthersConfigs.Envs.LayoutManagerEnvs import LayoutManagerApplicationsEnvs
        from src.components.Buttons.BackButton import BackButton

        main_text = (
            f"- {emoji.dados_config} **Configuração Atual:**\n"
            f"  - {emoji.network} **Chave**: `{self.env_key}`\n"
            f"  - {emoji.next} **Valor**: ||`{self.env_value}`||"
        )

        async def return_func(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)

            request = await squarecloud_request.get_app_envs(self.application_id)

            if isinstance(request, SquareErrorModel):
                msg = request.code if request.code else "Erro ao buscar variáveis de ambiente."
                return await interaction.edit_original_response(view=LayoutError(msg))

            envs_dict = request

            await interaction.edit_original_response(
                view=LayoutManagerApplicationsEnvs(self.application_id, envs_dict)
            )

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"## {emoji.network} | Gerenciando Variável"),
            discord.ui.Separator(spacing=discord.SeparatorSpacing.small),

            discord.ui.TextDisplay(content=main_text),

            discord.ui.ActionRow(
                EditEnvButton(self.application_id, self.env_key, self.env_value),
                DeleteEnvButton(self.application_id, self.env_key)
            ),

            discord.ui.Separator(spacing=discord.SeparatorSpacing.small),

            discord.ui.ActionRow(
                BackButton(return_func)
            ),
            accent_colour=discord.Colour(4519199),
        )

        self.add_item(container)