import itertools
from datetime import date, time
from typing import List, Optional

from pydantic import root_validator
from pydantic.networks import AnyUrl, HttpUrl

from blockkit.components import Component
from blockkit.objects import (
    Confirm,
    DispatchActionConfig,
    Filter,
    Option,
    OptionGroup,
    PlainText,
)
from blockkit.validators import (
    validate_choices,
    validate_date,
    validate_int_range,
    validate_list_size,
    validate_string_length,
    validate_text_length,
    validate_time,
    validator,
)

__all__ = [
    "Button",
    "ChannelsSelect",
    "Checkboxes",
    "ConversationsSelect",
    "DatePicker",
    "ExternalSelect",
    "Image",
    "MultiChannelsSelect",
    "MultiConversationsSelect",
    "MultiExternalSelect",
    "MultiStaticSelect",
    "MultiUsersSelect",
    "Overflow",
    "PlainTextInput",
    "RadioButtons",
    "StaticSelect",
    "Timepicker",
    "UsersSelect",
]


class ActionableComponent(Component):
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
    def _validate_values(cls, values):
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


class Image(Component):
    type: str = "image"
    image_url: HttpUrl
    alt_text: str

    def __init__(self, *, image_url: HttpUrl, alt_text: str):
        super().__init__(image_url=image_url, alt_text=alt_text)

    _validate_alt_text = validator("alt_text", validate_string_length, max_len=2000)


class Select(ActionableComponent):
    placeholder: PlainText
    confirm: Optional[Confirm] = None

    _validate_placeholder = validator("placeholder", validate_text_length, max_len=150)


class StaticSelectBase(Select):
    options: Optional[List[Option]] = None
    option_groups: Optional[List[OptionGroup]] = None

    _validate_options = validator("options", validate_list_size, min_len=1, max_len=100)
    _validate_option_groups = validator(
        "option_groups", validate_list_size, min_len=1, max_len=100
    )


class StaticSelect(StaticSelectBase):
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


class MultiStaticSelect(StaticSelectBase):
    type: str = "multi_static_select"
    initial_options: Optional[List[Option]] = None
    max_selected_items: Optional[int] = None

    def __init__(
        self,
        *,
        placeholder: PlainText,
        action_id: Optional[str] = None,
        options: Optional[List[Option]] = None,
        option_groups: Optional[List[OptionGroup]] = None,
        initial_options: Optional[Option] = None,
        confirm: Optional[Confirm] = None,
        max_selected_items: Optional[int] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            options=options,
            option_groups=option_groups,
            initial_options=initial_options,
            confirm=confirm,
            max_selected_items=max_selected_items,
        )

    @root_validator
    def _validate_values(cls, values):
        initial_options = values.get("initial_options")
        options = values.get("options")
        option_groups = values.get("option_groups")

        if not any((options, option_groups)) or options and option_groups:
            raise ValueError("You must provide either options or option_groups")

        if None not in (initial_options, options):
            for initial_option in initial_options:
                if initial_option not in options:
                    raise ValueError(f"Option {initial_option} isn't within {options}")

        if None not in (initial_options, option_groups):
            groups_options = itertools.chain(*[og.options for og in option_groups])
            for initial_option in initial_options:
                if initial_option not in groups_options:
                    raise ValueError(
                        f"Option {initial_option} isn't within {option_groups}"
                    )

        return values

    _validate_max_selected_items = validator(
        "max_selected_items", validate_int_range, min_value=1, max_value=999
    )


class ExternalSelectBase(Select):
    min_query_length: Optional[int] = None

    _validate_min_query_length = validator(
        "min_query_length", validate_int_range, min_value=0, max_value=999
    )


class ExternalSelect(ExternalSelectBase):
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


class MultiExternalSelect(ExternalSelectBase):
    type: str = "multi_external_select"
    initial_options: Optional[List[Option]] = None
    max_selected_items: Optional[int] = None

    def __init__(
        self,
        *,
        placeholder: PlainText,
        action_id: Optional[str] = None,
        min_query_length: Optional[int] = None,
        initial_options: Optional[List[Option]] = None,
        confirm: Optional[Confirm] = None,
        max_selected_items: Optional[int] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            min_query_length=min_query_length,
            initial_options=initial_options,
            confirm=confirm,
            max_selected_items=max_selected_items,
        )

    _validate_max_selected_items = validator(
        "max_selected_items", validate_int_range, min_value=1, max_value=999
    )


class UsersSelect(Select):
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


