import itertools
from datetime import date
from typing import List, Optional

from pydantic import root_validator
from pydantic.networks import AnyUrl, HttpUrl

from blockkit.components import NewComponent
from blockkit.fields import (
    ArrayField,
    BooleanField,
    IntegerField,
    ObjectField,
    StringField,
    TextField,
    UrlField,
    ValidationError,
)
from blockkit.objects import PlainText
from blockkit.validators import (
    validate_choices,
    validate_date,
    validate_int_range,
    validate_list_size,
    validate_string_length,
    validate_text_length,
    validator,
)

from . import Confirm, DispatchActionConfig, Filter, Option, OptionGroup
from .components import Component


class Element(Component):
    type = StringField()


class ActionableElement(Element):
    action_id = StringField(max_length=255)


class ActionableComponent(NewComponent):
    action_id: Optional[str] = None

    _validate_action_id = validator("action_id", validate_string_length, max_len=255)


class Button(ActionableComponent):
    type: str = "button"
    text: PlainText
    url: Optional[AnyUrl] = None
    value: Optional[str] = None
    style: Optional[str] = None
    confirm: Optional[Confirm] = None

    def __init__(
        self,
        *,
        text: PlainText,
        action_id: Optional[str] = None,
        url: Optional[AnyUrl] = None,
        value: Optional[str] = None,
        style: Optional[str] = None,
        confirm: Optional[Confirm] = None,
    ):
        super().__init__(
            text=text,
            action_id=action_id,
            url=url,
            value=value,
            style=style,
            confirm=confirm,
        )

    _validate_text = validator("text", validate_text_length, max_len=75)
    _validate_url = validator("url", validate_string_length, max_len=3000)
    _validate_value = validator("value", validate_string_length, max_len=2000)
    _validate_style = validator(
        "style", validate_choices, choices=("primary", "danger")
    )


class Checkboxes(ActionableComponent):
    type: str = "checkboxes"
    options: List[Option]
    initial_options: Optional[List[Option]] = None
    confirm: Optional[Confirm] = None

    def __init__(
        self,
        *,
        options: List[Option],
        action_id: Optional[str] = None,
        initial_options: Optional[List[Option]] = None,
        confirm: Optional[Confirm] = None,
    ):
        super().__init__(
            options=options,
            action_id=action_id,
            initial_options=initial_options,
            confirm=confirm,
        )

    _validate_options = validator("options", validate_list_size, min_len=1, max_len=10)
    _validate_initial_options = validator(
        "initial_options", validate_list_size, min_len=1, max_len=10
    )

    @root_validator
    def _validate_initial_within_options(cls, values):
        initial_options = values.get("initial_options")
        options = values.get("options")

        if initial_options is not None:
            for initial_option in initial_options:
                if initial_option not in options:
                    raise ValueError(f"Option {initial_option} isn't within {options}")
        return values


class DatePicker(ActionableComponent):
    type: str = "datepicker"
    placeholder: Optional[PlainText] = None
    initial_date: Optional[date] = None
    confirm: Optional[Confirm] = None

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        placeholder: Optional[PlainText] = None,
        initial_date: Optional[date] = None,
        confirm: Optional[Confirm] = None,
    ):
        super().__init__(
            action_id=action_id,
            placeholder=placeholder,
            initial_date=initial_date,
            confirm=confirm,
        )

    _validate_placeholder = validator("placeholder", validate_text_length, max_len=150)
    _validate_initial_date = validator("initial_date", validate_date)


class Image(NewComponent):
    type: str = "image"
    image_url: HttpUrl
    alt_text: str

    def __init__(self, *, image_url: HttpUrl, alt_text: str):
        super().__init__(image_url=image_url, alt_text=alt_text)


class Select(ActionableElement):
    placeholder = TextField(plain=True, max_length=150)
    confirm = ObjectField(Confirm)


