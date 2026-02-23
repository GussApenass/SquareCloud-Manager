import discord
from discord.ui import Modal as OriginalModal
from .components import Label, ComponentType, TextDisplay, TextInput, CheckBox, FileUpload
from base import logger
from typing import List, Dict, Any, Union

class Modal(OriginalModal):
    def __init__(self, *, title: str, timeout: float = None, custom_id: str = None):
        custom_id = custom_id or f"modal_{id(self)}"
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)

    def _get_custom_items(self) -> List[Union[Label, TextDisplay]]:
        items = []
        for value in self.__dict__.values():
            if isinstance(value, (Label, TextDisplay)):
                items.append(value)
        return items

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "title": self.title,
            "custom_id": self.custom_id,
            "components": []
        }

        for child in self.children:
            try:
                payload["components"].append(child.to_component_dict())
            except:
                pass

        custom_items = self._get_custom_items()
        for item in custom_items:
            payload["components"].append(item.to_dict())

        return payload

    async def _parse_custom_interaction(self, interaction: discord.Interaction):
        try:
            data = interaction.data
            if not data:
                logger.warning("Interaction data está vazio.")
                return

            if 'components' not in data:
                logger.warning(f"Chave 'components' não encontrada no data. Chaves disponíveis: {list(data.keys())}")
                return

            resolved = data.get('resolved', {}).get('attachments', {})
            state = interaction._state

            all_custom_items = self._get_custom_items()
            custom_labels = [i for i in all_custom_items if isinstance(i, Label)]

            for comp_idx, comp_data in enumerate(data.get('components', [])):
                c_type = comp_data.get('type')

                if c_type == ComponentType.LABEL:
                    inner_data = comp_data.get('component', {})
                    inner_type = inner_data.get('type')
                    c_id = inner_data.get('custom_id')
                    user_value = inner_data.get('value')

                    target_label = next((l for l in custom_labels 
                                        if l.component and str(l.component.custom_id) == str(c_id)), None)

                    if not target_label or not target_label.component:
                        continue

                    if inner_type == ComponentType.FILE_UPLOAD:
                        if isinstance(target_label.component, FileUpload):
                            v_ids = inner_data.get('values', [])
                            attachments = [
                                discord.Attachment(data=resolved[f_id], state=state)
                                for f_id in v_ids if f_id in resolved
                            ]
                            target_label._values = attachments

                    elif inner_type == ComponentType.TEXT_INPUT:
                        if isinstance(target_label.component, TextInput):
                            target_label.component._value = str(user_value) if user_value is not None else None

                    elif inner_type == ComponentType.CHECKBOX:
                        if isinstance(target_label.component, CheckBox):
                            target_label.component._value = bool(user_value)

        except Exception as e:
            logger.error(f"Erro ao processar interação do modal: {e}", exc_info=True)