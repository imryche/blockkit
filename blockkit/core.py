from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Sequence, Type

from blockkit.utils import is_md


class FieldValidationError(Exception):
    def __init__(self, field_name: str, message: str):
        self.field_name = field_name
        self.message = message
        super().__init__(f"Field '{field_name}': {message}")


class FieldValidator(ABC):
    @abstractmethod
    def validate(self, field_name: str, field_value: Any) -> None:
        pass

    def __call__(self, field_name: str, field_value: Any) -> None:
        return self.validate(field_name, field_value)


class Required(FieldValidator):
    def validate(self, field_name: str, field_value: Any) -> None:
        if field_value is None:
            raise FieldValidationError(field_name, "Value is required")


class Plain(FieldValidator):
    def validate(self, field_name: str, field_value: Any) -> None:
        if field_value is None:
            return

        type_field = field_value._get_field("type")
        if not type_field or type_field.value != Text.PLAIN:
            raise FieldValidationError(field_name, "Only plain_text is allowed")


class Length(FieldValidator):
    def __init__(self, min=0, max=999999):
        self.min = min
        self.max = max

    def validate(self, field_name: str, field_value: Any) -> None:
        if field_value is None:
            return

        value_length = len(field_value)
        if not (self.min <= value_length <= self.max):
            raise FieldValidationError(
                field_name,
                f"Length must be between {self.min} and {self.max} "
                f"(got {value_length})",
            )


class Values(FieldValidator):
    def __init__(self, *values: Sequence[str]):
        self.values = values

    def validate(self, field_name: str, field_value: Any) -> None:
        if field_value is None:
            return

        expected_values = ", ".join(f"'{v}'" for v in self.values)
        if isinstance(field_value, (list, tuple, set)):
            unexpected = set(field_value).difference(self.values)
            if unexpected:
                pretty_unexpected = ", ".join(f"'{v}'" for v in unexpected)
                raise FieldValidationError(
                    field_name,
                    f"Expected values {expected_values}, "
                    f"got unexpected {pretty_unexpected}",
                )
        else:
            if field_value not in self.values:
                raise FieldValidationError(
                    field_name,
                    f"Expected values {expected_values}, got '{field_value}'",
                )


class Typed(FieldValidator):
    def __init__(self, *types: Type):
        if not types:
            raise ValueError("At least one type must be specified")
        self.types = types

    def validate(self, field_name: str, field_value: Any) -> None:
        if field_value is None:
            return

        values = (
            [field_value]
            if not isinstance(field_value, (list, tuple, set))
            else field_value
        )

        for value in values:
            if isinstance(value, self.types):
                continue

            expected_names = ", ".join(f"'{c.__name__}'" for c in self.types)
            got_name = type(value).__name__
            raise FieldValidationError(
                field_name,
                f"Expected type{'s' if len(self.types) > 1 else ''} "
                f"{expected_names}, got '{got_name}'",
            )


class ComponentValidationError(Exception):
    def __init__(self, component_name: str, message: str):
        self.component_name = component_name
        self.message = message
        super().__init__(f"Component '{component_name}': {message}")


class ComponentValidator(ABC):
    @abstractmethod
    def validate(self, component: "Component") -> None:
        pass

    def __call__(self, component: "Component") -> None:
        return self.validate(component)


class Either(ComponentValidator):
    def __init__(self, *field_names: tuple[str]):
        self.field_names = field_names

    def validate(self, component: "Component") -> None:
        if not any(
            getattr(component._get_field(name), "value", None)
            for name in self.field_names
        ):
            expected_names = ", ".join(f"'{n}'" for n in self.field_names)
            raise ComponentValidationError(
                component.__class__.__name__,
                f"At least one of the following fields is required {expected_names}",
            )


class OnlyOne(ComponentValidator):
    def __init__(self, *field_names: tuple[str]):
        self.field_names = field_names

    def validate(self, component: "Component") -> None:
        field_count = sum(
            bool(getattr(component._get_field(name), "value", None))
            for name in self.field_names
        )
        if field_count > 1:
            allowed_names = ", ".join(f"'{n}'" for n in self.field_names)
            raise ComponentValidationError(
                component.__class__.__name__,
                f"Only one of the following fields is allowed {allowed_names}",
            )


