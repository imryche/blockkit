from typing import List, Optional, Union

from pydantic.class_validators import root_validator
from pydantic.networks import AnyUrl

from blockkit.components import Component
from blockkit.validators import (
    validate_choices,
    validate_list_choices,
    validate_list_size,
    validate_string_length,
    validate_text_length,
    validator,
    validators,
)

__all__ = [
    "Confirm",
    "DispatchActionConfig",
    "Filter",
    "MarkdownText",
    "Option",
    "OptionGroup",
    "PlainText",
]


class MarkdownText(Component):
    type: str = "mrkdwn"
    text: str
    verbatim: Optional[bool] = None

    def __init__(self, *, text: str, verbatim: Optional[bool] = None):
        super().__init__(text=text, verbatim=verbatim)


class PlainText(Component):
    type: str = "plain_text"
    text: str
    emoji: Optional[bool] = None

    def __init__(self, *, text: str, emoji: Optional[bool] = None):
        super().__init__(text=text, emoji=emoji)


class Confirm(Component):
    title: PlainText
    text: Union[PlainText, MarkdownText]
    confirm: PlainText
    deny: PlainText
    style: Optional[str] = None

    def __init__(
        self,
        *,
        title: PlainText,
        text: Union[PlainText, MarkdownText],
        confirm: PlainText,
        deny: PlainText,
        style: Optional[str] = None,
    ):
        super().__init__(
            title=title, text=text, confirm=confirm, deny=deny, style=style
        )

    _validate_title = validator("title", validate_text_length, max_len=100)
    _validate_text = validator("text", validate_text_length, max_len=300)
    _validate_confirm = validator("confirm", validate_text_length, max_len=30)
    _validate_deny = validator("deny", validate_text_length, max_len=30)
    _validate_style = validator(
        "style", validate_choices, choices=("primary", "danger")
    )


class Option(Component):
    text: Union[PlainText, MarkdownText]
    value: str
    description: Optional[PlainText] = None
    url: Optional[AnyUrl] = None

    def __init__(
        self,
        *,
        text: Union[PlainText, MarkdownText],
        value: str,
        description: Optional[PlainText] = None,
        url: Optional[AnyUrl] = None,
    ):
        super().__init__(text=text, value=value, description=description, url=url)

    _validate_text = validator("text", validate_text_length, max_len=75)
    _validate_value = validator("value", validate_string_length, max_len=75)
    _validate_description = validator("description", validate_text_length, max_len=75)
    _validate_url = validator("url", validate_string_length, max_len=3000)


class OptionGroup(Component):
    label: PlainText
    options: List[Option]

    def __init__(self, *, label: PlainText, options: List[Option]):
        super().__init__(label=label, options=options)

    _validate_label = validator("label", validate_text_length, max_len=75)
    _validate_options = validator("options", validate_list_size, min_len=1, max_len=100)


class DispatchActionConfig(Component):
    trigger_actions_on: List[str]

    def __init__(self, *, trigger_actions_on: List[str]):
        super().__init__(trigger_actions_on=trigger_actions_on)

    _validate_trigger_actions_on = validators(
        "trigger_actions_on",
        (validate_list_size, dict(min_len=1, max_len=2)),
        (
            validate_list_choices,
            dict(choices=("on_enter_pressed", "on_character_entered")),
        ),
    )


class Filter(Component):
    include: Optional[List[str]] = None
    exclude_external_shared_channels: Optional[bool] = None
    exclude_bot_users: Optional[bool] = None

    def __init__(
        self,
        *,
        include: Optional[List[str]] = None,
        exclude_external_shared_channels: Optional[bool] = None,
        exclude_bot_users: Optional[bool] = None,
    ):
        super().__init__(
            include=include,
            exclude_external_shared_channels=exclude_external_shared_channels,
            exclude_bot_users=exclude_bot_users,
        )

    _validate_include = validator(
        "include", validate_list_choices, choices=("im", "mpim", "private", "public")
    )

    @root_validator
    def _validate_values(cls, values):
        if not any(values.values()):
            raise ValueError("You should provide at least one argument.")
        return values