class MultiUsersSelect(Select):
    type: str = "multi_users_select"
    initial_users: Optional[List[str]] = None
    max_selected_items: Optional[int] = None

    def __init__(
        self,
        *,
        placeholder: PlainText,
        action_id: Optional[str] = None,
        initial_users: Optional[str] = None,
        confirm: Optional[Confirm] = None,
        max_selected_items: Optional[int] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_users=initial_users,
            confirm=confirm,
            max_selected_items=max_selected_items,
        )

    _validate_max_selected_items = validator(
        "max_selected_items", validate_int_range, min_value=1, max_value=999
    )


class ConversationsSelect(Select):
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


class MultiConversationsSelect(Select):
    type: str = "multi_conversations_select"
    initial_conversations: Optional[List[str]] = None
    default_to_current_conversation: Optional[bool] = None
    max_selected_items: Optional[int] = None
    filter: Optional[Filter] = None

    def __init__(
        self,
        *,
        placeholder: PlainText,
        action_id: Optional[str] = None,
        initial_conversations: Optional[List[str]] = None,
        default_to_current_conversation: Optional[bool] = None,
        confirm: Optional[Confirm] = None,
        max_selected_items: Optional[int] = None,
        filter: Optional[Filter] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_conversations=initial_conversations,
            default_to_current_conversation=default_to_current_conversation,
            confirm=confirm,
            max_selected_items=max_selected_items,
            filter=filter,
        )

    _validate_max_selected_items = validator(
        "max_selected_items", validate_int_range, min_value=1, max_value=999
    )


class ChannelsSelect(Select):
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


class MultiChannelsSelect(Select):
    type: str = "multi_channels_select"
    initial_channels: Optional[List[str]] = None
    max_selected_items: Optional[int] = None

    def __init__(
        self,
        *,
        placeholder: PlainText,
        action_id: Optional[str] = None,
        initial_channels: Optional[str] = None,
        confirm: Optional[Confirm] = None,
        max_selected_items: Optional[int] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_channels=initial_channels,
            confirm=confirm,
            max_selected_items=max_selected_items,
        )

    _validate_max_selected_items = validator(
        "max_selected_items", validate_int_range, min_value=1, max_value=999
    )


class Overflow(ActionableComponent):
    type: str = "overflow"
    options: List[Option]
    confirm: Optional[Confirm] = None

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        options: List[Option],
        confirm: Optional[Confirm] = None,
    ):
        super().__init__(action_id=action_id, options=options, confirm=confirm)

    _validate_options = validator("options", validate_list_size, min_len=2, max_len=5)


class PlainTextInput(ActionableComponent):
    type: str = "plain_text_input"
    placeholder: Optional[PlainText] = None
    initial_value: Optional[str] = None
    multiline: Optional[bool] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    dispatch_action_config: Optional[DispatchActionConfig] = None

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        placeholder: Optional[PlainText] = None,
        initial_value: Optional[str] = None,
        multiline: Optional[bool] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        dispatch_action_config: Optional[DispatchActionConfig] = None,
    ):
        super().__init__(
            action_id=action_id,
            placeholder=placeholder,
            initial_value=initial_value,
            multiline=multiline,
            min_length=min_length,
            max_length=max_length,
            dispatch_action_config=dispatch_action_config,
        )

    _validate_placeholder = validator("placeholder", validate_text_length, max_len=150)
    _validate_min_length = validator(
        "min_length", validate_int_range, min_value=0, max_value=3000
    )
    _validate_max_length = validator(
        "max_length", validate_int_range, min_value=0, max_value=3000
    )


class RadioButtons(ActionableComponent):
    type: str = "radio_buttons"
    options: List[Option]
    initial_option: Optional[Option] = None
    confirm: Optional[Confirm] = None

    def __init__(
        self,
        *,
        options: List[Option],
        action_id: Optional[str] = None,
        initial_option: Optional[Option] = None,
        confirm: Optional[Confirm] = None,
    ):
        super().__init__(
            options=options,
            action_id=action_id,
            initial_option=initial_option,
            confirm=confirm,
        )

    _validate_options = validator("options", validate_list_size, min_len=1, max_len=10)

    @root_validator
    def _validate_values(cls, values):
        initial_option = values.get("initial_option")
        options = values.get("options")

        if initial_option is not None and initial_option not in options:
            raise ValueError(f"Option {initial_option} isn't within {options}")
        return values


class Timepicker(ActionableComponent):
    type: str = "timepicker"
    placeholder: Optional[PlainText] = None
    initial_time: Optional[time] = None
    confirm: Optional[Confirm] = None

    _validate_placeholder = validator("placeholder", validate_text_length, max_len=150)
    _validate_initial_time = validator("initial_time", validate_time)

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        placeholder: Optional[PlainText] = None,
        initial_time: Optional[time] = None,
        confirm: Optional[Confirm] = None,
    ):
        super().__init__(
            action_id=action_id,
            placeholder=placeholder,
            initial_time=initial_time,
            confirm=confirm,
        )
