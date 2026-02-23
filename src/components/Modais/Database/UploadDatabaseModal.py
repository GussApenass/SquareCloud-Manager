import discord
import base64
from io import BytesIO
from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.Database.ListDatabases import ListDatabases
from src.components.LayoutView.LayoutLoading import LayoutLoading
from src.components.LayoutView.Database.LayoutCreatedApp import LayoutCreatedApp

class UploadDatabaseModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Criando um Banco de Dados")

        self.db_name = discord.ui.Label(
            text="Nome do Banco de Dados",
            description="Digite o nome do banco de dados.",
            component=discord.ui.TextInput(
                min_length=1,
                max_length=100,
                default="Meu Banco de Dados",
                required=True
            )
        )

        self.db_ram = discord.ui.Label(
            text="Ram do Banco de Dados",
            description="Quantidade de Ram do Banco de Dados",
            component=discord.ui.TextInput(
                min_length=1,
                max_length=10,
                default="1024",
                required=True
            )
        )

        self.db_type = discord.ui.Label(
            text="Tipo do Banco de Dados",
            description="Selecione o Tipo do Banco de Dados",
            component=discord.ui.Select(
                options=[
                    discord.SelectOption(label="MongoDB", value="mongo", emoji=emoji.mongodb, description="Banco de dados NoSQL. Requer: 1024mb de Mémoria RAM ou mais"),
                    discord.SelectOption(label="PostgreSQL", value="postgres", emoji=emoji.postgres, description="Banco de dados SQL. Requer: 1024mb de Mémoria RAM ou mais"),
                    discord.SelectOption(label="Redis", value="redis", emoji=emoji.redis, description="Banco de dados NoSQL. Requer: 512mb de Mémoria RAM ou mais"),
                    discord.SelectOption(label="MySQL", value="mysql", emoji=emoji.mysql, description="Banco de dados SQL. Requer: 1024mb de Mémoria RAM ou mais"),
                ],
                min_values=1,
                max_values=1,
                required=True
            )
        )

        self.add_item(self.db_name)
        self.add_item(self.db_ram)
        self.add_item(self.db_type)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        loading_msg = await interaction.followup.send(
            view=LayoutLoading("Criando banco de dados..."),
            ephemeral=True
        )

        try:
            ram_value = int(self.db_ram.component.value)
        except ValueError:
            return await loading_msg.edit(
                view=LayoutError("A RAM deve ser um número inteiro (ex: 1024)."),
            )

        db_type_value = self.db_type.component.values[0]

        if db_type_value == "redis":
            if ram_value < 512:
                return await loading_msg.edit(
                    view=LayoutError("Para o **Redis**, o mínimo de RAM permitido é **512MB**.")
                )
        else:
            if ram_value < 1024:
                return await loading_msg.edit(
                    view=LayoutError(f"Para o banco {db_type_value.capitalize()}, o mínimo de RAM permitido é **1024MB**."),
                )

        db_name = self.db_name.component.value

        # CREATE REQ

        result = await squarecloud_request.create_database(
            db_name,
            ram_value,
            db_type_value
        )

        if isinstance(result, SquareErrorModel):
            code = result.code
            msg = code if code else "Erro ao criar banco de dados."

            return await loading_msg.edit(
                view=LayoutError(msg)
            )

        # ME REQ

        req_me = await squarecloud_request.get_me()

        if isinstance(req_me, SquareErrorModel):
            code = req_me.code
            msg = code if code else "Erro ao buscar informações."

            return await loading_msg.edit(
                view=LayoutError(msg)
            )

        dbs = req_me.get("databases", [])

        # DATABASE CREATED

        connection_string = result.get("connection_url", "N/A")
        password = result.get("password", "N/A")

        base64_cert = result.get("certificate", None)

        if not base64_cert:
            code = "ERROR_DECODE"

            return await loading_msg.edit(
                view=LayoutError(code)
            )

        decoded_bytes = base64.b64decode(base64_cert)

        filename = "certificate.pem"

        file = discord.File(
            BytesIO(decoded_bytes),
            filename=filename
        )

        await loading_msg.edit(
            view=LayoutCreatedApp(connection_string, filename, password),
            attachments=[file]
        )
        
        await interaction.edit_original_response(
            view=ListDatabases(dbs)
        )