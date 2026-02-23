import discord
from base import emoji

class CertificateDownload(discord.ui.LayoutView):
    def __init__(self, filename: str | None = None):
        super().__init__(timeout=None)

        components = [
            discord.ui.TextDisplay(
                content=f"## {emoji.credencial} | Certificado de seu Banco de Dados"
            ),
            discord.ui.TextDisplay(
                content="- O **certificado** de seu database foi generado com sucesso!\n"
                        "-# Siga o anexo abaixo para o download!"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        ]

        if filename:
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
