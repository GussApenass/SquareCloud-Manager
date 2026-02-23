from typing import Optional, Dict, Any, List, Union
import discord
import os
import binascii
from discord.utils import MISSING
from .subcomponents import TextInputStyle

class ComponentType:
    TEXT_INPUT = 4
    TEXT_DISPLAY = 10
    ACTION_ROW = 1
    LABEL = 18
    FILE_UPLOAD = 19
    CHECKBOX = 23

class CheckBox:
    def __init__(
        self,
        custom_id: str = MISSING,
        default: bool = False,
    ):
        self.type = ComponentType.CHECKBOX
        if custom_id is MISSING:
            self.custom_id = binascii.hexlify(os.urandom(8)).decode()
        else:
            self.custom_id = custom_id

        self.default = default
        self._value: bool = default

    @property
    def value(self) -> bool:
        return self._value

    @property
    def checked(self) -> bool:
        return self._value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "custom_id": str(self.custom_id),
            "default": self.default,
        }

class TextInput:
    def __init__(
        self,
        style: int = TextInputStyle.short,
        custom_id: str = MISSING,
        placeholder: Optional[str] = None,
        default: Optional[str] = None,
        required: bool = True,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None
    ):
        self.type = ComponentType.TEXT_INPUT
        self.style = style
        
        if custom_id is MISSING:
            self.custom_id = binascii.hexlify(os.urandom(8)).decode()
        else:
            self.custom_id = custom_id
            
        self.placeholder = placeholder
        self.default = default
        self.required = required
        self.min_length = min_length
        self.max_length = max_length
        self._value: Optional[str] = None

    @property
    def value(self) -> Optional[str]:
        return self._value

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "type": self.type,
            "custom_id": str(self.custom_id),
            "style": self.style,
            "required": self.required
        }
        if self.placeholder:
            payload["placeholder"] = self.placeholder
        if self.default:
            payload["value"] = self.default
        if self.min_length:
            payload["min_length"] = self.min_length
        if self.max_length:
            payload["max_length"] = self.max_length

        return payload

class TextDisplay:
    def __init__(self, content: str):
        self.type = ComponentType.TEXT_DISPLAY
        self.content = content

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "content": self.content
        }

class FileUpload:
    def __init__(
        self, 
        custom_id: str = "file_upload", 
        min_values: int = 1, 
        max_values: int = 1, 
        required: bool = True
    ):
        self.type = ComponentType.FILE_UPLOAD
        self.custom_id = custom_id
        self.min_values = min_values
        self.max_values = max_values
        self.required = required

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "custom_id": self.custom_id,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "required": self.required
        }

class Label:
    def __init__(
        self, 
        text: str,
        description: Optional[str] = None, 
        component: Optional[Union[FileUpload, TextInput, CheckBox]] = None
    ):
        self.type = ComponentType.LABEL
        self.label = text
        self.description = description
        self.component = component
        self._values: List[discord.Attachment] = []

    @property
    def text_value(self) -> Optional[str]:
        if isinstance(self.component, TextInput):
            return self.component.value
        return None

    @property
    def checked(self) -> bool:
        if isinstance(self.component, CheckBox):
            return self.component.checked
        return False

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "type": self.type,
            "label": self.label,
        }
        if self.description:
            payload["description"] = self.description
        if self.component:
            payload["component"] = self.component.to_dict()
        return payload

    @property
    def values(self) -> List[discord.Attachment]:
        return self._values