class StaticSelectBase(Select):
    options = ArrayField(Option, max_items=100)
    option_groups = ArrayField(OptionGroup, max_items=100)


class NewSelect(ActionableComponent):
    placeholder: PlainText
    confirm: Optional[Confirm] = None

    _validate_placeholder = validator("placeholder", validate_text_length, max_len=150)


class NewStaticSelectBase(NewSelect):
    options: Optional[List[Option]] = None
    option_groups: Optional[List[OptionGroup]] = None

    _validate_options = validator("options", validate_list_size, min_len=1, max_len=100)
    _validate_option_groups = validator(
        "option_groups", validate_list_size, min_len=1, max_len=100
    )


class StaticSelect(NewStaticSelectBase):
    type: str = "static_select"
    initial_option: Optional[Option] = None

    def __init__(
        self,
        *,
        placeholder: PlainText,
        action_id: Optional[str] = None,
        options: Optional[List[Option]] = None,
        option_groups: Optional[List[OptionGroup]] = None,
        initial_option: Optional[Option] = None,
        confirm: Optional[Confirm] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            options=options,
            option_groups=option_groups,
            initial_option=initial_option,
            confirm=confirm,
        )

    @root_validator
    def _validate_values(cls, values):
        initial_option = values.get("initial_option")
        options = values.get("options")
        option_groups = values.get("option_groups")

        if not any((options, option_groups)) or options and option_groups:
            raise ValueError("You must provide either options or option_groups")

        if None not in (initial_option, options) and initial_option not in options:
            raise ValueError(f"Option {initial_option} isn't within {options}")

        if None not in (initial_option, option_groups):
            if initial_option not in itertools.chain(
                *[og.options for og in option_groups]
            ):
                raise ValueError(
                    f"Option {initial_option} isn't within {option_groups}"
                )

        return values


class ExternalSelectBase(Select):
    min_query_length = IntegerField()


class NewExternalSelectBase(NewSelect):
    min_query_length: Optional[int] = None

    _validate_min_query_length = validator(
        "min_query_length", validate_int_range, min_value=0, max_value=999
    )


class ExternalSelect(NewExternalSelectBase):
    type: str = "external_select"
    initial_option: Optional[Option] = None

    def __init__(
        self,
        *,
        placeholder: PlainText,
        action_id: Optional[str] = None,
        initial_option: Optional[Option] = None,
        min_query_length: Optional[int] = None,
        confirm: Optional[Confirm] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_option=initial_option,
            min_query_length=min_query_length,
            confirm=confirm,
        )


class UsersSelect(NewSelect):
    type: str = "users_select"
    initial_user: Optional[str] = None

    def __init__(
        self,
        *,
        placeholder: PlainText,
        action_id: Optional[str] = None,
        initial_user: Optional[str] = None,
        confirm: Optional[Confirm] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_user=initial_user,
            confirm=confirm,
        )


class ConversationsSelect(NewSelect):
    type: str = "conversations_select"
    initial_conversation: Optional[str] = None
    default_to_current_conversation: Optional[bool] = None
    response_url_enabled: Optional[bool] = None
    filter: Optional[Filter] = None

    def __init__(
        self,
        *,
        placeholder: PlainText,
        action_id: Optional[str] = None,
        initial_conversation: Optional[str] = None,
        default_to_current_conversation: Optional[bool] = None,
        confirm: Optional[Confirm] = None,
        response_url_enabled: Optional[bool] = None,
        filter: Optional[Filter] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_conversation=initial_conversation,
            default_to_current_conversation=default_to_current_conversation,
            confirm=confirm,
            response_url_enabled=response_url_enabled,
            filter=filter,
        )


class ChannelsSelect(NewSelect):
    type: str = "channels_select"
    initial_channel: Optional[str] = None
    response_url_enabled: Optional[bool] = None

    def __init__(
        self,
        *,
        placeholder: PlainText,
        action_id: Optional[str] = None,
        initial_channel: Optional[str] = None,
        confirm: Optional[Confirm] = None,
        response_url_enabled: Optional[bool] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_channel=initial_channel,
            confirm=confirm,
            response_url_enabled=response_url_enabled,
        )


