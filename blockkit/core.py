import dataclasses
import json
import re
from abc import ABC, abstractmethod
from datetime import date, datetime, time
from typing import Any, Final, Literal, Self, TypeAlias, get_args
from zoneinfo import ZoneInfo

from blockkit.utils import is_md


class FieldValidationError(Exception):
    def __init__(self, field_name: str, message: str):
        self.field_name = field_name
        self.message = message
        super().__init__(f"Field '{field_name}': {message}")


class FieldValidator(ABC):
    @abstractmethod
    def validate(self, field_name: str, value: Any) -> None:
        pass

    def __call__(self, field_name: str, value: Any) -> None:
        return self.validate(field_name, value)


class Required(FieldValidator):
    def validate(self, field_name: str, value: Any) -> None:
        if value is None:
            raise FieldValidationError(field_name, "Value is required")


class Plain(FieldValidator):
    def validate(self, field_name: str, value: Any) -> None:
        if value is None:
            return

        type_field = value._get_field("type")
        if not type_field or type_field.value != Text.PLAIN:
            raise FieldValidationError(field_name, "Only plain_text is allowed")


class Length(FieldValidator):
    def __init__(self, min: int = 0, max: int = 999999):
        self.min = min
        self.max = max

    def validate(self, field_name: str, value: Any) -> None:
        if value is None:
            return

        if isinstance(value, list | tuple | set) and len(value) < 1:
            return

        value_length = len(value)
        if not (self.min <= value_length <= self.max):
            raise FieldValidationError(
                field_name,
                f"Length must be between {self.min} and {self.max} "
                f"(got {value_length})",
            )


class HexColor(FieldValidator):
    def validate(self, field_name: str, value: Any) -> None:
        if value is None:
            return

        if not re.match("^#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", value):
            raise FieldValidationError(field_name, f"Invalid HEX color, got {value}")


class Strings(FieldValidator):
    def __init__(self, *values: str):
        self.values = values

    def validate(self, field_name: str, value: Any) -> None:
        if value is None:
            return

        expected_values = ", ".join(f"'{v}'" for v in self.values)
        if isinstance(value, list | tuple | set):
            unexpected = set(value).difference(self.values)
            if unexpected:
                pretty_unexpected = ", ".join(f"'{v}'" for v in unexpected)
                raise FieldValidationError(
                    field_name,
                    f"Expected values {expected_values}, "
                    f"got unexpected {pretty_unexpected}",
                )
        else:
            if value not in self.values:
                raise FieldValidationError(
                    field_name,
                    f"Expected values {expected_values}, got '{value}'",
                )


class Ints(FieldValidator):
    def __init__(self, min=0, max=999999):
        self.min = min
        self.max = max

    def validate(self, field_name: str, value: Any) -> None:
        if value is None:
            return

        if not (self.min <= value <= self.max):
            raise FieldValidationError(
                field_name,
                f"Value must be between {self.min} and {self.max} (got {value})",
            )


class IsoDate(FieldValidator):
    def validate(self, field_name: str, value: Any) -> None:
        if value is None:
            return

        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise FieldValidationError(
                field_name, "Invalid date format. Expected YYYY-MM-DD"
            )


class UnixTimestamp(FieldValidator):
    def validate(self, field_name: str, value: Any) -> None:
        if value is None:
            return

        try:
            datetime.fromtimestamp(int(value))
        except ValueError:
            raise FieldValidationError(
                field_name, "Invalid datetime format. Expected UNIX timestamp"
            )


class Typed(FieldValidator):
    def __init__(self, *types: type):
        if not types:
            raise ValueError("At least one type must be specified")
        self.types = types

    def validate(self, field_name: str, value: Any) -> None:
        if value is None:
            return

        values = [value] if not isinstance(value, list | tuple | set) else value

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
    def __init__(self, component: "Component", message: str):
        self.component = component
        self.message = message
        super().__init__(f"Component '{component.__class__.__name__}': {message}")


class ComponentValidator(ABC):
    @abstractmethod
    def validate(self, component: "Component") -> None:
        pass

    def __call__(self, component: "Component") -> None:
        return self.validate(component)


class AtLeastOne(ComponentValidator):
    def __init__(self, *field_names: str):
        self.field_names = field_names

    def validate(self, component: "Component") -> None:
        if not any(component._get_field_value(name) for name in self.field_names):
            expected_names = ", ".join(f"'{n}'" for n in self.field_names)
            raise ComponentValidationError(
                component,
                f"At least one of the following fields is required {expected_names}",
            )


class OnlyOne(ComponentValidator):
    def __init__(self, *field_names: str):
        self.field_names = field_names

    def validate(self, component: "Component") -> None:
        field_count = sum(
            bool(component._get_field_value(name)) for name in self.field_names
        )
        if field_count != 1:
            allowed_names = ", ".join(f"'{n}'" for n in self.field_names)
            raise ComponentValidationError(
                component,
                f"Only one of the following fields is required {allowed_names}",
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
                component,
                f"'{self.dependent_field}' is only allowed when "
                f"'{self.required_field}' is '{self.required_value}'",
            )


class Within(ComponentValidator):
    def __init__(self, source_field: str, target_field: str):
        self.source_field = source_field
        self.target_field = target_field

    def validate(self, component: "Component") -> None:
        source_value = component._get_field_value(self.source_field)
        target_value = component._get_field_value(self.target_field)

        if not (source_value and target_value):
            return

        if not isinstance(source_value, list | tuple | set):
            source_value = [source_value]

        if not set(source_value).issubset(set(target_value)):
            raise ComponentValidationError(
                component,
                f"'{self.source_field}' has items that aren't "
                f"present in the '{self.target_field}'",
            )


class Ranging(ComponentValidator):
    def __init__(self, source_field: str, min_field: str, max_field: str):
        self.source_field = source_field
        self.min_field = min_field
        self.max_field = max_field

    def validate(self, component: "Component") -> None:
        source_value = component._get_field(self.source_field).value
        if source_value is None:
            return

        if isinstance(source_value, str):
            source_value = len(source_value)

        min_value = component._get_field(self.min_field).value
        if min_value and source_value < min_value:
            raise ComponentValidationError(
                component,
                f"'{self.source_field}' value must be greater than or equal to "
                f"'{min_value:.0f}', got '{source_value:.0f}'",
            )

        max_value = component._get_field(self.max_field).value
        if max_value and source_value > max_value:
            raise ComponentValidationError(
                component,
                f"'{self.source_field}' value must be less than or equal to "
                f"'{max_value:.0f}', got '{source_value:.0f}'",
            )


class DecimalAllowed(ComponentValidator):
    def __init__(self, source_field: str, *fields: str):
        self.source_field = source_field
        self.fields = fields

    def validate(self, component: "Component") -> None:
        decimal_allowed = component._get_field(self.source_field).value
        if decimal_allowed is None:
            raise ValueError(f"'{self.source_field}' field not found")

        for field_name in self.fields:
            field_value = component._get_field(field_name).value
            if not field_value:
                continue

            if not decimal_allowed and isinstance(field_value, float):
                raise ComponentValidationError(
                    component,
                    f"'{field_name}' decimal values are not allowed, "
                    f"got '{field_value}'",
                )


class StyledCorrectly(ComponentValidator):
    def __init__(self, extended: bool = False):
        self.extended = extended

    def validate(self, component: "Component") -> None:
        style = component._get_field("style").value
        if not style:
            return

        code = style._get_field("code").value
        highlight = style._get_field("highlight").value
        client_highlight = style._get_field("client_highlight").value
        unlink = style._get_field("unlink").value

        if self.extended and code:
            raise ComponentValidationError(component, "'code' style is not allowed")

        if not self.extended and any((highlight, client_highlight, unlink)):
            raise ComponentValidationError(
                component,
                "'highlight', 'client_highlight', 'unlink' styles are not allowed",
            )


def str_to_plain(value: "str | Text | None") -> "Text | None":
    if isinstance(value, str):
        return Text(value).type(Text.PLAIN)
    return value


@dataclasses.dataclass
class Field:
    name: str
    value: Any
    validators: list[FieldValidator] = dataclasses.field(default_factory=list)
    stringify: bool = False

    def validate(self):
        for validator in self.validators:
            validator(self.name, self.value)


class Component:
    def __init__(self, type: str | None = None):
        self._fields: dict[str, Field] = {}
        self._validators: list[ComponentValidator | FieldValidator] = []
        if type:
            self._add_field("type", type)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Component):
            return NotImplemented
        if not isinstance(other, self.__class__):
            return False
        return self.build() == other.build()

    def __hash__(self):
        def make_hashable(obj):
            if isinstance(obj, dict):
                return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
            elif isinstance(obj, list):
                return tuple(make_hashable(item) for item in obj)
            elif isinstance(obj, set | tuple):
                return tuple(make_hashable(item) for item in obj)
            else:
                return obj

        return hash(make_hashable(self.build()))

    def _add_field(
        self: Self,
        name: str,
        value: Any,
        validators: list[FieldValidator] | None = None,
        stringify: bool = False,
    ) -> Self:
        if not validators:
            validators = []
        field = Field(
            name=name,
            value=value,
            validators=validators,
            stringify=stringify,
        )
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

    def _get_field(self, field_name: str) -> Field:
        field = self._fields.get(field_name)
        if not field:
            raise AttributeError(f"Field '{field_name}' does not exist")
        return field

    def _get_field_value(self, field_name: str) -> Any:
        try:
            return self._get_field(field_name).value
        except AttributeError:
            return None

    def _add_field_value(self, field_name: str, value: Any) -> Self:
        field = self._get_field(field_name)
        field.value.append(value)
        return self

    def validate(self):
        for field_ in self._fields.values():
            field_.validate()

        for validator in self._validators:
            validator.validate(self)

    def build(self):
        self.validate()
        obj = {}
        for field in self._fields.values():
            if field.value is None:
                continue
            if isinstance(field.value, list | tuple | set) and len(field.value) < 1:
                continue
            if type(field.value) is date:
                field.value = field.value.strftime("%Y-%m-%d")
            if type(field.value) is datetime:
                field.value = str(int(field.value.timestamp()))
            if isinstance(field.value, time):
                field.value = field.value.strftime("%H:%M")
            if isinstance(field.value, ZoneInfo):
                field.value = str(field.value)
            if field.stringify:
                field.value = str(field.value)
            obj[field.name] = field.value
            if hasattr(field.value, "build"):
                obj[field.name] = field.value.build()
            if isinstance(field.value, list | tuple | set):
                obj[field.name] = [
                    item.build() if hasattr(item, "build") else item
                    for item in field.value
                ]
        return obj