class OnlyIf(ComponentValidator):
    def __init__(self, dependent_field: str, required_field: str, required_value: Any):
        self.dependent_field = dependent_field
        self.required_field = required_field
        self.required_value = required_value

    def validate(self, component: "Component") -> None:
        dependent_value = component._get_field(self.dependent_field).value
        required_value = component._get_field(self.required_field).value

        if dependent_value and required_value != self.required_value:
            raise ComponentValidationError(
                component.__class__.__name__,
                f"'{self.dependent_field}' is only allowed when "
                f"'{self.required_field}' is '{self.required_value}'",
            )


def str_to_plain(value: str) -> "Text":
    if isinstance(value, str):
        return Text(value).type(Text.PLAIN)
    return value


@dataclass
class Field:
    name: str
    value: Any
    validators: list[FieldValidator] = field(default_factory=list)

    def validate(self):
        for validator in self.validators:
            validator(self.name, self.value)


@dataclass
class Component:
    _fields: dict[str, Field] = field(default_factory=dict)
    _validators: list[ComponentValidator] = field(default_factory=list)

    def _add_field(self, name, value, validators: Sequence[FieldValidator] = None):
        if not validators:
            validators = []
        field = Field(name=name, value=value, validators=validators)
        self._fields[name] = field
        return self

    def _add_validator(
        self, validator: FieldValidator | ComponentValidator, field_name=None
    ) -> None:
        if isinstance(validator, FieldValidator):
            if not field_name:
                raise ValueError("Field name is required")
            if field_name not in self._fields:
                raise ValueError(f"No '{field_name}' field found")
            self._fields[field_name].validators.append(validator)
            return
        self._validators.append(validator)

    def _get_field(self, field_name: str) -> Any:
        return self._fields.get(field_name)

    def validate(self):
        for field_ in self._fields.values():
            field_.validate()

        for validator in self._validators:
            validator.validate(self)

    def build(self):
        self.validate()
        fields = {field.name: field.value for field in self._fields.values()}
        obj = {}
        for name, value in fields.items():
            if value is None:
                continue
            obj[name] = value
            if hasattr(value, "build"):
                obj[name] = value.build()
            if isinstance(value, (list, tuple, set)):
                obj[name] = [
                    item.build() if hasattr(item, "build") else item for item in value
                ]
        return obj


"""
Composition objects:

x Confirmation dialog (Confirm) - https://api.slack.com/reference/block-kit/composition-objects#confirm
x Conversation filter (ConversationFilter) - https://api.slack.com/reference/block-kit/composition-objects#filter_conversations
x Dispatch action configuration (DispatchActionConfig) - https://api.slack.com/reference/block-kit/composition-objects#dispatch_action_config
x Option (Option) - https://api.slack.com/reference/block-kit/composition-objects#option
x Option group (OptionGroup) - https://api.slack.com/reference/block-kit/composition-objects#option_group
x Text (Text) - https://api.slack.com/reference/block-kit/composition-objects#text
x Trigger (Trigger) - https://api.slack.com/reference/block-kit/composition-objects#trigger
x Workflow (Workflow) - https://api.slack.com/reference/block-kit/composition-objects#workflow
x Slack file (SlackFile) - https://api.slack.com/reference/block-kit/composition-objects#slack_file
"""


class Text(Component):
    PLAIN = "plain_text"
    MD = "mrkdwn"

    def __init__(
        self,
        text: str | None = None,
        emoji: bool | None = None,
        verbatim: bool | None = None,
        type: str | None = None,
    ):
        super().__init__()
        self.text(text)
        self.emoji(emoji)
        self.verbatim(verbatim)
        if type:
            self.type(type)
        self._add_validator(OnlyIf("verbatim", "type", self.MD))
        self._add_validator(OnlyIf("emoji", "type", self.PLAIN))

    def __len__(self):
        text = self._get_field("text")
        return len(text.value or "")

    def _detect_type(self, text):
        if text is None:
            return self.PLAIN
        return self.MD if is_md(str(text)) else self.PLAIN

    def text(self, text: str) -> "Text":
        self.type(self._detect_type(text))
        return self._add_field(
            "text",
            text,
            validators=[Typed(str), Required(), Length(1, 3000)],
        )

    def emoji(self, emoji: bool = True) -> "Text":
        return self._add_field("emoji", emoji, validators=[Typed(bool)])

    def verbatim(self, verbatim: bool = True) -> "Text":
        return self._add_field("verbatim", verbatim, validators=[Typed(bool)])

    def type(self, type: str) -> "Text":
        return self._add_field(
            "type",
            type,
            validators=[Typed(str), Required(), Values("plain_text", "mrkdwn")],
        )


