from typing import List, Optional, Union

from pydantic import Field, model_validator
from pydantic.networks import HttpUrl

from blockkit.components import Component
from blockkit.elements import (
    Button,
    ChannelsSelect,
    Checkboxes,
    ConversationsSelect,
    DatePicker,
    DatetimePicker,
    ExternalSelect,
    FileInput,
    Image,
    MultiChannelsSelect,
    MultiConversationsSelect,
    MultiExternalSelect,
    MultiStaticSelect,
    MultiUsersSelect,
    NumberInput,
    Overflow,
    PlainTextInput,
    RadioButtons,
    RichTextList,
    RichTextPreformatted,
    RichTextQuote,
    RichTextSection,
    StaticSelect,
    TimePicker,
    UsersSelect,
)
from blockkit.objects import MarkdownText, PlainText
from blockkit.validators import (
    validate_list_text_length,
    validate_text_length,
    validator,
)

__all__ = [
    "Actions",
    "Context",
    "Divider",
    "Header",
    "ImageBlock",
    "Input",
    "RichText",
    "Section",
]

ActionElement = Union[
    Button,
    Checkboxes,
    DatePicker,
    DatetimePicker,
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
    TimePicker,
]


class Block(Component):
    block_id: Optional[str] = Field(None, min_length=1, max_length=255)


class Actions(Block):
    type: str = "actions"
    elements: List[ActionElement] = Field(..., min_length=1, max_length=5)

    def __init__(
        self, *, elements: List[ActionElement], block_id: Optional[str] = None
    ):
        super().__init__(elements=elements, block_id=block_id)


class Context(Block):
    type: str = "context"
    elements: List[Union[Image, PlainText, MarkdownText, str]] = Field(
        ..., min_length=1, max_length=10
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
    DatetimePicker,
    TimePicker,
    NumberInput,
    FileInput
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


RichTextElement = Union[
    RichTextList,
    RichTextQuote,
    RichTextPreformatted,
    RichTextSection,
]


class RichText(Block):
    type: str = "rich_text"
    elements: List[RichTextElement] = Field(..., min_length=1)

    def __init__(
        self, *, elements: List[RichTextElement], block_id: Optional[str] = None
    ):
        super().__init__(elements=elements, block_id=block_id)


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
    TimePicker,
]


class Section(Block):
    type: str = "section"
    text: Union[PlainText, MarkdownText, str, None] = None
    fields_: Optional[List[Union[PlainText, MarkdownText, str]]] = Field(
        None, alias="fields", min_length=1, max_length=10
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
    _validate_fields = validator("fields_", validate_list_text_length, max_length=2000)

    @model_validator(mode="after")
    def _validate_values(self) -> "Section":
        if not self.text and not self.fields_:
            raise ValueError("You must provide either text or fields.")
        return self
