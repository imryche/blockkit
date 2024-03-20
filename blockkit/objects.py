from typing import List, Optional, Union

from pydantic import AnyUrl, Field, model_validator

from blockkit.components import Component
from blockkit.enums import Include, Style as ConfirmStyle, TriggerActionsOn
from blockkit.validators import validate_text_length, validator

__all__ = [
    "Confirm",
    "DispatchActionConfig",
    "Filter",
    "MarkdownText",
    "PlainOption",
    "MarkdownOption",
    "OptionGroup",
    "PlainText",
    "Text",
    "Style",
    "Emoji",
]


class MarkdownText(Component):
    type: str = "mrkdwn"
    text: str = Field(..., min_length=1)
    verbatim: Optional[bool] = None

    def __init__(self, *, text: str, verbatim: Optional[bool] = None):
        super().__init__(text=text, verbatim=verbatim)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.text == other.text


class PlainText(Component):
    type: str = "plain_text"
    text: str = Field(..., min_length=1)
    emoji: Optional[bool] = None

    def __init__(self, *, text: str, emoji: Optional[bool] = None):
        super().__init__(text=text, emoji=emoji)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.text == other.text


class Style(Component):
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    strike: Optional[bool] = None
    code: Optional[bool] = None

    def __init__(
        self,
        *,
        bold: Optional[bool] = None,
        italic: Optional[bool] = None,
        strike: Optional[bool] = None,
        code: Optional[bool] = None,
    ):
        super().__init__(bold=bold, italic=italic, strike=strike, code=code)


class Text(Component):
    type: str = "text"
    text: str = Field(..., min_length=1)
    style: Optional[Style] = None

    def __init__(self, *, text: str, style: Optional[Style] = None):
        super().__init__(text=text, style=style)


class Emoji(Component):
    type: str = "emoji"
    name: str = Field(..., min_length=1)

    def __init__(self, *, name: str):
        super().__init__(name=name)


class Confirm(Component):
    title: Union[PlainText, str]
    text: Union[PlainText, MarkdownText, str]
    confirm: Union[PlainText, str]
    deny: Union[PlainText, str]
    style: Optional[ConfirmStyle] = None

    def __init__(
        self,
        *,
        title: Union[PlainText, str],
        text: Union[PlainText, MarkdownText, str],
        confirm: Union[PlainText, str],
        deny: Union[PlainText, str],
        style: Optional[ConfirmStyle] = None,
    ):
        super().__init__(
            title=title, text=text, confirm=confirm, deny=deny, style=style
        )

    _validate_title = validator("title", validate_text_length, max_length=100)
    _validate_text = validator("text", validate_text_length, max_length=300)
    _validate_confirm = validator("confirm", validate_text_length, max_length=30)
    _validate_deny = validator("deny", validate_text_length, max_length=30)


class BaseOption(Component):
    value: str = Field(..., min_length=1, max_length=75)
    description: Union[PlainText, str, None] = None
    url: Optional[AnyUrl] = Field(None, max_length=3000)

    def __init__(
        self,
        *,
        text: Union[PlainText, MarkdownText, str],
        value: str,
        description: Optional[Union[PlainText, str]] = None,
        url: Optional[AnyUrl] = None,
    ):
        super().__init__(text=text, value=value, description=description, url=url)

    _validate_description = validator(
        "description", validate_text_length, max_length=75
    )


class PlainOption(BaseOption):
    text: Union[PlainText, str]

    def __init__(
        self,
        *,
        text: Union[PlainText, str],
        value: str,
        description: Optional[Union[PlainText, str]] = None,
        url: Optional[AnyUrl] = None,
    ):
        super().__init__(text=text, value=value, description=description, url=url)

    _validate_text = validator("text", validate_text_length, max_length=75)


class MarkdownOption(BaseOption):
    text: Union[MarkdownText, str]

    def __init__(
        self,
        *,
        text: Union[MarkdownText, str],
        value: str,
        description: Optional[Union[PlainText, str]] = None,
        url: Optional[AnyUrl] = None,
    ):
        super().__init__(text=text, value=value, description=description, url=url)

    _validate_text = validator("text", validate_text_length, max_length=75)


class OptionGroup(Component):
    label: Union[PlainText, str]
    options: List[PlainOption] = Field(..., min_length=1, max_length=100)

    def __init__(self, *, label: Union[PlainText, str], options: List[PlainOption]):
        super().__init__(label=label, options=options)

    _validate_label = validator("label", validate_text_length, max_length=75)


class DispatchActionConfig(Component):
    trigger_actions_on: List[TriggerActionsOn] = Field(..., min_length=1, max_length=2)

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

    @model_validator(mode="after")
    def _validate_values(self) -> "Filter":
        if not any(
            [
                self.include,
                self.exclude_external_shared_channels,
                self.exclude_bot_users,
            ]
        ):
            raise ValueError("You should provide at least one argument.")
        return self
