from abc import ABC, abstractmethod
from dataclasses import dataclass, field
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


class Values(Validator):
    def __init__(self, *values: Sequence[str]):
        self.values = values

    def validate(self, field_name: str, field_value: Any) -> None:
        if field_value is not None and field_value not in self.values:
            expected_values = ", ".join(self.values)
            raise ValidationError(
                field_name, f"Expected values '{expected_values}', got '{field_value}'"
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


def str_to_plain(value: str) -> "PlainText":
    if isinstance(value, str):
        return PlainText(value)
    return value


@dataclass
class Field:
    name: str
    value: Any
    validators: Sequence[Validator] = field(default_factory=list)

    def validate(self):
        for validator in self.validators:
            validator(self.name, self.value)


class Component:
    def __init__(self):
        self._fields: dict[str, Field] = {}

    def _add_field(self, name, value, validators: Sequence[Validator] = None):
        if not validators:
            validators = []
        field = Field(name=name, value=value, validators=validators)
        self._fields[name] = field
        return self

    def _add_validator(self, field_name: str, validator: Validator) -> None:
        if field_name not in self._fields:
            raise ValueError(f"No '{field_name}' field found")

        self._fields[field_name].validators.append(validator)

    def _get_field_value(self, field_name: str) -> Any:
        field = self._fields.get(field_name)
        return field.value if field else None

    def validate(self):
        for field_ in self._fields.values():
            field_.validate()

    def build(self):
        self.validate()
        fields = {field.name: field.value for field in self._fields.values()}
        return {
            k: v.build() if hasattr(v, "build") else v
            for k, v in fields.items()
            if v is not None
        }


"""
Composition objects:

x Confirmation dialog (Confirm) - https://api.slack.com/reference/block-kit/composition-objects#confirm
- Conversation filter (ConversationFilter) - https://api.slack.com/reference/block-kit/composition-objects#filter_conversations
- Dispatch action configuration (DispatchActionConfig) - https://api.slack.com/reference/block-kit/composition-objects#dispatch_action_config
- Option (Option) - https://api.slack.com/reference/block-kit/composition-objects#option
- Option group (OptionGroup) - https://api.slack.com/reference/block-kit/composition-objects#option_group
- Text (Text) - https://api.slack.com/reference/block-kit/composition-objects#text
- Trigger (Trigger) - https://api.slack.com/reference/block-kit/composition-objects#trigger
- Workflow (Workflow) - https://api.slack.com/reference/block-kit/composition-objects#workflow
- Slack file (SlackFile) - https://api.slack.com/reference/block-kit/composition-objects#slack_file

Block elements:

- Button (Button) - https://api.slack.com/reference/block-kit/block-elements#button
- Checkboxes (Checkboxes) - https://api.slack.com/reference/block-kit/block-elements#checkboxes
- Date picker (DatePicker) - https://api.slack.com/reference/block-kit/block-elements#datepicker
- Datetime picker (DatetimePicker) - https://api.slack.com/reference/block-kit/block-elements#datetimepicker
- Email input (EmailInput) - https://api.slack.com/reference/block-kit/block-elements#email
- Image (ImageEl) - https://api.slack.com/reference/block-kit/block-elements#image
- Multi-select static (MultiStaticSelect) - https://api.slack.com/reference/block-kit/block-elements#static_multi_select
- Multi-select external (MultiExternalSelect) - https://api.slack.com/reference/block-kit/block-elements#external_multi_select
- Multi-select users (MultiUsersSelect) - https://api.slack.com/reference/block-kit/block-elements#users_multi_select
- Multi-select conversations (MultiConversationsSelect) - https://api.slack.com/reference/block-kit/block-elements#conversation_multi_select
- Multi-select channels (MultiChannelsSelect) - https://api.slack.com/reference/block-kit/block-elements#channel_multi_select
- Number input (NumberInput) - https://api.slack.com/reference/block-kit/block-elements#number
- Overflow menu (Overflow) - https://api.slack.com/reference/block-kit/block-elements#overflow
- Plain-text input (PlainTextInput) - https://api.slack.com/reference/block-kit/block-elements#input
- Radio buttons (RadioButtons) - https://api.slack.com/reference/block-kit/block-elements#radio
- Rich text input (RichTextInput) - https://api.slack.com/reference/block-kit/block-elements#rich_text_input
- Select static (StaticSelect) - https://api.slack.com/reference/block-kit/block-elements#static_select
- Select external (ExternalSelect) - https://api.slack.com/reference/block-kit/block-elements#external_select
- Select users (UsersSelect) - https://api.slack.com/reference/block-kit/block-elements#users_select
- Select conversations (ConversationsSelect) - https://api.slack.com/reference/block-kit/block-elements#conversations_select
- Select channels (ChannelsSelect) - https://api.slack.com/reference/block-kit/block-elements#channels_select
- Time picker (TimePicker) - https://api.slack.com/reference/block-kit/block-elements#timepicker
- URL input (UrlInput) - https://api.slack.com/reference/block-kit/block-elements#url
- Workflow button (WorkflowButton) - https://api.slack.com/reference/block-kit/block-elements#workflow_button

Blocks:

- Actions (Actions) - https://api.slack.com/reference/block-kit/blocks#actions
- Context (Context) - https://api.slack.com/reference/block-kit/blocks#context
- Divider (Divider) - https://api.slack.com/reference/block-kit/blocks#divider
- File (File) - https://api.slack.com/reference/block-kit/blocks#file
- Header (Header) - https://api.slack.com/reference/block-kit/blocks#header
- Image (Image) - https://api.slack.com/reference/block-kit/blocks#image
- Input (Input) - https://api.slack.com/reference/block-kit/blocks#input
- Markdown (Markdown) - https://api.slack.com/reference/block-kit/blocks#markdown
- Rich text (RichText) - https://api.slack.com/reference/block-kit/blocks#rich_text
- Rich text section (RichTextSection) - https://api.slack.com/reference/block-kit/blocks#rich_text_section
- Rich text list (RichTextList) - https://api.slack.com/reference/block-kit/blocks#rich_text_list
- Rich text preformatted (RichTextPreformatted) - https://api.slack.com/reference/block-kit/blocks#rich_text_preformatted
- Rich text quote (RichTextQuote) - https://api.slack.com/reference/block-kit/blocks#rich_text_quote
- Rich broadcast (RichBroadcast) - https://api.slack.com/reference/block-kit/blocks#broadcast-element-type
- Rich color (RichColor) - https://api.slack.com/reference/block-kit/blocks#color-element-type
- Rich channel (RichChannel) - https://api.slack.com/reference/block-kit/blocks#channel-element-type
- Rich date (RichDate) - https://api.slack.com/reference/block-kit/blocks#date-element-type
- Rich emoji (RichEmoji) - https://api.slack.com/reference/block-kit/blocks#emoji-element-type
- Rich link (RichLink) - https://api.slack.com/reference/block-kit/blocks#link-element-type
- Rich text (RichText) - https://api.slack.com/reference/block-kit/blocks#text-element-type
- Rich user (RichUser) - https://api.slack.com/reference/block-kit/blocks#user-element-type
- Rich usergroup (RichUsergroup) - https://api.slack.com/reference/block-kit/blocks#user-group-element-type
- Rich style (RichStyle) - ...
- Section (Section) - https://api.slack.com/reference/block-kit/blocks#section
- Video (Video) - https://api.slack.com/reference/block-kit/blocks#video

"""

"""
Composition objects
"""


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


class Confirm(Component):
    """
    Confirmation dialog

    Defines a dialog that adds a confirmation step to interactive elements.

    Slack docs:
        https://api.slack.com/reference/block-kit/composition-objects#confirm
    """

    def __init__(
        self,
        title: str | PlainText | None = None,
        text: str | PlainText | None = None,
        confirm: str | PlainText | None = None,
        deny: str | PlainText | None = None,
        style: str | None = None,
    ):
        super().__init__()
        self.title(title)
        self.text(text)
        self.confirm(confirm)
        self.deny(deny)
        self.style(style)

    def title(self, title: str | PlainText) -> "Confirm":
        self._add_field(
            "title",
            str_to_plain(title),
            validators=[Typed(PlainText), Required(), MaxLength(100)],
        )
        return self

    def text(self, text: str | PlainText) -> "Confirm":
        self._add_field(
            "text",
            str_to_plain(text),
            validators=[Typed(PlainText), Required(), MaxLength(300)],
        )
        return self

    def confirm(self, confirm: str | PlainText) -> "Confirm":
        self._add_field(
            "confirm",
            str_to_plain(confirm),
            validators=[Typed(PlainText), Required(), MaxLength(30)],
        )
        return self

    def deny(self, deny: str | PlainText) -> "Confirm":
        self._add_field(
            "deny",
            str_to_plain(deny),
            validators=[Typed(PlainText), Required(), MaxLength(30)],
        )
        return self

    def style(self, style: str) -> "Confirm":
        self._add_field(
            "style", style, validators=[Typed(str), Values("primary", "danger")]
        )
        return self


class ConversationFilter(Component):
    def __init__(
        self,
        include: Sequence[str] | None,
        exclude_bot_users: bool | None = None,
        exclude_external_shared_channels: bool | None = None,
    ):
        super().__init__()

    def include(self, include: Sequence[str]):
        pass

    def exclude_bot_users(self, exclude_bot_users: bool):
        pass

    def exclude_external_shared_channels(self, exclude_external_shared_channels: bool):
        pass


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