class Confirm(Component):
    """
    Confirmation dialog

    Defines a dialog that adds a confirmation step to interactive elements.

    Slack docs:
        https://api.slack.com/reference/block-kit/composition-objects#confirm
    """

    def __init__(
        self,
        title: str | Text | None = None,
        text: str | Text | None = None,
        confirm: str | Text | None = None,
        deny: str | Text | None = None,
        style: str | None = None,
    ):
        super().__init__()
        self.title(title)
        self.text(text)
        self.confirm(confirm)
        self.deny(deny)
        self.style(style)

    def title(self, title: str | Text) -> "Confirm":
        self._add_field(
            "title",
            str_to_plain(title),
            validators=[Typed(Text), Required(), Plain(), Length(1, 100)],
        )
        return self

    def text(self, text: str | Text) -> "Confirm":
        self._add_field(
            "text",
            str_to_plain(text),
            validators=[Typed(Text), Required(), Plain(), Length(1, 300)],
        )
        return self

    def confirm(self, confirm: str | Text) -> "Confirm":
        self._add_field(
            "confirm",
            str_to_plain(confirm),
            validators=[Typed(Text), Required(), Plain(), Length(1, 30)],
        )
        return self

    def deny(self, deny: str | Text) -> "Confirm":
        self._add_field(
            "deny",
            str_to_plain(deny),
            validators=[Typed(Text), Required(), Plain(), Length(1, 30)],
        )
        return self

    def style(self, style: str) -> "Confirm":
        self._add_field(
            "style", style, validators=[Typed(str), Values("primary", "danger")]
        )
        return self


class ConversationFilter(Component):
    """
    Conversation filter object

    Defines a filter for the list of options in a conversation selector menu.

    Slack docs:
        https://api.slack.com/reference/block-kit/composition-objects#filter_conversations
    """

    def __init__(
        self,
        include: Sequence[str] | None = None,
        exclude_bot_users: bool | None = None,
        exclude_external_shared_channels: bool | None = None,
    ):
        super().__init__()
        self.include(include)
        self.exclude_bot_users(exclude_bot_users)
        self.exclude_external_shared_channels(exclude_external_shared_channels)

        self._add_validator(
            Either("include", "exclude_bot_users", "exclude_external_shared_channels")
        )

    def include(self, include: Sequence[str]) -> "ConversationFilter":
        self._add_field(
            "include",
            include,
            validators=[Typed(str), Values("im", "mpim", "private", "public")],
        )
        return self

    def exclude_bot_users(self, exclude_bot_users: bool = True) -> "ConversationFilter":
        self._add_field(
            "exclude_bot_users", exclude_bot_users, validators=[Typed(bool)]
        )
        return self

    def exclude_external_shared_channels(
        self, exclude_external_shared_channels: bool = True
    ) -> "ConversationFilter":
        self._add_field(
            "exclude_external_shared_channels",
            exclude_external_shared_channels,
            validators=[Typed(bool)],
        )
        return self


class DispatchActionConfig(Component):
    """
    Dispatch action configuration object

    Defines when a plain-text input element will return a
    block_actions interaction payload.

    Slack docs:
        https://api.slack.com/reference/block-kit/composition-objects#dispatch_action_config
    """

    def __init__(self, trigger_actions_on: Sequence[str] | None = None):
        super().__init__()
        self.trigger_actions_on(trigger_actions_on)

    def trigger_actions_on(self, trigger_actions_on: Sequence[str]):
        self._add_field(
            "trigger_actions_on",
            trigger_actions_on,
            validators=[
                Typed(str),
                Required(),
                Values("on_enter_pressed", "on_character_entered"),
            ],
        )
        return self


