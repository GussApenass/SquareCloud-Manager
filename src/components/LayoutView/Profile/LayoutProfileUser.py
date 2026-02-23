import discord
from typing import Dict, Any
from base import emoji
from datetime import datetime

class LayoutProfileUser(discord.ui.LayoutView):
    def __init__(self, UserInfo: Dict[str, Any], is_email_view: bool = False):
        super().__init__(timeout=None)
        self.user_data = UserInfo
        self.is_email_view = is_email_view
        self.render()

    def format_email(self, email: str) -> str:
        try:
            user, domain = email.split('@')
            if len(user) <= 2:
                return f"**@{domain}"
            return f"**{user[-2:]}@{domain}"
        except:
            return "Indisponível"

    def get_plan_emoji(self, plan_name: str):
        plan_name = plan_name.lower()
        if "hobby" in plan_name:
            return emoji.hobby
        elif "standard" in plan_name:
            return emoji.standard
        elif "pro" in plan_name:
            return emoji.pro
        elif "enterprise" in plan_name:
            return emoji.enterprise
        return emoji.plan_default

    def render(self):
        self.clear_items()

        u_id = self.user_data.get("id", "N/A")
        u_name = self.user_data.get("name", "N/A")
        u_email = self.user_data.get("email", "")
        plan = self.user_data.get("plan", {})
        plan_name = plan.get("name").upper()

        mem = plan.get("memory", {})
        used = mem.get("used", 0)
        limit = mem.get("limit", 0)

        display_email = u_email if self.is_email_view else self.format_email(u_email)
        timestamp_expira = int(plan.get('duration', 0) / 1000)
        timestamp_created = int(datetime.fromisoformat(self.user_data['created_at'].replace('Z', '+00:00')).timestamp())
        plan_emoji = self.get_plan_emoji(plan_name)

        formatted_used = f"{used:,}"
        formatted_limit = f"{limit:,}"

        content = (
            f"## {emoji.user} | seu Perfil!\n"
            f"-# {emoji.id} {u_id}\n"
            f"{emoji.tag} **Nome:** {u_name}\n"
            f"{emoji.date} **Criado em:** <t:{timestamp_created}:F> (<t:{timestamp_created}:R>)\n"
        )

        content_plan = (
            f"### {emoji.star} | Sobre sua Assinatura\n"
            f"{plan_emoji} **Plano:** {plan_name}\n"
            f"{emoji.memory_ram} **Memória RAM:** {formatted_used}MB / {formatted_limit}MB utilizados\n"
            f"{emoji.clock} **Expira em:** <t:{timestamp_expira}:F> (<t:{timestamp_expira}:R>)"
        )

        content_email = (
            f"### {emoji.link} | Email\n"
            f"{emoji.email} **Email:** {display_email}"
        )

        from src.components.LayoutView.InitialLayout import InitialLayout
        from src.components.Buttons.Profile.ShowEmailButton import ShowEmailButton

        async def back_callback(interaction: discord.Interaction):
            await interaction.response.defer()
            await interaction.edit_original_response(view=InitialLayout())

        from src.components.Buttons.BackButton import BackButton

        container = discord.ui.Container(
            discord.ui.TextDisplay(content),
            discord.ui.Separator(spacing=discord.SeparatorSpacing.large),
            discord.ui.TextDisplay(content_plan),
            discord.ui.Separator(spacing=discord.SeparatorSpacing.large),
            discord.ui.Section(
                content_email,
                accessory=ShowEmailButton(self.user_data, self.is_email_view)
            ),
            discord.ui.ActionRow(BackButton(back_callback)),
            accent_colour=discord.Colour.blue(),
        )

        self.add_item(container)