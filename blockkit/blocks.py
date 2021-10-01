from typing import List, Optional, Union

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
from blockkit.validators import (
    validate_list_size,
    validate_list_text_length,
    validate_string_length,
    validate_text_length,
    validator,
    validators,
)

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
    block_id: Optional[str] = None

    _validate_block_id = validator("block_id", validate_string_length, max_len=255)


class Actions(Block):
    type: str = "actions"
    elements: List[ActionElement]

    def __init__(
        self, *, elements: List[ActionElement], block_id: Optional[str] = None
    ):
        super().__init__(elements=elements, block_id=block_id)

    _validate_elements = validator("elements", validate_list_size, min_len=1, max_len=5)


class Context(Block):
    type: str = "context"
    elements: List[Union[Image, PlainText, MarkdownText]]

    def __init__(
        self,
        *,
        elements: List[Union[Image, PlainText, MarkdownText]],
        block_id: Optional[str] = None,
    ):
        super().__init__(elements=elements, block_id=block_id)

    _validate_elements = validator(
        "elements", validate_list_size, min_len=1, max_len=10
    )


class Divider(Block):
    type: str = "divider"

    def __init__(self, *, block_id: Optional[str] = None):
        super().__init__(block_id=block_id)


class Header(Block):
    type: str = "header"
    text: PlainText

    def __init__(self, *, text: PlainText, block_id: Optional[str] = None):
        super().__init__(text=text, block_id=block_id)

    _validate_text = validator("text", validate_text_length, max_len=150)


class ImageBlock(Block):
    type: str = "image"
    image_url: HttpUrl
    alt_text: str
    title: Optional[PlainText] = None

    def __init__(
        self,
        *,
        image_url: HttpUrl,
        alt_text: str,
        title: Optional[PlainText] = None,
        block_id: Optional[str] = None,
    ):
        super().__init__(
            image_url=image_url, alt_text=alt_text, title=title, block_id=block_id
        )

    _validate_alt_text = validator("alt_text", validate_string_length, max_len=2000)
    _validate_title = validator("title", validate_text_length, max_len=2000)


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
    label: PlainText
    element: InputElement
    dispatch_action: Optional[bool] = None
    hint: Optional[PlainText] = None
    optional: Optional[bool] = None

    def __init__(
        self,
        *,
        label: PlainText,
        element: InputElement,
        block_id: Optional[str] = None,
        dispatch_action: Optional[bool] = None,
        hint: Optional[PlainText] = None,
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

    _validate_label = validator("label", validate_text_length, max_len=2000)
    _validate_hint = validator("hint", validate_text_length, max_len=2000)


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
    text: Optional[Union[PlainText, MarkdownText]] = None
    fields_: Optional[List[Union[PlainText, MarkdownText]]] = Field(
        None, alias="fields"
    )
    accessory: Optional[AccessoryElement] = None

    def __init__(
        self,
        *,
        text: Optional[Union[PlainText, MarkdownText]] = None,
        block_id: Optional[str] = None,
        fields: Optional[List[Union[PlainText, MarkdownText]]] = None,
        accessory: Optional[AccessoryElement] = None,
    ):
        super().__init__(
            text=text, block_id=block_id, fields=fields, accessory=accessory
        )

    _validate_text = validator("text", validate_text_length, max_len=3000)
    _validate_fields = validators(
        "fields_",
        (validate_list_size, {"min_len": 1, "max_len": 10}),
        (validate_list_text_length, {"max_len": 2000}),
    )

    @root_validator
    def _validate_values(cls, values):
        text = values.get("text")
        fields = values.get("fields_")

        if text is None and fields is None:
            raise ValueError("You must provide either text or fields")

        return values
