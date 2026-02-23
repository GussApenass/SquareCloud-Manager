import discord
from base import emoji

class LayoutCreatedApp(discord.ui.LayoutView):
    def __init__(self, connection_string: str, filename: str, password: str):
        super().__init__(timeout=None)

        components = [
            discord.ui.TextDisplay(
                content=f"## {emoji.database} | Database criada com sucesso!"
            ),
            discord.ui.TextDisplay(
                content="- O seu database foi criada com sucesso!\n"
                        "A string de **conexão** e o **certificado**, estão logo a baixo!"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        ]

        components.append(
            discord.ui.TextDisplay(
                f"- {emoji.password} Senha do banco de dados: `{password}`\n"
                f"`{connection_string}`"
            )
        )

        components.append(
            discord.ui.File(
                media=f"attachment://{filename}"
            )
        )

        container = discord.ui.Container(
            *components,
            accent_colour=discord.Colour(291319),
        )

        self.add_item(container)
