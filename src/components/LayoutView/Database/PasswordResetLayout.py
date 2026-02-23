import discord
from base import emoji

class PasswordResetLayout(discord.ui.LayoutView):
    def __init__(self, db_connect_str: str, new_password: str):
        super().__init__(timeout=None)

        components = [
            discord.ui.TextDisplay(
                content=f"## {emoji.password} | Senha do seu Banco de Dados"
            ),
            discord.ui.TextDisplay(
                content="- A nova **senha** de seu database foi gerada com sucesso!\n"
                        f"  - Nova senha: `{new_password}`\n"
                        f"  - String de conexão: `{db_connect_str}`"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        ]

        container = discord.ui.Container(
            *components,
            accent_colour=discord.Colour(291319),
        )

        self.add_item(container)
