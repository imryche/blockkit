from typing import List, Optional, Union

from pydantic import Field
from pydantic.class_validators import root_validator

from blockkit.components import Component
from blockkit.enums import Include, Style, TriggerActionsOn
from blockkit.validators import SlackUrl, validate_text_length, validator

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
    text: str = Field(..., min_length=1)
    verbatim: Optional[bool] = None

    def __init__(self, *, text: str, verbatim: Optional[bool] = None):
        super().__init__(text=text, verbatim=verbatim)


class PlainText(Component):
    type: str = "plain_text"
    text: str = Field(..., min_length=1)
    emoji: Optional[bool] = None

    def __init__(self, *, text: str, emoji: Optional[bool] = None):
        super().__init__(text=text, emoji=emoji)


class Confirm(Component):
    title: PlainText
    text: Union[PlainText, MarkdownText]
    confirm: PlainText
    deny: PlainText
    style: Optional[Style] = None

    def __init__(
        self,
        *,
        title: PlainText,
        text: Union[PlainText, MarkdownText],
        confirm: PlainText,
        deny: PlainText,
        style: Optional[Style] = None,
    ):
        super().__init__(
            title=title, text=text, confirm=confirm, deny=deny, style=style
        )

    _validate_title = validator("title", validate_text_length, max_len=100)
    _validate_text = validator("text", validate_text_length, max_len=300)
    _validate_confirm = validator("confirm", validate_text_length, max_len=30)
    _validate_deny = validator("deny", validate_text_length, max_len=30)


class Option(Component):
    text: Union[PlainText, MarkdownText]
    value: str = Field(..., min_length=1, max_length=75)
    description: Optional[PlainText] = None
    url: Optional[SlackUrl] = None

    def __init__(
        self,
        *,
        text: Union[PlainText, MarkdownText],
        value: str,
        description: Optional[PlainText] = None,
        url: Optional[SlackUrl] = None,
    ):
        super().__init__(text=text, value=value, description=description, url=url)

    _validate_text = validator("text", validate_text_length, max_len=75)
    _validate_description = validator("description", validate_text_length, max_len=75)


class OptionGroup(Component):
    label: PlainText
    options: List[Option] = Field(..., min_items=1, max_items=100)

    def __init__(self, *, label: PlainText, options: List[Option]):
        super().__init__(label=label, options=options)

    _validate_label = validator("label", validate_text_length, max_len=75)


class DispatchActionConfig(Component):
    trigger_actions_on: List[TriggerActionsOn] = Field(..., min_items=1, max_items=2)

    def __init__(self, *, trigger_actions_on: List[TriggerActionsOn]):
        super().__init__(trigger_actions_on=trigger_actions_on)


class Filter(Component):
    include: Optional[List[Include]] = None
    exclude_external_shared_channels: Optional[bool] = None
    exclude_bot_users: Optional[bool] = None

    def __init__(
        self,
        *,
        include: Optional[List[Include]] = None,
        exclude_external_shared_channels: Optional[bool] = None,
        exclude_bot_users: Optional[bool] = None,
    ):
        super().__init__(
            include=include,
            exclude_external_shared_channels=exclude_external_shared_channels,
            exclude_bot_users=exclude_bot_users,
        )

    @root_validator
    def _validate_values(cls, values):
        if not any(values.values()):
            raise ValueError("You should provide at least one argument.")
        return values