class ActionIdMixin:
    def action_id(self, action_id: str | None) -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "action_id", action_id, validators=[Typed(str), Length(1, 255)]
        )


class BlockIdMixin:
    def block_id(self, block_id: str | None) -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "block_id", block_id, validators=[Typed(str), Length(1, 255)]
        )


class TextMixin:
    def text(self, text: "str | Text | None") -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "text",
            str_to_plain(text),
            validators=[Typed(Text), Required(), Plain(), Length(1, 75)],
        )


class UrlMixin:
    def url(self, url: str | None) -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "url", url, validators=[Typed(str), Length(1, 3000)]
        )


class FocusOnLoadMixin:
    def focus_on_load(self, focus_on_load: bool | None = True) -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "focus_on_load",
            focus_on_load,
            validators=[Typed(bool)],
        )


class ConfirmMixin:
    def confirm(self, confirm: "Confirm | None") -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "confirm",
            confirm,
            validators=[Typed(Confirm)],
        )


class PlaceholderMixin:
    def placeholder(self, placeholder: "str | Text | None") -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "placeholder",
            str_to_plain(placeholder),
            validators=[Typed(Text), Plain(), Length(1, 150)],
        )


class StyleMixin:
    PRIMARY: Final[Literal["primary"]] = "primary"
    DANGER: Final[Literal["danger"]] = "danger"

    def style(self, style: Literal["primary", "danger"] | None) -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "style",
            style,
            validators=[Typed(str), Strings(self.PRIMARY, self.DANGER)],
        )


class AccessibilityLabelMixin:
    def accessibility_label(self, accessibility_label: str | None) -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "accessibility_label",
            accessibility_label,
            validators=[Typed(str), Length(1, 75)],
        )


class InitialOptionsMixin:
    def initial_options(self, *initial_options: "Option | OptionGroup") -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "initial_options",
            list(initial_options),
            validators=[Typed(Option, OptionGroup), Length(1, 100)],
        )

    def add_initial_option(self, option: "Option | OptionGroup") -> Self:
        return self._add_field_value("initial_options", option)  # type: ignore[attr-defined]


class InitialOptionMixin:
    def initial_option(self, initial_option: "Option | OptionGroup | None") -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "initial_option",
            initial_option,
            validators=[Typed(Option, OptionGroup)],
        )


class MaxSelectedItemsMixin:
    def max_selected_items(self, max_selected_items: int | None) -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "max_selected_items",
            max_selected_items,
            validators=[Typed(int), Ints(1)],
        )


class OptionsMixin:
    def options(self, *options: "Option") -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "options",
            list(options),
            validators=[
                Typed(Option),
                Required(),
                Length(1, getattr(self, "_max_options", 100)),
            ],
        )

    def add_option(self, option: "Option") -> Self:
        return self._add_field_value("options", option)  # type: ignore[attr-defined]


class OptionGroupsMixin:
    def option_groups(self, *option_groups: "OptionGroup") -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "option_groups",
            list(option_groups),
            validators=[Typed(OptionGroup), Length(1, 100)],
        )

    def add_option_group(self, option_group: "OptionGroup") -> Self:
        return self._add_field_value("option_groups", option_group)  # type: ignore[attr-defined]


class DispatchActionConfigMixin:
    def dispatch_action_config(
        self, dispatch_action_config: "DispatchActionConfig | None"
    ) -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "dispatch_action_config",
            dispatch_action_config,
            validators=[Typed(DispatchActionConfig)],
        )


class MinQueryLengthMixin:
    def min_query_length(self, min_query_length: int | None) -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "min_query_length",
            min_query_length,
            validators=[Typed(int), Ints(1)],
        )


class DefaultToCurrentConversationMixin:
    def default_to_current_conversation(
        self, default_to_current_conversation: bool | None = True
    ) -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "default_to_current_conversation",
            default_to_current_conversation,
            validators=[Typed(bool)],
        )


class FilterMixin:
    def filter(self, filter: "ConversationFilter | None") -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "filter",
            filter,
            validators=[Typed(ConversationFilter)],
        )


class ResponseUrlEnabledMixin:
    def response_url_enabled(self, response_url_enabled: bool | None = True) -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "response_url_enabled",
            response_url_enabled,
            validators=[Typed(bool)],
        )


class AltTextMixin:
    def alt_text(self, alt_text: str | None) -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "alt_text",
            alt_text,
            validators=[Typed(str), Required(), Length(1, 255)],
        )


class ImageUrlMixin:
    def image_url(self, image_url: str | None) -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "image_url",
            image_url,
            validators=[Typed(str), Length(1, 3000)],
        )


class SlackFileMixin:
    def slack_file(self, slack_file: "SlackFile | None") -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "slack_file",
            slack_file,
            validators=[Typed(SlackFile)],
        )


class RichStyleMixin:
    def style(self, style: "RichStyle | None") -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "style", style, validators=[Typed(RichStyle)]
        )


class RichTextElementsMixin:
    def elements(self, *elements: "RichTextElement") -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "elements",
            list(elements),
            validators=[Typed(*get_args(RichTextElement)), Required()],
        )

    def add_element(self, element: "RichTextElement") -> Self:
        return self._add_field_value("elements", element)  # type: ignore[attr-defined]


class RichBorderMixin:
    def border(self, border: int | None) -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "border", border, validators=[Typed(int), Ints(max=1)]
        )


class BlocksMixin:
    def blocks(self, *blocks: "ModalBlock") -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "blocks",
            list(blocks),
            validators=[Typed(*get_args(ModalBlock)), Required(), Length(1, 100)],
        )

    def add_block(self, block: "ModalBlock | None") -> Self:
        return self._add_field_value("blocks", block)  # type: ignore[attr-defined]


class PrivateMetadataMixin:
    def private_metadata(self, private_metadata: Any) -> Self:
        if not isinstance(private_metadata, str):
            private_metadata = json.dumps(private_metadata)
        return self._add_field(  # type: ignore[attr-defined]
            "private_metadata",
            private_metadata,
            validators=[Typed(str), Length(1, 3000)],
        )


class CallbackIdMixin:
    def callback_id(self, callback_id: str | None) -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "callback_id", callback_id, validators=[Typed(str), Length(1, 255)]
        )


class ExternalIdMixin:
    def external_id(self, external_id: str | None) -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "external_id", external_id, validators=[Typed(str), Length(1)]
        )


"""
Composition objects
"""