class Option(Component):
    """
    Option object

    Defines a single item in a number of item selection elements.

    Slack docs:
        https://api.slack.com/reference/block-kit/composition-objects#option
    """

    def __init__(
        self,
        text: str | Text | None = None,
        value: str | None = None,
        description: str | Text | None = None,
        url: str | None = None,
    ):
        super().__init__()
        self.text(text)
        self.value(value)
        self.description(description)
        self.url(url)

    # TODO: markdown should be available in checkboxes and radiobuttons
    def text(self, text: str | Text) -> "Option":
        return self._add_field(
            "text",
            str_to_plain(text),
            validators=[Typed(Text), Required(), Plain(), Length(1, 75)],
        )

    def value(self, value: str) -> "Option":
        return self._add_field(
            "value", value, validators=[Typed(str), Required(), Length(1, 150)]
        )

    # TODO: markdown should be available in checkbox group and radiobutton group
    def description(self, description: str | Text) -> "Option":
        return self._add_field(
            "description",
            str_to_plain(description),
            validators=[Typed(Text), Plain(), Length(1, 75)],
        )

    # TODO: should be available in overflow menus only
    def url(self, url: str | None = None) -> "Option":
        return self._add_field("url", url, validators=[Typed(str), Length(1, 3000)])


class OptionGroup(Component):
    """
    Option group object

    Defines a way to group options in a menu.

    Slack docs:
        https://api.slack.com/reference/block-kit/composition-objects#option_group
    """

    def __init__(
        self, label: str | Text | None = None, options: list[Option] | None = None
    ):
        super().__init__()
        self.label(label)
        self.options(*options or ())

    def label(self, label: str | Text) -> "OptionGroup":
        return self._add_field(
            "label",
            str_to_plain(label),
            validators=[Typed(Text), Required(), Plain(), Length(1, 75)],
        )

    def options(self, *options: tuple[Option]) -> "OptionGroup":
        return self._add_field(
            "options",
            list(options),
            validators=[Typed(Option), Required(), Length(1, 100)],
        )

    def add_option(self, option: Option) -> "OptionGroup":
        field = self._get_field("options")
        field.value.append(option)
        return self


class InputParameter(Component):
    """
    Input parameter object

    Slack docs:
        https://api.slack.com/reference/block-kit/composition-objects#input_parameter
    """

    def __init__(self, name: str | None = None, value: str | None = None):
        super().__init__()
        self.name(name)
        self.value(value)

    def name(self, name: str) -> "InputParameter":
        return self._add_field(
            "name", name, validators=[Typed(str), Required(), Length(1, 3000)]
        )

    def value(self, value: str) -> "InputParameter":
        return self._add_field(
            "value", value, validators=[Typed(str), Required(), Length(1, 3000)]
        )


class Trigger(Component):
    """
    Trigger object

    Defines an object containing trigger information.

    Slack docs:
        https://api.slack.com/reference/block-kit/composition-objects#trigger
    """

    def __init__(
        self,
        url: str | None = None,
        customizable_input_parameters: list[InputParameter] | None = None,
    ):
        super().__init__()
        self.url(url)
        self.customizable_input_parameters(*customizable_input_parameters or ())

    def url(self, url: str) -> "Trigger":
        return self._add_field(
            "url", url, validators=[Typed(str), Required(), Length(1, 3000)]
        )

    def customizable_input_parameters(
        self, *customizable_input_parameters: tuple[InputParameter]
    ) -> "Trigger":
        return self._add_field(
            "customizable_input_parameters",
            list(customizable_input_parameters),
            validators=[Typed(InputParameter), Length(1, 100)],
        )

    def add_input_parameter(self, input_parameter: InputParameter) -> "Trigger":
        field = self._get_field("customizable_input_parameters")
        field.value.append(input_parameter)
        return self


