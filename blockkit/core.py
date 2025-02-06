from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Sequence


class ValidationError(Exception):
    def __init__(self, field_name: str, message: str):
        self.field_name = field_name
        self.message = message
        super().__init__(f"Field '{field_name}': {message}")


class Validator(ABC):
    @abstractmethod
    def validate(self, field_name: str, field_value: Any) -> None:
        pass

    def __call__(self, field_name: str, field_value: Any) -> None:
        return self.validate(field_name, field_value)


class Required(Validator):
    def validate(self, field_name: str, field_value: Any) -> None:
        if field_value is None:
            raise ValidationError(field_name, "Value is required")


class NonEmpty(Validator):
    def validate(self, field_name: str, field_value: Any) -> None:
        if field_value == "":
            raise ValidationError(field_name, "Value cannot be empty")


class MaxLength(Validator):
    def __init__(self, max_length):
        self.max_length = max_length

    def validate(self, field_name: str, field_value: Any) -> None:
        if field_value is not None and len(field_value) > self.max_length:
            raise ValidationError(
                field_name, f"Length must be less or equal {self.max_length}"
            )


class Typed(Validator):
    def __init__(self, *types):
        self.types = types

    def validate(self, field_name: str, field_value: Any) -> None:
        if field_value is not None and not isinstance(field_value, self.types):
            expected_names = ", ".join(c.__name__ for c in self.types)
            got_name = type(field_value).__name__
            raise ValidationError(
                field_name, f"Expected types '{expected_names}', got '{got_name}'"
            )


@dataclass
class Field:
    name: str
    value: Any
    validators: Sequence[Validator] = ()

    def validate(self):
        for validator in self.validators:
            validator(self.name, self.value)


class Component:
    def __init__(self):
        self._fields: dict[str, Field] = {}

    def _add_field(self, name, value, validators: Sequence[Validator] = ()):
        field = Field(name=name, value=value, validators=validators)
        self._fields[name] = field
        return self

    def _get_field_value(self, name: str) -> Any:
        field = self._fields.get(name)
        return field.value if field else None

    def validate(self):
        for field in self._fields.values():
            field.validate()

    def build(self):
        self.validate()
        fields = {field.name: field.value for field in self._fields.values()}
        return {
            k: v.build() if hasattr(v, "build") else v
            for k, v in fields.items()
            if v is not None
        }


class TextObject(Component):
    def __init__(
        self,
        text: str | None = None,
        verbatim: bool | None = None,
    ):
        super().__init__()
        self.text(text)
        self.verbatim(verbatim)

    def __len__(self):
        text = self._get_field_value("text")
        return len(text) if text else 0

    def text(self, text: str):
        return self._add_field(
            "text",
            text,
            validators=[Required(), NonEmpty(), MaxLength(3000)],
        )

    def verbatim(self, verbatim: bool = True):
        return self._add_field("verbatim", verbatim)


class PlainText(TextObject):
    """
    Displays basic text.

    Slack docs:
        https://api.slack.com/reference/block-kit/composition-objects#text
    """

    def __init__(
        self,
        text: str | None = None,
        emoji: bool | None = None,
        verbatim: bool | None = None,
    ):
        super().__init__(text, verbatim)
        self._add_field("type", "plain_text")
        self.emoji(emoji)

    def emoji(self, emoji: bool):
        self._add_field("emoji", emoji)


class MarkdownText(TextObject):
    """
    Displays text formatted as Slack's markdown.

    Slack docs:
        https://api.slack.com/reference/block-kit/composition-objects#text
    """

    def __init__(
        self,
        text: str | None = None,
        emoji: bool | None = None,
        verbatim: bool | None = None,
    ):
        super().__init__(text, verbatim)
        self._add_field("type", "mrkdwn")


class Button(Component):
    """
    Allows users a direct path to performing basic actions.

    Slack docs:
        https://api.slack.com/reference/block-kit/block-elements#button
    """

    def __init__(
        self,
        text: str | PlainText | None = None,
        action_id: str | None = None,
        url: str | None = None,
        value: str | None = None,
        style: str | None = None,
    ):
        super().__init__()
        self._add_field("type", "button")

        self.text(text)
        self.action_id(action_id)
        self.url(url)
        self.value(value)
        self.style(style)

    def text(self, text: str | PlainText):
        if isinstance(text, str):
            text = PlainText(text)

        return self._add_field(
            "text", text, validators=[Typed(PlainText), Required(), MaxLength(75)]
        )

    def action_id(self, action_id: str):
        return self._add_field("action_id", action_id)

    def url(self, url: str):
        return self._add_field("url", url)

    def value(self, value: str):
        return self._add_field("value", value)

    def style(self, style: str):
        return self._add_field("style", style)
