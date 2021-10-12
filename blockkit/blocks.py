from typing import Dict, List, Optional, Union

from pydantic import Field, root_validator
from pydantic.networks import HttpUrl

from blockkit.components import Component
from blockkit.elements import (
    Button,
    ChannelsSelect,
    Checkboxes,
    ConversationsSelect,
    DatePicker,
    ExternalSelect,
    Image,
    MultiChannelsSelect,
    MultiConversationsSelect,
    MultiExternalSelect,
    MultiStaticSelect,
    MultiUsersSelect,
    Overflow,
    PlainTextInput,
    RadioButtons,
    StaticSelect,
    Timepicker,
    UsersSelect,
)
from blockkit.objects import MarkdownText, PlainText
from blockkit.validators import validate_text_length, validator

__all__ = ["Actions", "Context", "Divider", "Header", "ImageBlock", "Input", "Section"]

ActionElement = Union[
    Button,
    Checkboxes,
    DatePicker,
    StaticSelect,
    MultiStaticSelect,
    ExternalSelect,
    MultiExternalSelect,
    UsersSelect,
    MultiUsersSelect,
    ConversationsSelect,
    MultiConversationsSelect,
    ChannelsSelect,
    MultiChannelsSelect,
    Overflow,
    RadioButtons,
    Timepicker,
]


class Block(Component):
    block_id: Optional[str] = Field(None, min_length=1, max_length=255)


class Actions(Block):
    type: str = "actions"
    elements: List[ActionElement] = Field(..., min_items=1, max_items=5)

    def __init__(
        self, *, elements: List[ActionElement], block_id: Optional[str] = None
    ):
        super().__init__(elements=elements, block_id=block_id)


class Context(Block):
    type: str = "context"
    elements: List[Union[Image, PlainText, MarkdownText, str]] = Field(
        ..., min_items=1, max_items=10
    )

    def __init__(
        self,
        *,
        elements: List[Union[Image, PlainText, MarkdownText, str]],
        block_id: Optional[str] = None,
    ):
        super().__init__(elements=elements, block_id=block_id)


class Divider(Block):
    type: str = "divider"

    def __init__(self, *, block_id: Optional[str] = None):
        super().__init__(block_id=block_id)


class Header(Block):
    type: str = "header"
    text: Union[PlainText, str]

    def __init__(self, *, text: Union[PlainText, str], block_id: Optional[str] = None):
        super().__init__(text=text, block_id=block_id)

    _validate_text = validator("text", validate_text_length, max_length=150)


class ImageBlock(Block):
    type: str = "image"
    image_url: HttpUrl
    alt_text: str = Field(..., min_length=1, max_length=2000)
    title: Union[PlainText, str, None] = None

    def __init__(
        self,
        *,
        image_url: HttpUrl,
        alt_text: str,
        title: Union[PlainText, str, None] = None,
        block_id: Optional[str] = None,
    ):
        super().__init__(
            image_url=image_url, alt_text=alt_text, title=title, block_id=block_id
        )

    _validate_title = validator("title", validate_text_length, max_length=2000)


InputElement = Union[
    PlainTextInput,
    Checkboxes,
    RadioButtons,
    StaticSelect,
    MultiStaticSelect,
    ExternalSelect,
    MultiExternalSelect,
    UsersSelect,
    MultiUsersSelect,
    ConversationsSelect,
    MultiConversationsSelect,
    ChannelsSelect,
    MultiChannelsSelect,
    DatePicker,
]


class Input(Block):
    type: str = "input"
    label: Union[PlainText, str]
    element: InputElement
    dispatch_action: Optional[bool] = None
    hint: Union[PlainText, str, None] = None
    optional: Optional[bool] = None

    def __init__(
        self,
        *,
        label: Union[PlainText, str],
        element: InputElement,
        block_id: Optional[str] = None,
        dispatch_action: Optional[bool] = None,
        hint: Union[PlainText, str, None] = None,
        optional: Optional[bool] = None,
    ):
        super().__init__(
            label=label,
            element=element,
            block_id=block_id,
            dispatch_action=dispatch_action,
            hint=hint,
            optional=optional,
        )

    _validate_label = validator("label", validate_text_length, max_length=2000)
    _validate_hint = validator("hint", validate_text_length, max_length=2000)


AccessoryElement = Union[
    Button,
    Checkboxes,
    DatePicker,
    Image,
    StaticSelect,
    MultiStaticSelect,
    ExternalSelect,
    MultiExternalSelect,
    UsersSelect,
    MultiUsersSelect,
    ConversationsSelect,
    MultiConversationsSelect,
    ChannelsSelect,
    MultiChannelsSelect,
    Overflow,
    RadioButtons,
    Timepicker,
]


class Section(Block):
    type: str = "section"
    text: Union[PlainText, MarkdownText, str, None] = None
    fields_: Optional[List[Union[PlainText, MarkdownText, str]]] = Field(
        None, alias="fields", min_items=1, max_items=10
    )
    accessory: Optional[AccessoryElement] = None

    def __init__(
        self,
        *,
        text: Union[PlainText, MarkdownText, str, None] = None,
        block_id: Optional[str] = None,
        fields: Optional[List[Union[PlainText, MarkdownText, str]]] = None,
        accessory: Optional[AccessoryElement] = None,
    ):
        super().__init__(
            text=text, block_id=block_id, fields=fields, accessory=accessory
        )

    _validate_text = validator("text", validate_text_length, max_length=3000)
    _validate_fields = validator(
        "fields_", validate_text_length, each_item=True, max_length=2000
    )

    @root_validator
    def _validate_values(cls, values: Dict) -> Dict:
        text = values.get("text")
        fields = values.get("fields_")

        if text is None and fields is None:
            raise ValueError("You must provide either text or fields")

        return values