class MultiStaticSelect(StaticSelectBase):
    initial_options = ArrayField(Option, OptionGroup, max_items=100)
    max_selected_items = IntegerField()

    def __init__(
        self,
        placeholder,
        action_id,
        options=None,
        option_groups=None,
        initial_options=None,
        confirm=None,
        max_selected_items=None,
    ):
        if options and option_groups:
            raise ValidationError("You can specify either options or option_groups.")

        super().__init__(
            "multi_static_select",
            action_id,
            placeholder,
            confirm,
            options,
            option_groups,
            initial_options,
            max_selected_items,
        )


class MultiExternalSelect(ExternalSelectBase):
    initial_options = ArrayField(Option, OptionGroup, max_items=100)
    max_selected_items = IntegerField()

    def __init__(
        self,
        placeholder,
        action_id,
        min_query_length=None,
        initial_options=None,
        confirm=None,
        max_selected_items=None,
    ):
        super().__init__(
            "multi_external_select",
            action_id,
            placeholder,
            confirm,
            min_query_length,
            initial_options,
            max_selected_items,
        )


class MultiUsersSelect(Select):
    initial_users = ArrayField(str)
    max_selected_items = IntegerField()

    def __init__(
        self,
        placeholder,
        action_id,
        initial_users=None,
        confirm=None,
        max_selected_items=None,
    ):
        super().__init__(
            "multi_users_select",
            action_id,
            placeholder,
            confirm,
            initial_users,
            max_selected_items,
        )


class MultiConversationsSelect(Select):
    initial_conversations = ArrayField(str)
    default_to_current_conversation = BooleanField()
    max_selected_items = IntegerField()
    filter = ObjectField(Filter)

    def __init__(
        self,
        placeholder,
        action_id,
        initial_conversations=None,
        default_to_current_conversation=None,
        confirm=None,
        max_selected_items=None,
        filter=None,
    ):
        super().__init__(
            "multi_conversations_select",
            action_id,
            placeholder,
            confirm,
            initial_conversations,
            default_to_current_conversation,
            max_selected_items,
            filter,
        )


class MultiChannelsSelect(Select):
    initial_channels = ArrayField(str)
    max_selected_items = IntegerField()

    def __init__(
        self,
        placeholder,
        action_id,
        initial_channels=None,
        confirm=None,
        max_selected_items=None,
    ):
        super().__init__(
            "multi_channels_select",
            action_id,
            placeholder,
            confirm,
            initial_channels,
            max_selected_items,
        )


class Overflow(ActionableElement):
    options = ArrayField(Option, min_items=1, max_items=5)
    confirm = ObjectField(Confirm)

    def __init__(self, action_id, options, confirm=None):
        super().__init__("overflow", action_id, options, confirm)


class PlainTextInput(ActionableElement):
    placeholder = TextField(plain=True, max_length=150)
    initial_value = StringField()
    multiline = BooleanField()
    min_length = IntegerField(max_value=3000)
    max_length = IntegerField()
    dispatch_action_config = ObjectField(DispatchActionConfig)

    def __init__(
        self,
        action_id,
        placeholder=None,
        initial_value=None,
        multiline=None,
        min_length=None,
        max_length=None,
        dispatch_action_config=None,
    ):
        super().__init__(
            "plain_text_input",
            action_id,
            placeholder,
            initial_value,
            multiline,
            min_length,
            max_length,
            dispatch_action_config,
        )


class RadioButtons(ActionableElement):
    options = ArrayField(Option)
    initial_option = ObjectField(Option)
    confirm = ObjectField(Confirm)

    def __init__(self, action_id, options, initial_option=None, confirm=None):
        super().__init__("radio_buttons", action_id, options, initial_option, confirm)