class Text(Component):
    """
    Text object

    Defines an object containing some text.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/composition-objects/text-object
    """

    PLAIN: Final[Literal["plain_text"]] = "plain_text"
    MD: Final[Literal["mrkdwn"]] = "mrkdwn"

    def __init__(
        self,
        text: str | None = None,
        emoji: bool | None = None,
        verbatim: bool | None = None,
        type: Literal["plain_text", "mrkdwn"] | None = None,
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

    def _detect_type(self, text) -> Literal["plain_text", "mrkdwn"]:
        if text is None:
            return self.PLAIN
        return self.MD if is_md(str(text)) else self.PLAIN

    def text(self, text: str | None) -> Self:
        self.type(self._detect_type(text))
        return self._add_field(
            "text",
            text,
            validators=[Typed(str), Required(), Length(1, 3000)],
        )

    def emoji(self, emoji: bool | None = True) -> Self:
        return self._add_field("emoji", emoji, validators=[Typed(bool)])

    def verbatim(self, verbatim: bool | None = True) -> Self:
        return self._add_field("verbatim", verbatim, validators=[Typed(bool)])

    def type(self, type: Literal["plain_text", "mrkdwn"]) -> Self:
        return self._add_field(
            "type",
            type,
            validators=[Typed(str), Required(), Strings("plain_text", "mrkdwn")],
        )


class Confirm(Component, StyleMixin):
    """
    Confirmation dialog

    Defines a dialog that adds a confirmation step to interactive elements.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/composition-objects/confirmation-dialog-object
    """

    def __init__(
        self,
        title: str | Text | None = None,
        text: str | Text | None = None,
        confirm: str | Text | None = None,
        deny: str | Text | None = None,
        style: Literal["primary", "danger"] | None = None,
    ):
        super().__init__()
        self.title(title)
        self.text(text)
        self.confirm(confirm)
        self.deny(deny)
        self.style(style)

    def title(self, title: str | Text | None) -> Self:
        return self._add_field(
            "title",
            str_to_plain(title),
            validators=[Typed(Text), Required(), Plain(), Length(1, 100)],
        )

    def text(self, text: str | Text | None) -> Self:
        return self._add_field(
            "text",
            str_to_plain(text),
            validators=[Typed(Text), Required(), Plain(), Length(1, 300)],
        )

    def confirm(self, confirm: str | Text | None) -> Self:
        return self._add_field(
            "confirm",
            str_to_plain(confirm),
            validators=[Typed(Text), Required(), Plain(), Length(1, 30)],
        )

    def deny(self, deny: str | Text | None) -> Self:
        return self._add_field(
            "deny",
            str_to_plain(deny),
            validators=[Typed(Text), Required(), Plain(), Length(1, 30)],
        )


class ConversationFilter(Component):
    """
    Conversation filter object

    Defines a filter for the list of options in a conversation selector menu.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/composition-objects/conversation-filter-object
    """

    IM: Final[Literal["im"]] = "im"
    MPIM: Final[Literal["mpim"]] = "mpim"
    PRIVATE: Final[Literal["private"]] = "private"
    PUBLIC: Final[Literal["public"]] = "public"

    def __init__(
        self,
        include: list[Literal["im", "mpim", "private", "public"]] | None = None,
        exclude_bot_users: bool | None = None,
        exclude_external_shared_channels: bool | None = None,
    ):
        super().__init__()
        self.include(include)
        self.exclude_bot_users(exclude_bot_users)
        self.exclude_external_shared_channels(exclude_external_shared_channels)
        self._add_validator(
            AtLeastOne(
                "include", "exclude_bot_users", "exclude_external_shared_channels"
            )
        )

    def include(
        self, include: list[Literal["im", "mpim", "private", "public"]] | None
    ) -> Self:
        return self._add_field(
            "include",
            include,
            validators=[
                Typed(str),
                Strings(self.IM, self.MPIM, self.PRIVATE, self.PUBLIC),
            ],
        )

    def exclude_bot_users(self, exclude_bot_users: bool | None = True) -> Self:
        return self._add_field(
            "exclude_bot_users", exclude_bot_users, validators=[Typed(bool)]
        )

    def exclude_external_shared_channels(
        self, exclude_external_shared_channels: bool | None = True
    ) -> Self:
        return self._add_field(
            "exclude_external_shared_channels",
            exclude_external_shared_channels,
            validators=[Typed(bool)],
        )


class DispatchActionConfig(Component):
    """
    Dispatch action configuration object

    Defines when a plain-text input element will return a
    block_actions interaction payload.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/composition-objects/dispatch-action-configuration-object
    """

    ON_ENTER_PRESSED: Final[Literal["on_enter_pressed"]] = "on_enter_pressed"
    ON_CHARACTER_ENTERED: Final[Literal["on_character_entered"]] = (
        "on_character_entered"
    )

    def __init__(
        self,
        trigger_actions_on: list[Literal["on_enter_pressed", "on_character_entered"]]
        | None = None,
    ):
        super().__init__()
        self.trigger_actions_on(trigger_actions_on)

    def trigger_actions_on(
        self,
        trigger_actions_on: list[Literal["on_enter_pressed", "on_character_entered"]]
        | None,
    ):
        return self._add_field(
            "trigger_actions_on",
            trigger_actions_on,
            validators=[
                Typed(str),
                Required(),
                Strings(self.ON_ENTER_PRESSED, self.ON_CHARACTER_ENTERED),
            ],
        )


class Option(Component, TextMixin, UrlMixin):
    """
    Option object

    Defines a single item in a number of item selection elements.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/composition-objects/option-object
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

    def value(self, value: str | None) -> Self:
        return self._add_field(
            "value", value, validators=[Typed(str), Required(), Length(1, 150)]
        )

    # TODO: markdown should be available in checkbox group and radiobutton group
    def description(self, description: str | Text | None) -> Self:
        return self._add_field(
            "description",
            str_to_plain(description),
            validators=[Typed(Text), Length(1, 75)],
        )


class OptionGroup(Component, OptionsMixin):
    """
    Option group object

    Defines a way to group options in a menu.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/composition-objects/option-group-object
    """

    def __init__(
        self, label: str | Text | None = None, options: list[Option] | None = None
    ):
        super().__init__()
        self.label(label)
        self.options(*options or ())

    def label(self, label: str | Text | None) -> Self:
        return self._add_field(
            "label",
            str_to_plain(label),
            validators=[Typed(Text), Required(), Plain(), Length(1, 75)],
        )


class InputParameter(Component):
    """
    Input parameter object

    Slack docs:
        https://docs.slack.dev/reference/block-kit/composition-objects/trigger-object#input_parameter
    """

    def __init__(self, name: str | None = None, value: str | None = None):
        super().__init__()
        self.name(name)
        self.value(value)

    def name(self, name: str | None) -> Self:
        return self._add_field(
            "name", name, validators=[Typed(str), Required(), Length(1, 3000)]
        )

    def value(self, value: str | None) -> Self:
        return self._add_field(
            "value", value, validators=[Typed(str), Required(), Length(1, 3000)]
        )


class Trigger(Component):
    """
    Trigger object

    Defines an object containing trigger information.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/composition-objects/trigger-object
    """

    def __init__(
        self,
        url: str | None = None,
        customizable_input_parameters: list[InputParameter] | None = None,
    ):
        super().__init__()
        self.url(url)
        self.customizable_input_parameters(*customizable_input_parameters or ())

    def url(self, url: str | None) -> Self:
        return self._add_field(
            "url", url, validators=[Typed(str), Required(), Length(1, 3000)]
        )

    def customizable_input_parameters(
        self, *customizable_input_parameters: tuple[InputParameter]
    ) -> Self:
        return self._add_field(
            "customizable_input_parameters",
            list(customizable_input_parameters),
            validators=[Typed(InputParameter), Length(1, 100)],
        )

    def add_input_parameter(self, input_parameter: InputParameter) -> Self:
        return self._add_field_value("customizable_input_parameters", input_parameter)  # type: ignore[attr-defined]


class Workflow(Component):
    """
    Workflow object

    Defines an object containing workflow information.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/composition-objects/workflow-object
    """

    def __init__(self, trigger: Trigger | None = None):
        super().__init__()
        self.trigger(trigger)

    def trigger(self, trigger: Trigger | None) -> Self:
        return self._add_field(
            "trigger", trigger, validators=[Typed(Trigger), Required()]
        )


class SlackFile(Component, UrlMixin):
    """
    Slack file object

    Defines an object containing Slack file information to be used
    in an image block or image element.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/composition-objects/slack-file-object
    """

    def __init__(self, url: str | None = None, id: str | None = None):
        super().__init__()
        self.url(url)
        self.id(id)
        self._add_validator(OnlyOne("url", "id"))

    def id(self, id: str | None) -> Self:
        return self._add_field("id", id, validators=[Typed(str), Length(1, 30)])


"""
Block elements
"""


class Button(
    Component,
    TextMixin,
    ActionIdMixin,
    UrlMixin,
    StyleMixin,
    ConfirmMixin,
    AccessibilityLabelMixin,
):
    """
    Button element

    Allows users a direct path to performing basic actions.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/button-element
    """

    def __init__(
        self,
        text: str | Text | None = None,
        action_id: str | None = None,
        url: str | None = None,
        value: str | None = None,
        style: Literal["primary", "danger"] | None = None,
        confirm: Confirm | None = None,
        accessibility_label: str | None = None,
    ):
        super().__init__("button")
        self.text(text)
        self.action_id(action_id)
        self.url(url)
        self.value(value)
        self.style(style)
        self.confirm(confirm)
        self.accessibility_label(accessibility_label)

    def value(self, value: str | None) -> Self:
        return self._add_field("value", value, validators=[Typed(str), Length(1, 2000)])


class Checkboxes(
    Component, ActionIdMixin, OptionsMixin, FocusOnLoadMixin, ConfirmMixin
):
    """
    Checkboxes element

    Allows users to choose multiple items from a list of options.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/checkboxes-element
    """

    def __init__(
        self,
        action_id: str | None = None,
        options: list[Option] | None = None,
        initial_options: list[Option] | None = None,
        confirm: Confirm | None = None,
        focus_on_load: bool | None = None,
    ):
        super().__init__("checkboxes")
        self._max_options = 10
        self.action_id(action_id)
        self.options(*options or ())
        self.initial_options(*initial_options or ())
        self.confirm(confirm)
        self.focus_on_load(focus_on_load)

    def initial_options(self, *initial_options: Option) -> Self:
        return self._add_field(
            "initial_options",
            list(initial_options),
            validators=[Typed(Option), Length(1, 10)],
        )

    def add_initial_option(self, initial_option: Option) -> Self:
        return self._add_field_value("initial_options", initial_option)  # type: ignore[attr-defined]


class DatePicker(
    Component, ActionIdMixin, FocusOnLoadMixin, ConfirmMixin, PlaceholderMixin
):
    """
    Date picker element

    Allows users to select a date from a calendar style UI.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/date-picker-element
    """

    def __init__(
        self,
        action_id: str | None = None,
        initial_date: str | date | None = None,
        confirm: Confirm | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
    ):
        super().__init__("datepicker")
        self.action_id(action_id)
        self.initial_date(initial_date)
        self.confirm(confirm)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)

    def initial_date(self, initial_date: str | date | None) -> Self:
        if isinstance(initial_date, str):
            initial_date = datetime.strptime(initial_date, "%Y-%m-%d").date()
        return self._add_field("initial_date", initial_date, validators=[Typed(date)])


class DatetimePicker(
    Component, ActionIdMixin, FocusOnLoadMixin, ConfirmMixin, PlaceholderMixin
):
    """
    Datetime picker element

    Allows users to select both a date and a time of day, formatted as a Unix timestamp.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/datetime-picker-element
    """

    def __init__(
        self,
        action_id: str | None = None,
        initial_date_time: int | datetime | None = None,
        confirm: Confirm | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
    ):
        super().__init__("datetimepicker")
        self.action_id(action_id)
        self.initial_date_time(initial_date_time)
        self.confirm(confirm)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)

    def initial_date_time(self, initial_date_time: int | datetime | None) -> Self:
        if isinstance(initial_date_time, datetime):
            initial_date_time = int(initial_date_time.timestamp())
        return self._add_field(
            "initial_date_time", initial_date_time, validators=[Typed(int)]
        )


class EmailInput(
    Component,
    ActionIdMixin,
    DispatchActionConfigMixin,
    FocusOnLoadMixin,
    PlaceholderMixin,
):
    """
    Email input element

    Allows user to enter an email into a single-line field.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/email-input-element
    """

    def __init__(
        self,
        action_id: str | None = None,
        initial_value: str | None = None,
        dispatch_action_config: DispatchActionConfig | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
    ):
        super().__init__("email_text_input")
        self.action_id(action_id)
        self.initial_value(initial_value)
        self.dispatch_action_config(dispatch_action_config)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)

    def initial_value(self, initial_value: str | None) -> Self:
        return self._add_field(
            "initial_value", initial_value, validators=[Typed(str), Length(1, 74)]
        )


class FileInput(Component, ActionIdMixin):
    """
    File input element

    Allows user to upload files.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/file-input-element
    """

    FILE_TYPES = [
        "auto", "text", "ai", "apk", "applescript", "binary", "bmp", "boxnote", "c",
        "csharp", "cpp", "css", "csv", "clojure", "coffeescript", "cfm", "d", "dart",
        "diff", "doc", "docx", "dockerfile", "dotx", "eml", "eps", "epub", "erlang",
        "fla", "flv", "fsharp", "fortran", "gdoc", "gdraw", "gif", "go", "gpres",
        "groovy", "gsheet", "gzip", "html", "handlebars", "haskell", "haxe", "indd",
        "java", "javascript", "jpg", "json", "keynote", "kotlin", "latex", "lisp",
        "lua", "m4a", "markdown", "matlab", "mhtml", "mkv", "mov", "mp3", "mp4",
        "mpg", "mumps", "numbers", "nzb", "objc", "ocaml", "odg", "odi", "odp", "ods",
        "odt", "ogg", "ogv", "pages", "pascal", "pdf", "perl", "php", "pig", "png",
        "post", "powershell", "ppt", "pptx", "psd", "puppet", "python", "qtz", "r",
        "rtf", "ruby", "rust", "sql", "sass", "scala", "scheme", "sketch", "shell",
        "smalltalk", "svg", "swf", "swift", "tar", "tiff", "tsv", "vb", "vbscript",
        "vcard", "velocity", "verilog", "wav", "webm", "wmv", "xls", "xlsx", "xlsb",
        "xlsm", "xltx", "xml", "yaml", "zip"
    ]  # fmt: skip

    def __init__(
        self,
        action_id: str | None = None,
        filetypes: list[str] | None = None,
        max_files: int | None = None,
    ):
        super().__init__("file_input")
        self.action_id(action_id)
        self.filetypes(*filetypes or ())
        self.max_files(max_files)

    def filetypes(self, *filetypes: str) -> Self:
        return self._add_field(
            "filetypes",
            list(filetypes),
            validators=[Typed(str), Strings(*self.FILE_TYPES)],
        )

    def max_files(self, max_files: int | None) -> Self:
        return self._add_field(
            "max_files", max_files, validators=[Typed(int), Ints(1, 10)]
        )


class ImageEl(Component, AltTextMixin, ImageUrlMixin, SlackFileMixin):
    """
    Image element

    Displays an image as part of a larger block of content.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/image-element
    """

    def __init__(
        self,
        alt_text: str | None = None,
        image_url: str | None = None,
        slack_file: SlackFile | None = None,
    ):
        super().__init__("image")
        self.alt_text(alt_text)
        self.image_url(image_url)
        self.slack_file(slack_file)
        self._add_validator(OnlyOne("image_url", "slack_file"))


class MultiStaticSelect(
    Component,
    ActionIdMixin,
    OptionsMixin,
    OptionGroupsMixin,
    InitialOptionsMixin,
    ConfirmMixin,
    MaxSelectedItemsMixin,
    FocusOnLoadMixin,
    PlaceholderMixin,
):
    """
    Multi-select menu element (static options)

    Allows users to select multiple items from a list of options.

    This is the most basic form of select menu, with a static list of
    options passed in when defining the element.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/multi-select-menu-element#static_multi_select
    """

    def __init__(
        self,
        action_id: str | None = None,
        options: list[Option] | None = None,
        option_groups: list[OptionGroup] | None = None,
        initial_options: list[Option | OptionGroup] | None = None,
        confirm: Confirm | None = None,
        max_selected_items: int | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
    ):
        super().__init__("multi_static_select")
        self.action_id(action_id)
        self.options(*options or ())
        self.option_groups(*option_groups or ())
        self.initial_options(*initial_options or ())
        self.confirm(confirm)
        self.max_selected_items(max_selected_items)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)
        self._add_validator(OnlyOne("options", "option_groups"))
        # TODO: Doesn't handle the case where initial_options are set
        # but options or option_groups are empty
        self._add_validator(Within("initial_options", "options"))
        self._add_validator(Within("initial_options", "option_groups"))


class MultiExternalSelect(
    Component,
    ActionIdMixin,
    MinQueryLengthMixin,
    InitialOptionsMixin,
    ConfirmMixin,
    MaxSelectedItemsMixin,
    FocusOnLoadMixin,
    PlaceholderMixin,
):
    """
    Multi-select menu element (external data source)

    Allows users to select multiple items from a list of options.

    This menu will load its options from an external data source, allowing
    for a dynamic list of options.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/multi-select-menu-element#external_multi_select
    """

    def __init__(
        self,
        action_id: str | None = None,
        min_query_length: int | None = None,
        initial_options: list[Option | OptionGroup] | None = None,
        confirm: Confirm | None = None,
        max_selected_items: int | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
    ):
        super().__init__("multi_external_select")
        self.action_id(action_id)
        self.min_query_length(min_query_length)
        self.initial_options(*initial_options or ())
        self.confirm(confirm)
        self.max_selected_items(max_selected_items)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)


class MultiUsersSelect(
    Component,
    ActionIdMixin,
    ConfirmMixin,
    MaxSelectedItemsMixin,
    FocusOnLoadMixin,
    PlaceholderMixin,
):
    """
    Multi-select menu element (user list)

    Allows users to select multiple items from a list of options.

    This multi-select menu will populate its options with a list of Slack users
    visible to the current user in the active workspace.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/multi-select-menu-element#users_multi_select
    """

    def __init__(
        self,
        action_id: str | None = None,
        initial_users: list[str] | None = None,
        confirm: Confirm | None = None,
        max_selected_items: int | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
    ):
        super().__init__("multi_users_select")
        self.action_id(action_id)
        self.initial_users(*initial_users or ())
        self.confirm(confirm)
        self.max_selected_items(max_selected_items)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)

    def initial_users(self, *initial_users: str) -> Self:
        return self._add_field(
            "initial_users", list(initial_users), validators=[Typed(str), Length(1)]
        )

    def add_initial_user(self, user_id: str) -> Self:
        return self._add_field_value("initial_users", user_id)  # type: ignore[attr-defined]


class MultiConversationsSelect(
    Component,
    ActionIdMixin,
    DefaultToCurrentConversationMixin,
    ConfirmMixin,
    MaxSelectedItemsMixin,
    FilterMixin,
    FocusOnLoadMixin,
    PlaceholderMixin,
):
    """
    Multi-select menu element (conversations list)

    Allows users to select multiple items from a list of options.

    This multi-select menu will populate its options with a list of public and private
    channels, DMs, and MPIMs visible to the current user in the active workspace.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/multi-select-menu-element#conversation_multi_select
    """

    def __init__(
        self,
        action_id: str | None = None,
        initial_conversations: list[str] | None = None,
        default_to_current_conversation: bool | None = None,
        confirm: Confirm | None = None,
        max_selected_items: int | None = None,
        filter: ConversationFilter | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
    ):
        super().__init__("multi_conversations_select")
        self.action_id(action_id)
        self.initial_conversations(*initial_conversations or ())
        self.default_to_current_conversation(default_to_current_conversation)
        self.confirm(confirm)
        self.max_selected_items(max_selected_items)
        self.filter(filter)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)

    def initial_conversations(self, *initial_conversations: str) -> Self:
        return self._add_field(
            "initial_conversations",
            list(initial_conversations),
            validators=[Typed(str), Length(1)],
        )

    def add_initial_conversation(self, conversation_id: str) -> Self:
        return self._add_field_value("initial_conversations", conversation_id)  # type: ignore[attr-defined]


class MultiChannelsSelect(
    Component,
    ActionIdMixin,
    ConfirmMixin,
    MaxSelectedItemsMixin,
    FocusOnLoadMixin,
    PlaceholderMixin,
):
    """
    Multi-select menu element (public channels list)

    Allows users to select multiple items from a list of options.

    This multi-select menu will populate its options with a list of public
    channels visible to the current user in the active workspace.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/multi-select-menu-element#channel_multi_select
    """

    def __init__(
        self,
        action_id: str | None = None,
        initial_channels: list[str] | None = None,
        confirm: Confirm | None = None,
        max_selected_items: int | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
    ):
        super().__init__("multi_channels_select")
        self.action_id(action_id)
        self.initial_channels(*initial_channels or ())
        self.confirm(confirm)
        self.max_selected_items(max_selected_items)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)

    def initial_channels(self, *initial_channels: str) -> Self:
        return self._add_field(
            "initial_channels",
            list(initial_channels),
            validators=[Typed(str), Length(1)],
        )

    def add_initial_channel(self, channel_id: str) -> Self:
        return self._add_field_value("initial_channels", channel_id)  # type: ignore[attr-defined]


class NumberInput(
    Component,
    ActionIdMixin,
    DispatchActionConfigMixin,
    FocusOnLoadMixin,
    PlaceholderMixin,
):
    """
    Number input element

    Allows user to enter a number into a single-line field.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/number-input-element
    """

    def __init__(
        self,
        is_decimal_allowed: bool | None = None,
        action_id: str | None = None,
        initial_value: int | float | None = None,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        dispatch_action_config: DispatchActionConfig | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
    ):
        super().__init__("number_input")
        self.is_decimal_allowed(is_decimal_allowed)
        self.action_id(action_id)
        self.initial_value(initial_value)
        self.min_value(min_value)
        self.max_value(max_value)
        self.dispatch_action_config(dispatch_action_config)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)
        self._add_validator(Ranging("initial_value", "min_value", "max_value"))
        self._add_validator(
            DecimalAllowed(
                "is_decimal_allowed", "initial_value", "min_value", "max_value"
            )
        )

    def is_decimal_allowed(self, is_decimal_allowed: bool | None) -> Self:
        return self._add_field(
            "is_decimal_allowed",
            is_decimal_allowed,
            validators=[Typed(bool), Required()],
        )

    def initial_value(self, initial_value: int | float | None) -> Self:
        return self._add_field(
            "initial_value",
            initial_value,
            validators=[Typed(int, float)],
            stringify=True,
        )

    def min_value(self, min_value: int | float | None) -> Self:
        return self._add_field(
            "min_value", min_value, validators=[Typed(int, float)], stringify=True
        )

    def max_value(self, max_value: int | float | None) -> Self:
        return self._add_field(
            "max_value", max_value, validators=[Typed(int, float)], stringify=True
        )


class Overflow(Component, ActionIdMixin, OptionsMixin, ConfirmMixin):
    """
    Overflow menu element

    Allows users to press a button to view a list of options.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/overflow-menu-element
    """

    def __init__(
        self,
        action_id: str | None = None,
        options: list[Option] | None = None,
        confirm: Confirm | None = None,
    ):
        super().__init__("overflow")
        self._max_options = 5
        self.action_id(action_id)
        self.options(*options or ())
        self.confirm(confirm)


class PlainTextInput(
    Component,
    ActionIdMixin,
    DispatchActionConfigMixin,
    FocusOnLoadMixin,
    PlaceholderMixin,
):
    """
    Plain-text input element

    Allows users to enter freeform text data into a single-line or multi-line field.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/plain-text-input-element
    """

    def __init__(
        self,
        action_id: str | None = None,
        initial_value: str | None = None,
        multiline: bool | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        dispatch_action_config: DispatchActionConfig | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
    ):
        super().__init__("plain_text_input")
        self.action_id(action_id)
        self.initial_value(initial_value)
        self.multiline(multiline)
        self.min_length(min_length)
        self.max_length(max_length)
        self.dispatch_action_config(dispatch_action_config)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)
        self._add_validator(Ranging("initial_value", "min_length", "max_length"))

    def initial_value(self, initial_value: str | None) -> Self:
        return self._add_field(
            "initial_value", initial_value, validators=[Typed(str), Length(1, 3000)]
        )

    def multiline(self, multiline: bool | None = True) -> Self:
        return self._add_field("multiline", multiline, validators=[Typed(bool)])

    def min_length(self, min_length: int | None) -> Self:
        return self._add_field(
            "min_length", min_length, validators=[Typed(int), Ints(0, 3000)]
        )

    def max_length(self, max_length: int | None) -> Self:
        return self._add_field(
            "max_length", max_length, validators=[Typed(int), Ints(1, 3000)]
        )


class RadioButtons(
    Component, ActionIdMixin, OptionsMixin, ConfirmMixin, FocusOnLoadMixin
):
    """
    Radio button group element

    Allows users to choose one item from a list of possible options.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/radio-button-group-element
    """

    def __init__(
        self,
        action_id: str | None = None,
        options: list[Option] | None = None,
        initial_option: Option | None = None,
        confirm: Confirm | None = None,
        focus_on_load: bool | None = None,
    ):
        super().__init__("radio_buttons")
        self._max_options = 10
        self.action_id(action_id)
        self.options(*options or ())
        self.initial_option(initial_option)
        self.confirm(confirm)
        self.focus_on_load(focus_on_load)
        self._add_validator(Within("initial_option", "options"))

    def initial_option(self, initial_option: Option | None) -> Self:
        return self._add_field(
            "initial_option", initial_option, validators=[Typed(Option)]
        )


class RichTextInput(
    Component,
    ActionIdMixin,
    DispatchActionConfigMixin,
    FocusOnLoadMixin,
    PlaceholderMixin,
):
    """
    Rich text input element

    Allows users to enter formatted text in a WYSIWYG composer, offering the same
    messaging writing experience as in Slack.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/rich-text-input-element
    """

    def __init__(
        self,
        action_id: str | None = None,
        initial_value: "RichText | None" = None,
        dispatch_action_config: DispatchActionConfig | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
    ):
        super().__init__("rich_text_input")
        self.action_id(action_id)
        self.initial_value(initial_value)
        self.dispatch_action_config(dispatch_action_config)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)

    def initial_value(self, initial_value: "RichText | None") -> Self:
        return self._add_field(
            "initial_value", initial_value, validators=[Typed(RichText)]
        )


class StaticSelect(
    Component,
    ActionIdMixin,
    OptionsMixin,
    OptionGroupsMixin,
    InitialOptionMixin,
    ConfirmMixin,
    MaxSelectedItemsMixin,
    FocusOnLoadMixin,
    PlaceholderMixin,
):
    """
    Select menu element (static options)

    Allows users to choose an option from a drop down menu.

    This is the most basic form of select menu, with a static list of
    options passed in when defining the element.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/select-menu-element#static_select
    """

    def __init__(
        self,
        action_id: str | None = None,
        options: list[Option] | None = None,
        option_groups: list[OptionGroup] | None = None,
        initial_option: Option | OptionGroup | None = None,
        confirm: Confirm | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
    ):
        super().__init__("static_select")
        self.action_id(action_id)
        self.options(*options or ())
        self.option_groups(*option_groups or ())
        self.initial_option(initial_option)
        self.confirm(confirm)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)
        self._add_validator(OnlyOne("options", "option_groups"))
        # TODO: Doesn't handle the case where initial_option is set
        # but options or option_groups are empty
        self._add_validator(Within("initial_option", "options"))
        self._add_validator(Within("initial_option", "option_groups"))


class ExternalSelect(
    Component,
    ActionIdMixin,
    MinQueryLengthMixin,
    InitialOptionMixin,
    ConfirmMixin,
    MaxSelectedItemsMixin,
    FocusOnLoadMixin,
    PlaceholderMixin,
):
    """
    Select menu element (external data source)

    Allows users to choose an option from a drop down menu.

    This select menu will load its options from an external data source,
    allowing for a dynamic list of options.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/select-menu-element#external_select
    """

    def __init__(
        self,
        action_id: str | None = None,
        min_query_length: int | None = None,
        initial_option: Option | OptionGroup | None = None,
        confirm: Confirm | None = None,
        max_selected_items: int | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
    ):
        super().__init__("external_select")
        self.action_id(action_id)
        self.min_query_length(min_query_length)
        self.initial_option(initial_option)
        self.confirm(confirm)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)


class UsersSelect(
    Component,
    ActionIdMixin,
    ConfirmMixin,
    MaxSelectedItemsMixin,
    FocusOnLoadMixin,
    PlaceholderMixin,
):
    """
    Select menu element (user list)

    Allows users to choose an option from a drop down menu.

    This select menu will populate its options with a list of Slack users visible to
    the current user in the active workspace.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/select-menu-element#users_select
    """

    def __init__(
        self,
        action_id: str | None = None,
        initial_user: str | None = None,
        confirm: Confirm | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
    ):
        super().__init__("users_select")
        self.action_id(action_id)
        self.initial_user(initial_user)
        self.confirm(confirm)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)

    def initial_user(self, initial_user: str | None) -> Self:
        return self._add_field(
            "initial_user", initial_user, validators=[Typed(str), Length(1)]
        )


class ConversationsSelect(
    Component,
    ActionIdMixin,
    DefaultToCurrentConversationMixin,
    ConfirmMixin,
    ResponseUrlEnabledMixin,
    FilterMixin,
    MaxSelectedItemsMixin,
    FocusOnLoadMixin,
    PlaceholderMixin,
):
    """
    Select menu element (conversations list)

    Allows users to choose an option from a drop down menu.

    This select menu will populate its options with a list of public and
    private channels, DMs, and MPIMs visible to the current user
    in the active workspace.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/select-menu-element#conversations_select
    """

    def __init__(
        self,
        action_id: str | None = None,
        initial_conversation: str | None = None,
        default_to_current_conversation: bool | None = None,
        confirm: Confirm | None = None,
        response_url_enabled: bool | None = None,
        filter: ConversationFilter | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
    ):
        super().__init__("conversations_select")
        self.action_id(action_id)
        self.initial_conversation(initial_conversation)
        self.default_to_current_conversation(default_to_current_conversation)
        self.confirm(confirm)
        self.response_url_enabled(response_url_enabled)
        self.filter(filter)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)

    def initial_conversation(self, initial_conversation: str | None) -> Self:
        return self._add_field(
            "initial_conversation",
            initial_conversation,
            validators=[Typed(str), Length(1)],
        )


class ChannelsSelect(
    Component,
    ActionIdMixin,
    ConfirmMixin,
    ResponseUrlEnabledMixin,
    FocusOnLoadMixin,
    PlaceholderMixin,
):
    """
    Select menu element (public channels list)

    Allows users to choose an option from a drop down menu.

    This select menu will populate its options with a list of public channels visible
    to the current user in the active workspace.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/select-menu-element#channels_select
    """

    def __init__(
        self,
        action_id: str | None = None,
        initial_channel: str | None = None,
        confirm: Confirm | None = None,
        response_url_enabled: bool | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
    ):
        super().__init__("channels_select")
        self.action_id(action_id)
        self.initial_channel(initial_channel)
        self.confirm(confirm)
        self.response_url_enabled(response_url_enabled)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)

    def initial_channel(self, initial_channel: str | None) -> Self:
        return self._add_field(
            "initial_channel",
            initial_channel,
            validators=[Typed(str), Length(1)],
        )


class TimePicker(
    Component,
    ActionIdMixin,
    ConfirmMixin,
    FocusOnLoadMixin,
    PlaceholderMixin,
):
    """
    Time picker element

    Allows users to enter numerical data into a single-line field.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/time-picker-element
    """

    def __init__(
        self,
        action_id: str | None = None,
        initial_time: str | time | None = None,
        confirm: Confirm | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
        timezone: str | ZoneInfo | None = None,
    ):
        super().__init__("timepicker")
        self.action_id(action_id)
        self.initial_time(initial_time)
        self.confirm(confirm)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)
        self.timezone(timezone)

    def initial_time(self, initial_time: str | time | None) -> Self:
        if isinstance(initial_time, str):
            initial_time = datetime.strptime(initial_time, "%H:%M").time()
        return self._add_field("initial_time", initial_time, validators=[Typed(time)])

    def timezone(self, timezone: str | ZoneInfo | None) -> Self:
        if isinstance(timezone, str):
            timezone = ZoneInfo(timezone)
        return self._add_field("timezone", timezone, validators=[Typed(ZoneInfo)])


class UrlInput(
    Component,
    ActionIdMixin,
    DispatchActionConfigMixin,
    FocusOnLoadMixin,
    PlaceholderMixin,
):
    """
    URL input element

    Allows user to enter a URL into a single-line field.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/url-input-element
    """

    def __init__(
        self,
        action_id: str | None = None,
        initial_value: str | None = None,
        dispatch_action_config: DispatchActionConfig | None = None,
        focus_on_load: bool | None = None,
        placeholder: str | Text | None = None,
    ):
        super().__init__("url_text_input")
        self.action_id(action_id)
        self.initial_value(initial_value)
        self.dispatch_action_config(dispatch_action_config)
        self.focus_on_load(focus_on_load)
        self.placeholder(placeholder)

    def initial_value(self, initial_value: str | None) -> Self:
        return self._add_field(
            "initial_value", initial_value, validators=[Typed(str), Length(1, 74)]
        )


class WorkflowButton(
    Component, TextMixin, ActionIdMixin, StyleMixin, AccessibilityLabelMixin
):
    """
    Workflow button element

    Allows users to run a link trigger with customizable inputs.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/block-elements/workflow-button-element
    """

    def __init__(
        self,
        text: str | Text | None = None,
        workflow: Workflow | None = None,
        action_id: str | None = None,
        style: Literal["primary", "danger"] | None = None,
        accessibility_label: str | None = None,
    ):
        super().__init__("workflow_button")
        self.text(text)
        self.workflow(workflow)
        self.action_id(action_id)
        self.style(style)
        self.accessibility_label(accessibility_label)

    def workflow(self, workflow: Workflow | None) -> Self:
        return self._add_field("workflow", workflow, validators=[Typed(Workflow)])


"""
Blocks
"""


ActionElement: TypeAlias = (
    Button
    | Checkboxes
    | DatePicker
    | MultiStaticSelect
    | MultiExternalSelect
    | MultiUsersSelect
    | MultiConversationsSelect
    | MultiChannelsSelect
    | Overflow
    | RadioButtons
    | RichTextInput
    | StaticSelect
    | ExternalSelect
    | UsersSelect
    | ConversationsSelect
    | ChannelsSelect
    | TimePicker
    | WorkflowButton
)


class Actions(Component, BlockIdMixin):
    """
    Actions block

    Holds multiple interactive elements.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/actions-block
    """

    def __init__(
        self,
        elements: list[ActionElement] | None = None,
        block_id: str | None = None,
    ):
        super().__init__("actions")
        self.elements(*elements or ())
        self.block_id(block_id)

    def elements(self, *elements: ActionElement) -> Self:
        return self._add_field(
            "elements",
            list(elements),
            validators=[Typed(*get_args(ActionElement)), Required(), Length(1, 25)],
        )

    def add_element(self, element: ActionElement) -> Self:
        return self._add_field_value("elements", element)  # type: ignore[attr-defined]


ContextElement: TypeAlias = ImageEl | Text


class Context(Component, BlockIdMixin):
    """
    Context block

    Provides contextual info, which can include both images and text.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/context-block
    """

    def __init__(
        self,
        elements: list[ContextElement] | None = None,
        block_id: str | None = None,
    ):
        super().__init__("context")
        self.elements(*elements or ())
        self.block_id(block_id)

    def elements(self, *elements: ContextElement) -> Self:
        return self._add_field(
            "elements",
            list(elements),
            validators=[Typed(*get_args(ContextElement)), Required(), Length(1, 10)],
        )

    def add_element(self, element: ContextElement) -> Self:
        return self._add_field_value("elements", element)  # type: ignore[attr-defined]


class Divider(Component, BlockIdMixin):
    """
    Divider block

    Visually separates pieces of info inside of a message.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/divider-block
    """

    def __init__(self, block_id: str | None = None):
        super().__init__("divider")
        self.block_id(block_id)


class File(Component, BlockIdMixin):
    """
    File block

    Displays info about remote files.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/file-block
    """

    REMOTE: Final[Literal["remote"]] = "remote"

    def __init__(
        self,
        external_id: str | None = None,
        source: Literal["remote"] | None = None,
        block_id: str | None = None,
    ):
        super().__init__("file")
        self.external_id(external_id)
        self.source(source)
        self.block_id(block_id)

    def external_id(self, external_id: str | None) -> Self:
        return self._add_field(
            "external_id",
            external_id,
            validators=[Typed(str), Required(), Length(1, 255)],
        )

    def source(self, source: Literal["remote"] | None) -> Self:
        return self._add_field(
            "source",
            source,
            validators=[Typed(str), Required(), Strings(self.REMOTE)],
        )


class Header(Component, BlockIdMixin):
    """
    Header block

    Displays a larger-sized text.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/header-block
    """

    def __init__(self, text: str | Text | None = None, block_id: str | None = None):
        super().__init__("header")
        self.text(text)
        self.block_id(block_id)

    def text(self, text: str | Text | None) -> Self:
        return self._add_field(
            "text",
            str_to_plain(text),
            validators=[Typed(Text), Required(), Plain(), Length(1, 150)],
        )


class Image(Component, BlockIdMixin, AltTextMixin, ImageUrlMixin, SlackFileMixin):
    """
    Image block

    Displays an image.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/image-block
    """

    def __init__(
        self,
        alt_text: str | None = None,
        image_url: str | None = None,
        slack_file: SlackFile | None = None,
        title: str | Text | None = None,
        block_id: str | None = None,
    ):
        super().__init__("image")
        self.alt_text(alt_text)
        self.image_url(image_url)
        self.slack_file(slack_file)
        self.title(title)
        self.block_id(block_id)
        self._add_validator(OnlyOne("image_url", "slack_file"))

    def title(self, title: str | Text | None) -> Self:
        return self._add_field(
            "title",
            str_to_plain(title),
            validators=[Typed(Text), Plain(), Length(1, 2000)],
        )


InputElement: TypeAlias = (
    Checkboxes
    | DatePicker
    | DatetimePicker
    | EmailInput
    | FileInput
    | MultiStaticSelect
    | MultiExternalSelect
    | MultiUsersSelect
    | MultiConversationsSelect
    | MultiChannelsSelect
    | NumberInput
    | PlainTextInput
    | RadioButtons
    | RichTextInput
    | StaticSelect
    | ExternalSelect
    | UsersSelect
    | ConversationsSelect
    | ChannelsSelect
    | TimePicker
    | UrlInput
)


class Input(Component, BlockIdMixin):
    """
    Input block

    Collects information from users via elements.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/input-block#input
    """

    def __init__(
        self,
        label: str | Text | None = None,
        element: InputElement | None = None,
        dispatch_action: bool | None = None,
        hint: str | Text | None = None,
        optional: bool | None = None,
        block_id: str | None = None,
    ):
        super().__init__("input")
        self.label(label)
        self.element(element)
        self.dispatch_action(dispatch_action)
        self.hint(hint)
        self.optional(optional)
        self.block_id(block_id)

    def label(self, label: str | Text | None) -> Self:
        return self._add_field(
            "label",
            str_to_plain(label),
            validators=[Typed(Text), Required(), Plain(), Length(1, 2000)],
        )

    def element(self, element: InputElement | None) -> Self:
        return self._add_field(
            "element", element, validators=[Typed(*get_args(InputElement)), Required()]
        )

    def dispatch_action(self, dispatch_action: bool | None = True):
        return self._add_field(
            "dispatch_action", dispatch_action, validators=[Typed(bool)]
        )

    def hint(self, hint: str | Text | None) -> Self:
        return self._add_field(
            "hint",
            str_to_plain(hint),
            validators=[Typed(Text), Plain(), Length(1, 2000)],
        )

    def optional(self, optional: bool | None = True) -> Self:
        return self._add_field("optional", optional, validators=[Typed(bool)])


class Markdown(Component, BlockIdMixin):
    """
    Markdown block

    Displays formatted markdown.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/markdown-block
    """

    def __init__(self, text: str | None = None, block_id: str | None = None):
        super().__init__("markdown")
        self.text(text)
        self.block_id(block_id)

    def text(self, text: str | None) -> Self:
        return self._add_field(
            "text", text, validators=[Typed(str), Required(), Length(1, 12000)]
        )


class RichBroadcastEl(Component):
    """
    Rich broadcast text element

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/rich-text-block#broadcast-element-type
    """

    HERE: Final[Literal["here"]] = "here"
    CHANNEL: Final[Literal["channel"]] = "channel"
    EVERYONE: Final[Literal["everyone"]] = "everyone"

    def __init__(self, range: Literal["here", "channel", "everyone"] | None = None):
        super().__init__("broadcast")
        self.range(range)

    def range(self, range: Literal["here", "channel", "everyone"] | None) -> Self:
        return self._add_field(
            "range",
            range,
            validators=[
                Typed(str),
                Required(),
                Strings(self.HERE, self.CHANNEL, self.EVERYONE),
            ],
        )


class RichStyle(Component):
    """
    Rich style object

    An object of six optional boolean properties that dictate style
    """

    def __init__(
        self,
        *,
        bold: bool | None = None,
        italic: bool | None = None,
        strike: bool | None = None,
        code: bool | None = None,
        highlight: bool | None = None,
        client_highlight: bool | None = None,
        unlink: bool | None = None,
    ):
        super().__init__()
        self.bold(bold)
        self.italic(italic)
        self.strike(strike)
        self.code(code)
        self.highlight(highlight)
        self.client_highlight(client_highlight)
        self.unlink(unlink)

    def bold(self, bold: bool | None = True) -> Self:
        return self._add_field("bold", bold, validators=[Typed(bool)])

    def italic(self, italic: bool | None = True) -> Self:
        return self._add_field("italic", italic, validators=[Typed(bool)])

    def strike(self, strike: bool | None = True) -> Self:
        return self._add_field("strike", strike, validators=[Typed(bool)])

    def code(self, code: bool | None = True) -> Self:
        return self._add_field("code", code, validators=[Typed(bool)])

    def highlight(self, highlight: bool | None = True) -> Self:
        return self._add_field("highlight", highlight, validators=[Typed(bool)])

    def client_highlight(self, client_highlight: bool | None = True) -> Self:
        return self._add_field(
            "client_highlight", client_highlight, validators=[Typed(bool)]
        )

    def unlink(self, unlink: bool | None = True) -> Self:
        return self._add_field("unlink", unlink, validators=[Typed(bool)])


class RichColorEl(Component):
    """
    Rich color text element

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/rich-text-block#color-element-type
    """

    def __init__(self, value: str | None = None):
        super().__init__("color")
        self.value(value)

    def value(self, value: str | None) -> Self:
        return self._add_field(
            "value",
            value,
            validators=[Typed(str), Required(), HexColor()],
        )


class RichChannelEl(Component, RichStyleMixin):
    """
    Rich channel text element

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/rich-text-block#channel-element-type
    """

    def __init__(
        self,
        channel_id: str | None = None,
        style: RichStyle | None = None,
    ):
        super().__init__("channel")
        self.channel_id(channel_id)
        self.style(style)
        self._add_validator(StyledCorrectly(extended=True))

    # TODO: validate channel_id
    def channel_id(self, channel_id: str | None) -> Self:
        return self._add_field(
            "channel_id", channel_id, validators=[Typed(str), Required(), Length(1)]
        )


class RichDateEl(Component, UrlMixin):
    """
    Rich date text element

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/rich-text-block#date-element-type
    """

    DAY_DIVIDER_PRETTY = "{day_divider_pretty}"
    DATE_NUM = "{date_num}"
    DATE_SLASH = "{date_slash}"
    DATE_LONG = "{date_long}"
    DATE_LONG_FULL = "{date_long_full}"
    DATE_LONG_PRETTY = "{date_long_pretty}"
    DATE = "{date}"
    DATE_PRETTY = "{date_pretty}"
    DATE_SHORT = "{date_short}"
    DATE_SHORT_PRETTY = "{date_short_pretty}"
    TIME = "{time}"
    TIME_SECS = "{time_secs}"
    AGO = "{ago}"

    def __init__(
        self,
        timestamp: int | datetime | None = None,
        format: str | None = None,
        url: str | None = None,
        fallback: str | None = None,
    ):
        super().__init__("date")
        self.timestamp(timestamp)
        self.format(format)
        self.url(url)
        self.fallback(fallback)

    def timestamp(self, timestamp: int | datetime | None) -> Self:
        if isinstance(timestamp, datetime):
            timestamp = int(timestamp.timestamp())
        return self._add_field(
            "timestamp", timestamp, validators=[Typed(int), Required()]
        )

    def format(self, format: str | None) -> Self:
        return self._add_field(
            "format", format, validators=[Typed(str), Required(), Length(1)]
        )

    def fallback(self, fallback: str | None) -> Self:
        return self._add_field("fallback", fallback, validators=[Typed(str), Length(1)])


class RichEmojiEl(Component):
    """
    Rich emoji text element

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/rich-text-block#emoji-element-type
    """

    def __init__(self, name: str | None = None, unicode: str | None = None):
        super().__init__("emoji")
        self.name(name)
        self.unicode(unicode)

    def name(self, name: str | None) -> Self:
        return self._add_field(
            "name", name, validators=[Typed(str), Required(), Length(1)]
        )

    # TODO: validate unicode code point "^[0-9a-f-]+$"
    def unicode(self, unicode: str | None) -> Self:
        return self._add_field("unicode", unicode, validators=[Typed(str), Length(1)])


class RichLinkEl(Component, UrlMixin, RichStyleMixin):
    """
    Rich link text element

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/rich-text-block#link-element-type
    """

    def __init__(
        self,
        url: str | None = None,
        text: str | None = None,
        unsafe: bool | None = None,
        style: RichStyle | None = None,
    ):
        super().__init__("link")
        self.url(url)
        self.text(text)
        self.unsafe(unsafe)
        self.style(style)
        self._add_validator(StyledCorrectly())

    def url(self, url: str | None) -> Self:
        return self._add_field(  # type: ignore[attr-defined]
            "url", url, validators=[Typed(str), Required(), Length(1, 3000)]
        )

    def text(self, text: str | None) -> Self:
        return self._add_field("text", text, validators=[Typed(str), Length(1)])

    def unsafe(self, unsafe: bool | None = True) -> Self:
        return self._add_field("unsafe", unsafe, validators=[Typed(bool)])


class RichTextEl(Component, RichStyleMixin):
    """
    Rich text element

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/rich-text-block#text-element-type
    """

    def __init__(self, text: str | None = None, style: RichStyle | None = None):
        super().__init__("text")
        self.text(text)
        self.style(style)
        self._add_validator(StyledCorrectly())

    def text(self, text: str | None) -> Self:
        return self._add_field(
            "text", text, validators=[Typed(str), Required(), Length(1)]
        )


class RichUserEl(Component, RichStyleMixin):
    """
    Rich user text element

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/rich-text-block#user-element-type
    """

    def __init__(self, user_id: str | None = None, style: RichStyle | None = None):
        super().__init__("user")
        self.user_id(user_id)
        self.style(style)
        self._add_validator(StyledCorrectly(extended=True))

    # TODO: validate user_id
    def user_id(self, user_id: str | None) -> Self:
        return self._add_field(
            "user_id", user_id, validators=[Typed(str), Required(), Length(1)]
        )


class RichUserGroupEl(Component, RichStyleMixin):
    """
    Rich usergroup text element

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/rich-text-block#user-group-element-type
    """

    def __init__(self, usergroup_id: str | None = None, style: RichStyle | None = None):
        super().__init__("usergroup")
        self.usergroup_id(usergroup_id)
        self.style(style)
        self._add_validator(StyledCorrectly(extended=True))

    # TODO: validate usergroup_id
    def usergroup_id(self, usergroup_id: str | None) -> Self:
        return self._add_field(
            "usergroup_id", usergroup_id, validators=[Typed(str), Required(), Length(1)]
        )


RichTextElement: TypeAlias = (
    RichBroadcastEl
    | RichColorEl
    | RichChannelEl
    | RichDateEl
    | RichEmojiEl
    | RichLinkEl
    | RichTextEl
    | RichUserEl
    | RichUserGroupEl
)


class RichTextSection(Component, RichTextElementsMixin):
    """
    Rich text section object

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/rich-text-block#rich_text_section
    """

    def __init__(self, elements: list[RichTextElement] | None = None):
        super().__init__("rich_text_section")
        self.elements(*elements or ())


class RichTextList(Component, RichBorderMixin):
    """
    Rich text list object

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/rich-text-block#rich_text_list
    """

    BULLET: Final[Literal["bullet"]] = "bullet"
    ORDERED: Final[Literal["ordered"]] = "ordered"

    def __init__(
        self,
        style: Literal["bullet", "ordered"] | None = None,
        elements: list[RichTextSection] | None = None,
        indent: int | None = None,
        offset: int | None = None,
        border: int | None = None,
    ):
        super().__init__("rich_text_list")
        self.style(style)
        self.elements(*elements or ())
        self.indent(indent)
        self.offset(offset)
        self.border(border)

    def style(self, style: Literal["bullet", "ordered"] | None) -> Self:
        return self._add_field(
            "style",
            style,
            validators=[Typed(str), Required(), Strings(self.BULLET, self.ORDERED)],
        )

    def elements(self, *elements: RichTextSection) -> Self:
        return self._add_field(
            "elements",
            list(elements),
            validators=[Typed(RichTextSection), Required()],
        )

    def add_element(self, element: RichTextSection) -> Self:
        return self._add_field_value("elements", element)  # type: ignore[attr-defined]

    def indent(self, indent: int | None) -> Self:
        return self._add_field("indent", indent, validators=[Typed(int), Ints(max=6)])

    def offset(self, offset: int | None) -> Self:
        return self._add_field("offset", offset, validators=[Typed(int), Ints(max=6)])


class RichTextPreformatted(Component, RichTextElementsMixin, RichBorderMixin):
    """
    Rich text preformatted object

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/rich-text-block#rich_text_preformatted
    """

    def __init__(
        self, elements: list[RichTextElement] | None = None, border: int | None = None
    ):
        super().__init__("rich_text_preformatted")
        self.elements(*elements or ())
        self.border(border)


class RichTextQuote(Component, RichTextElementsMixin, RichBorderMixin):
    """
    Rich text quote object

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/rich-text-block#rich_text_quote
    """

    def __init__(
        self, elements: list[RichTextElement] | None = None, border: int | None = None
    ):
        super().__init__("rich_text_quote")
        self.elements(*elements or ())
        self.border(border)


RichTextObject: TypeAlias = (
    RichTextSection | RichTextList | RichTextPreformatted | RichTextQuote
)


class RichText(Component, BlockIdMixin):
    """
    Rich text block

    Displays formatted, structured representation of text.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/rich-text-block
    """

    def __init__(
        self, elements: list[RichTextObject] | None = None, block_id: str | None = None
    ):
        super().__init__("rich_text")
        self.elements(*elements or ())
        self.block_id(block_id)

    def elements(self, *elements: RichTextObject) -> Self:
        return self._add_field(
            "elements",
            list(elements),
            validators=[Typed(*get_args(RichTextObject)), Required()],
        )

    def add_element(self, element: RichTextObject) -> Self:
        return self._add_field_value("elements", element)  # type: ignore[attr-defined]


SectionElement: TypeAlias = (
    Button
    | Checkboxes
    | DatePicker
    | ImageEl
    | MultiStaticSelect
    | MultiExternalSelect
    | MultiUsersSelect
    | MultiConversationsSelect
    | MultiChannelsSelect
    | Overflow
    | RadioButtons
    | StaticSelect
    | ExternalSelect
    | UsersSelect
    | ConversationsSelect
    | ChannelsSelect
    | TimePicker
    | WorkflowButton
)


class Section(Component, BlockIdMixin):
    """
    Section block

    Displays text, possibly alongside elements.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/section-block
    """

    def __init__(
        self,
        text: str | Text | None = None,
        fields: list[Text] | None = None,
        accessory: SectionElement | None = None,
        expand: bool | None = None,
        block_id: str | None = None,
    ):
        super().__init__("section")
        self.text(text)
        self.fields(*fields or ())
        self.accessory(accessory)
        self.expand(expand)
        self.block_id(block_id)
        self._add_validator(AtLeastOne("text", "fields"))

    def text(self, text: str | Text | None) -> Self:
        if isinstance(text, str):
            text = Text(text)
        return self._add_field("text", text, validators=[Typed(Text), Length(1, 3000)])

    def fields(self, *fields: str | Text) -> Self:
        return self._add_field(
            "fields",
            [Text(f) if isinstance(f, str) else f for f in list(fields)],
            validators=[Typed(Text)],
        )

    def add_field(self, field: str | Text) -> Self:
        return self._add_field_value("fields", field)  # type: ignore[attr-defined]

    def accessory(self, accessory: SectionElement | None) -> Self:
        return self._add_field(
            "accessory", accessory, validators=[Typed(*get_args(SectionElement))]
        )

    def expand(self, expand: bool | None = True) -> Self:
        return self._add_field("expand", expand, validators=[Typed(bool)])


class Video(Component, BlockIdMixin):
    """
    Video block

    Displays an embedded video player.

    Slack docs:
        https://docs.slack.dev/reference/block-kit/blocks/video-block
    """

    def __init__(
        self,
        title: str | Text | None = None,
        title_url: str | None = None,
        description: str | Text | None = None,
        alt_text: str | None = None,
        video_url: str | None = None,
        thumbnail_url: str | None = None,
        provider_icon_url: str | None = None,
        provider_name: str | None = None,
        author_name: str | None = None,
        block_id: str | None = None,
    ):
        super().__init__("video")
        self.title(title)
        self.title_url(title_url)
        self.description(description)
        self.alt_text(alt_text)
        self.video_url(video_url)
        self.thumbnail_url(thumbnail_url)
        self.provider_icon_url(provider_icon_url)
        self.provider_name(provider_name)
        self.author_name(author_name)
        self.block_id(block_id)

    def title(self, title: str | Text | None) -> Self:
        return self._add_field(
            "title",
            str_to_plain(title),
            validators=[Typed(Text), Required(), Plain(), Length(1, 200)],
        )

    def title_url(self, title_url: str | None) -> Self:
        return self._add_field(
            "title_url", title_url, validators=[Typed(str), Length(1, 2000)]
        )

    def description(self, description: str | Text | None) -> Self:
        return self._add_field(
            "description",
            str_to_plain(description),
            validators=[Typed(Text), Plain(), Length(1, 200)],
        )

    def alt_text(self, alt_text: str | None) -> Self:
        return self._add_field(
            "alt_text", alt_text, validators=[Typed(str), Required(), Length(1)]
        )

    def video_url(self, video_url: str | None) -> Self:
        return self._add_field(
            "video_url", video_url, validators=[Typed(str), Length(1, 2000)]
        )

    def thumbnail_url(self, thumbnail_url: str | None) -> Self:
        return self._add_field(
            "thumbnail_url", thumbnail_url, validators=[Typed(str), Length(1, 2000)]
        )

    def provider_icon_url(self, provider_icon_url: str | None) -> Self:
        return self._add_field(
            "provider_icon_url",
            provider_icon_url,
            validators=[Typed(str), Length(1, 2000)],
        )

    def provider_name(self, provider_name: str | None) -> Self:
        return self._add_field(
            "provider_name", provider_name, validators=[Typed(str), Length(1, 50)]
        )

    def author_name(self, author_name: str | None) -> Self:
        return self._add_field(
            "author_name", author_name, validators=[Typed(str), Length(1, 50)]
        )


"""
Surfaces
"""

MessageBlock: TypeAlias = (
    Actions
    | Context
    | Divider
    | File
    | Header
    | Image
    | Input
    | Markdown
    | RichText
    | Section
    | Video
)


class Message(Component):
    """
    Message surface

    Slack docs:
        https://api.slack.com/surfaces/messages
    """

    def __init__(
        self,
        text: str | None = None,
        blocks: list[MessageBlock] | None = None,
        thread_ts: str | int | float | None = None,
        mrkdwn: bool | None = None,
    ):
        super().__init__()
        self.text(text)
        self.blocks(*blocks or ())
        self.thread_ts(thread_ts)
        self.mrkdwn(mrkdwn)
        self._add_validator(AtLeastOne("text", "blocks"))

    def text(self, text: str | None) -> Self:
        return self._add_field("text", text, validators=[Typed(str)])

    def blocks(self, *blocks: MessageBlock) -> Self:
        return self._add_field(
            "blocks", list(blocks), validators=[Typed(*get_args(MessageBlock))]
        )

    def add_block(self, block: MessageBlock) -> Self:
        return self._add_field_value("blocks", block)

    def thread_ts(self, thread_ts: str | int | float | None) -> Self:
        if isinstance(thread_ts, int | float):
            thread_ts = str(thread_ts)
        return self._add_field(
            "thread_ts", thread_ts, validators=[Typed(str), Length(1)]
        )

    def mrkdwn(self, mrkdwn: bool | None = True) -> Self:
        return self._add_field("mrkdwn", mrkdwn, validators=[Typed(bool)])


ModalBlock: TypeAlias = (
    Actions | Context | Divider | Header | Image | Input | RichText | Section | Video
)


class Modal(
    Component, BlocksMixin, PrivateMetadataMixin, CallbackIdMixin, ExternalIdMixin
):
    """
    Modal surface

    Slack docs:
        https://docs.slack.dev/surfaces/modals
    """

    def __init__(
        self,
        title: str | Text | None = None,
        blocks: list[ModalBlock] | None = None,
        submit: str | Text | None = None,
        close: str | Text | None = None,
        private_metadata: Any = None,
        callback_id: str | None = None,
        clear_on_close: bool | None = None,
        notify_on_close: bool | None = None,
        external_id: str | None = None,
        submit_disabled: bool | None = None,
    ):
        super().__init__("modal")
        self.title(title)
        self.blocks(*blocks or ())
        self.submit(submit)
        self.close(close)
        self.private_metadata(private_metadata)
        self.callback_id(callback_id)
        self.clear_on_close(clear_on_close)
        self.notify_on_close(notify_on_close)
        self.external_id(external_id)
        self.submit_disabled(submit_disabled)

    def title(self, title: str | Text | None) -> Self:
        return self._add_field(
            "title",
            str_to_plain(title),
            validators=[Typed(Text), Required(), Plain(), Length(1, 24)],
        )

    # TODO: required when an input is within the blocks
    def submit(self, submit: str | Text | None) -> Self:
        return self._add_field(
            "submit",
            str_to_plain(submit),
            validators=[Typed(Text), Plain(), Length(1, 24)],
        )

    def close(self, close: str | Text | None) -> Self:
        return self._add_field(
            "close",
            str_to_plain(close),
            validators=[Typed(Text), Plain(), Length(1, 24)],
        )

    def clear_on_close(self, clear_on_close: bool | None = True) -> Self:
        return self._add_field(
            "clear_on_close", clear_on_close, validators=[Typed(bool)]
        )

    def notify_on_close(self, notify_on_close: bool | None = True) -> Self:
        return self._add_field(
            "notify_on_close", notify_on_close, validators=[Typed(bool)]
        )

    def submit_disabled(self, submit_disabled: bool | None = True) -> Self:
        return self._add_field(
            "submit_disabled", submit_disabled, validators=[Typed(bool)]
        )


HomeBlock: TypeAlias = (
    Actions | Context | Divider | Header | Image | Input | RichText | Section | Video
)


class Home(
    Component, BlocksMixin, PrivateMetadataMixin, CallbackIdMixin, ExternalIdMixin
):
    """
    App Home surface

    Slack docs:
        https://docs.slack.dev/surfaces/app-home
    """

    def __init__(
        self,
        blocks: list[HomeBlock] | None = None,
        private_metadata: Any = None,
        callback_id: str | None = None,
        external_id: str | None = None,
    ):
        super().__init__("home")
        self.blocks(*blocks or ())
        self.private_metadata(private_metadata)
        self.callback_id(callback_id)
        self.external_id(external_id)