class Workflow(Component):
    """
    Workflow object

    Defines an object containing workflow information.

    Slack docs:
        https://api.slack.com/reference/block-kit/composition-objects#workflow
    """

    def __init__(self, trigger: Trigger | None = None):
        super().__init__()
        self.trigger(trigger)

    def trigger(self, trigger: Trigger) -> "Workflow":
        return self._add_field(
            "trigger", trigger, validators=[Typed(Trigger), Required()]
        )


class SlackFile(Component):
    """
    Slack file object

    Defines an object containing Slack file information to be used
    in an image block or image element.

    Slack docs:
        https://api.slack.com/reference/block-kit/composition-objects#slack_file
    """

    def __init__(self, url: str | None = None, id: str | None = None):
        super().__init__()
        self.url(url)
        self.id(id)
        self._add_validator(OnlyOne("url", "id"))

    def url(self, url: str) -> "SlackFile":
        return self._add_field("url", url, validators=[Typed(str), Length(1, 3000)])

    def id(self, id: str) -> "SlackFile":
        return self._add_field("id", id, validators=[Typed(str), Length(1, 30)])


"""
Block elements:

x Button (Button) - https://api.slack.com/reference/block-kit/block-elements#button
"""


class Button(Component):
    """
    Button element

    Allows users a direct path to performing basic actions.

    Slack docs:
        https://api.slack.com/reference/block-kit/block-elements#button
    """

    PRIMARY = "primary"
    DANGER = "danger"

    def __init__(
        self,
        text: str | Text | None = None,
        action_id: str | None = None,
        url: str | None = None,
        value: str | None = None,
        style: str | None = None,
        confirm: Confirm | None = None,
        accessibility_label: str | None = None,
    ):
        super().__init__()
        self._add_field("type", "button")

        self.text(text)
        self.action_id(action_id)
        self.url(url)
        self.value(value)
        self.style(style)
        self.confirm(confirm)
        self.accessibility_label(accessibility_label)

    def text(self, text: str | Text) -> "Button":
        return self._add_field(
            "text",
            str_to_plain(text),
            validators=[Typed(Text), Required(), Plain(), Length(1, 75)],
        )

    def action_id(self, action_id: str) -> "Button":
        return self._add_field(
            "action_id", action_id, validators=[Typed(str), Length(1, 255)]
        )

    def url(self, url: str) -> "Button":
        return self._add_field("url", url, validators=[Typed(str), Length(1, 3000)])

    def value(self, value: str) -> "Button":
        return self._add_field("value", value, validators=[Typed(str), Length(1, 2000)])

    def style(self, style: str) -> "Button":
        return self._add_field(
            "style", style, validators=[Typed(str), Values(self.PRIMARY, self.DANGER)]
        )

    def confirm(self, confirm: Confirm) -> "Button":
        return self._add_field("confirm", confirm, validators=[Typed(Confirm)])

    def accessibility_label(self, accessibility_label: str) -> "Button":
        return self._add_field(
            "accessibility_label",
            accessibility_label,
            validators=[Typed(str), Length(1, 75)],
        )


class Checkboxes(Component):
    def __init__(
        self,
        action_id: str | None = None,
        options: Sequence[Option] | None = None,
        initial_options: Sequence[Option] | None = None,
        confirm: Confirm | None = None,
        focus_on_load: bool | None = None,
    ):
        super().__init__()
        self.action_id(action_id)
        self.options(*options or ())
        self.initial_options(*initial_options or ())
        self.confirm(confirm)
        self.focus_on_load(focus_on_load)

    def action_id(self, action_id: str) -> "Checkboxes":
        return self._add_field("action_id", action_id, validators=[])

    def options(self, *options: Option) -> "Checkboxes":
        return self._add_field("options", options, validators=[])

    def initial_options(self, *initial_options: Option) -> "Checkboxes":
        return self._add_field("initial_options", initial_options, validators=[])

    def confirm(self, confirm: Confirm) -> "Checkboxes":
        return self._add_field("confirm", confirm, validators=[])

    def focus_on_load(self, focus_on_load: bool) -> "Checkboxes":
        return self._add_field("focus_on_load", focus_on_load, validators=[])


"""
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
