import itertools
from datetime import date, datetime, time
from typing import List, Optional, Union

from pydantic import AnyUrl, Field, model_validator
from pydantic.networks import HttpUrl

from blockkit.components import Component
from blockkit.enums import ListStyle, Style
from blockkit.objects import (
    Confirm,
    DispatchActionConfig,
    Emoji,
    Filter,
    MarkdownOption,
    OptionGroup,
    PlainOption,
    PlainText,
    Text,
)
from blockkit.validators import (
    validate_date,
    validate_datetime,
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
    "DatetimePicker",
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
    "TimePicker",
    "UsersSelect",
    "NumberInput",
    "RichTextPreformatted",
    "RichTextQuote",
    "RichTextSection",
    "RichTextList",
    "FileInput",
]


class ActionableComponent(Component):
    action_id: Optional[str] = Field(None, min_length=1, max_length=255)


class FocusableElement(ActionableComponent):
    focus_on_load: Optional[bool] = None


class Button(ActionableComponent):
    type: str = "button"
    text: Union[PlainText, str]
    url: Optional[AnyUrl] = Field(None, max_length=3000)
    value: Optional[str] = Field(None, min_length=1, max_length=2000)
    style: Optional[Style] = None
    confirm: Optional[Confirm] = None

    def __init__(
        self,
        *,
        text: Union[PlainText],
        action_id: Optional[str] = None,
        url: Optional[AnyUrl] = None,
        value: Optional[str] = None,
        style: Optional[Style] = None,
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

    _validate_text = validator("text", validate_text_length, max_length=75)


class Checkboxes(FocusableElement):
    type: str = "checkboxes"
    options: List[Union[MarkdownOption, PlainOption]] = Field(
        ..., min_length=1, max_length=10
    )
    initial_options: Optional[List[Union[MarkdownOption, PlainOption]]] = Field(
        None, min_length=1, max_length=10
    )
    confirm: Optional[Confirm] = None

    def __init__(
        self,
        *,
        options: List[Union[MarkdownOption, PlainOption]],
        action_id: Optional[str] = None,
        initial_options: Optional[List[Union[MarkdownOption, PlainOption]]] = None,
        confirm: Optional[Confirm] = None,
        focus_on_load: Optional[bool] = None,
    ):
        super().__init__(
            options=options,
            action_id=action_id,
            initial_options=initial_options,
            confirm=confirm,
            focus_on_load=focus_on_load,
        )

    @model_validator(mode="after")
    def _validate_values(self) -> "Checkboxes":
        if not self.initial_options:
            return self

        for initial_option in self.initial_options:
            if initial_option not in self.options:
                raise ValueError(f"Option {initial_option} isn't within {self.options}")
        return self


class DatePicker(FocusableElement):
    type: str = "datepicker"
    placeholder: Union[PlainText, str, None] = None
    initial_date: Optional[date] = None
    confirm: Optional[Confirm] = None

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        placeholder: Union[PlainText, str, None] = None,
        initial_date: Optional[date] = None,
        confirm: Optional[Confirm] = None,
        focus_on_load: Optional[bool] = None,
    ):
        super().__init__(
            action_id=action_id,
            placeholder=placeholder,
            initial_date=initial_date,
            confirm=confirm,
            focus_on_load=focus_on_load,
        )

    _validate_placeholder = validator(
        "placeholder", validate_text_length, max_length=150
    )
    _validate_initial_date = validator("initial_date", validate_date)


class DatetimePicker(FocusableElement):
    type: str = "datetimepicker"
    initial_date_time: Union[int, datetime, None] = None
    confirm: Optional[Confirm] = None

    _validate_initial_datetime = validator("initial_date_time", validate_datetime)

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        initial_date_time: Optional[Union[int, datetime]] = None,
        confirm: Optional[Confirm] = None,
        focus_on_load: Optional[bool] = None,
    ):
        super().__init__(
            action_id=action_id,
            initial_date_time=initial_date_time,
            confirm=confirm,
            focus_on_load=focus_on_load,
        )


class Image(Component):
    type: str = "image"
    image_url: HttpUrl
    alt_text: str = Field(..., min_length=1, max_length=2000)

    def __init__(self, *, image_url: HttpUrl, alt_text: str):
        super().__init__(image_url=image_url, alt_text=alt_text)


class Select(FocusableElement):
    placeholder: Union[PlainText, str]
    confirm: Optional[Confirm] = None

    _validate_placeholder = validator(
        "placeholder", validate_text_length, max_length=150
    )


class StaticSelectBase(Select):
    options: Optional[List[PlainOption]] = Field(None, min_length=1, max_length=100)
    option_groups: Optional[List[OptionGroup]] = Field(
        None, min_length=1, max_length=100
    )


class StaticSelect(StaticSelectBase):
    type: str = "static_select"
    initial_option: Optional[PlainOption] = None

    def __init__(
        self,
        *,
        placeholder: Union[PlainText, str],
        action_id: Optional[str] = None,
        options: Optional[List[PlainOption]] = None,
        option_groups: Optional[List[OptionGroup]] = None,
        initial_option: Optional[PlainOption] = None,
        confirm: Optional[Confirm] = None,
        focus_on_load: Optional[bool] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            options=options,
            option_groups=option_groups,
            initial_option=initial_option,
            confirm=confirm,
            focus_on_load=focus_on_load,
        )

    @model_validator(mode="after")
    def _validate_values(self) -> "StaticSelect":
        if bool(self.options) == bool(self.option_groups):
            raise ValueError("You must provide either options or option_groups.")

        if (
            self.initial_option
            and self.options
            and self.initial_option not in self.options
        ):
            raise ValueError(
                f"Option {self.initial_option} isn't within {self.options}"
            )

        if self.initial_option and self.option_groups:
            if self.initial_option not in itertools.chain(
                *[og.options for og in self.option_groups]
            ):
                raise ValueError(
                    f"Option {self.initial_option} isn't within {self.option_groups}"
                )
        return self


class MultiStaticSelect(StaticSelectBase):
    type: str = "multi_static_select"
    initial_options: Optional[List[PlainOption]] = None
    max_selected_items: Optional[int] = Field(..., gt=0)

    def __init__(
        self,
        *,
        placeholder: Union[PlainText, str],
        action_id: Optional[str] = None,
        options: Optional[List[PlainOption]] = None,
        option_groups: Optional[List[OptionGroup]] = None,
        initial_options: Optional[List[PlainOption]] = None,
        confirm: Optional[Confirm] = None,
        max_selected_items: Optional[int] = None,
        focus_on_load: Optional[bool] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            options=options,
            option_groups=option_groups,
            initial_options=initial_options,
            confirm=confirm,
            max_selected_items=max_selected_items,
            focus_on_load=focus_on_load,
        )

    @model_validator(mode="after")
    def _validate_values(self) -> "MultiStaticSelect":
        if bool(self.options) == bool(self.option_groups):
            raise ValueError("You must provide either options or option_groups.")

        if self.initial_options and self.options:
            for initial_option in self.initial_options:
                if initial_option not in self.options:
                    raise ValueError(
                        f"Option {initial_option} isn't within {self.options}"
                    )

        if self.initial_options and self.option_groups:
            groups_options = itertools.chain(*[og.options for og in self.option_groups])
            for initial_option in self.initial_options:
                if initial_option not in groups_options:
                    raise ValueError(
                        f"Option {initial_option} isn't within {self.option_groups}"
                    )
        return self


class ExternalSelectBase(Select):
    min_query_length: Optional[int] = Field(None, ge=0)


class ExternalSelect(ExternalSelectBase):
    type: str = "external_select"
    initial_option: Optional[PlainOption] = None

    def __init__(
        self,
        *,
        placeholder: Union[PlainText, str],
        action_id: Optional[str] = None,
        initial_option: Optional[PlainOption] = None,
        min_query_length: Optional[int] = None,
        confirm: Optional[Confirm] = None,
        focus_on_load: Optional[bool] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_option=initial_option,
            min_query_length=min_query_length,
            confirm=confirm,
            focus_on_load=focus_on_load,
        )


class MultiExternalSelect(ExternalSelectBase):
    type: str = "multi_external_select"
    initial_options: Optional[List[PlainOption]] = None
    max_selected_items: Optional[int] = Field(None, gt=0)

    def __init__(
        self,
        *,
        placeholder: Union[PlainText, str],
        action_id: Optional[str] = None,
        min_query_length: Optional[int] = None,
        initial_options: Optional[List[PlainOption]] = None,
        confirm: Optional[Confirm] = None,
        max_selected_items: Optional[int] = None,
        focus_on_load: Optional[bool] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            min_query_length=min_query_length,
            initial_options=initial_options,
            confirm=confirm,
            max_selected_items=max_selected_items,
            focus_on_load=focus_on_load,
        )


class UsersSelect(Select):
    type: str = "users_select"
    initial_user: Optional[str] = Field(None, min_length=1)

    def __init__(
        self,
        *,
        placeholder: Union[PlainText, str],
        action_id: Optional[str] = None,
        initial_user: Optional[str] = None,
        confirm: Optional[Confirm] = None,
        focus_on_load: Optional[bool] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_user=initial_user,
            confirm=confirm,
            focus_on_load=focus_on_load,
        )


class MultiUsersSelect(Select):
    type: str = "multi_users_select"
    initial_users: Optional[List[str]] = None
    max_selected_items: Optional[int] = Field(None, gt=0)

    def __init__(
        self,
        *,
        placeholder: Union[PlainText, str],
        action_id: Optional[str] = None,
        initial_users: Optional[str] = None,
        confirm: Optional[Confirm] = None,
        max_selected_items: Optional[int] = None,
        focus_on_load: Optional[bool] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_users=initial_users,
            confirm=confirm,
            max_selected_items=max_selected_items,
            focus_on_load=focus_on_load,
        )


class ConversationsSelect(Select):
    type: str = "conversations_select"
    initial_conversation: Optional[str] = Field(None, min_length=1)
    default_to_current_conversation: Optional[bool] = None
    response_url_enabled: Optional[bool] = None
    filter: Optional[Filter] = None

    def __init__(
        self,
        *,
        placeholder: Union[PlainText, str],
        action_id: Optional[str] = None,
        initial_conversation: Optional[str] = None,
        default_to_current_conversation: Optional[bool] = None,
        confirm: Optional[Confirm] = None,
        response_url_enabled: Optional[bool] = None,
        filter: Optional[Filter] = None,
        focus_on_load: Optional[bool] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_conversation=initial_conversation,
            default_to_current_conversation=default_to_current_conversation,
            confirm=confirm,
            response_url_enabled=response_url_enabled,
            filter=filter,
            focus_on_load=focus_on_load,
        )


class MultiConversationsSelect(Select):
    type: str = "multi_conversations_select"
    initial_conversations: Optional[List[str]] = None
    default_to_current_conversation: Optional[bool] = None
    max_selected_items: Optional[int] = Field(None, gt=0)
    filter: Optional[Filter] = None

    def __init__(
        self,
        *,
        placeholder: Union[PlainText, str],
        action_id: Optional[str] = None,
        initial_conversations: Optional[List[str]] = None,
        default_to_current_conversation: Optional[bool] = None,
        confirm: Optional[Confirm] = None,
        max_selected_items: Optional[int] = None,
        filter: Optional[Filter] = None,
        focus_on_load: Optional[bool] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_conversations=initial_conversations,
            default_to_current_conversation=default_to_current_conversation,
            confirm=confirm,
            max_selected_items=max_selected_items,
            filter=filter,
            focus_on_load=focus_on_load,
        )


class ChannelsSelect(Select):
    type: str = "channels_select"
    initial_channel: Optional[str] = Field(None, min_length=1)
    response_url_enabled: Optional[bool] = None

    def __init__(
        self,
        *,
        placeholder: Union[PlainText, str],
        action_id: Optional[str] = None,
        initial_channel: Optional[str] = None,
        confirm: Optional[Confirm] = None,
        response_url_enabled: Optional[bool] = None,
        focus_on_load: Optional[bool] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_channel=initial_channel,
            confirm=confirm,
            response_url_enabled=response_url_enabled,
            focus_on_load=focus_on_load,
        )


class MultiChannelsSelect(Select):
    type: str = "multi_channels_select"
    initial_channels: Optional[List[str]] = None
    max_selected_items: Optional[int] = Field(None, gt=0)

    def __init__(
        self,
        *,
        placeholder: Union[PlainText, str],
        action_id: Optional[str] = None,
        initial_channels: Optional[str] = None,
        confirm: Optional[Confirm] = None,
        max_selected_items: Optional[int] = None,
        focus_on_load: Optional[bool] = None,
    ):
        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            initial_channels=initial_channels,
            confirm=confirm,
            max_selected_items=max_selected_items,
            focus_on_load=focus_on_load,
        )


class Overflow(ActionableComponent):
    type: str = "overflow"
    options: List[PlainOption] = Field(..., min_length=1, max_length=5)
    confirm: Optional[Confirm] = None

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        options: List[PlainOption],
        confirm: Optional[Confirm] = None,
    ):
        super().__init__(action_id=action_id, options=options, confirm=confirm)


class PlainTextInput(FocusableElement):
    type: str = "plain_text_input"
    placeholder: Union[PlainText, str, None] = None
    initial_value: Optional[str] = Field(None, min_length=1)
    multiline: Optional[bool] = None
    min_length: Optional[int] = Field(None, ge=0, lt=3000)
    max_length: Optional[int] = Field(None, ge=0, lt=3000)
    dispatch_action_config: Optional[DispatchActionConfig] = None

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        placeholder: Union[PlainText, str, None] = None,
        initial_value: Optional[str] = None,
        multiline: Optional[bool] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        dispatch_action_config: Optional[DispatchActionConfig] = None,
        focus_on_load: Optional[bool] = None,
    ):
        super().__init__(
            action_id=action_id,
            placeholder=placeholder,
            initial_value=initial_value,
            multiline=multiline,
            min_length=min_length,
            max_length=max_length,
            dispatch_action_config=dispatch_action_config,
            focus_on_load=focus_on_load,
        )

    _validate_placeholder = validator(
        "placeholder", validate_text_length, max_length=150
    )


class RadioButtons(FocusableElement):
    type: str = "radio_buttons"
    options: List[Union[MarkdownOption, PlainOption]] = Field(
        ..., min_length=1, max_length=10
    )
    initial_option: Union[MarkdownOption, PlainOption, None] = None
    confirm: Optional[Confirm] = None

    def __init__(
        self,
        *,
        options: List[Union[MarkdownOption, PlainOption]],
        action_id: Optional[str] = None,
        initial_option: Union[MarkdownOption, PlainOption, None] = None,
        confirm: Optional[Confirm] = None,
        focus_on_load: Optional[bool] = None,
    ):
        super().__init__(
            options=options,
            action_id=action_id,
            initial_option=initial_option,
            confirm=confirm,
            focus_on_load=focus_on_load,
        )

    @model_validator(mode="after")
    def _validate_values(self) -> "RadioButtons":
        if (
            self.initial_option
            and self.options
            and self.initial_option not in self.options
        ):
            raise ValueError(
                f"Option {self.initial_option} isn't within {self.options}"
            )
        return self


class TimePicker(FocusableElement):
    type: str = "timepicker"
    placeholder: Union[PlainText, str, None] = None
    initial_time: Optional[time] = None
    confirm: Optional[Confirm] = None

    _validate_placeholder = validator(
        "placeholder", validate_text_length, max_length=150
    )
    _validate_initial_time = validator("initial_time", validate_time)

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        placeholder: Union[PlainText, str, None] = None,
        initial_time: Optional[time] = None,
        confirm: Optional[Confirm] = None,
        focus_on_load: Optional[bool] = None,
    ):
        super().__init__(
            action_id=action_id,
            placeholder=placeholder,
            initial_time=initial_time,
            confirm=confirm,
            focus_on_load=focus_on_load,
        )


class NumberInput(FocusableElement):
    type: str = "number_input"
    placeholder: Union[PlainText, str, None] = None
    initial_value: Optional[str] = Field(None, min_length=1)
    is_decimal_allowed: bool = True
    min_value: Optional[str] = Field(None)
    max_value: Optional[str] = Field(None)
    dispatch_action_config: Optional[DispatchActionConfig] = None

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        placeholder: Union[PlainText, str, None] = None,
        initial_value: Optional[str] = None,
        is_decimal_allowed: bool,
        min_value: Optional[str] = None,
        max_value: Optional[str] = None,
        dispatch_action_config: Optional[DispatchActionConfig] = None,
        focus_on_load: Optional[bool] = None,
    ):
        super().__init__(
            action_id=action_id,
            placeholder=placeholder,
            initial_value=initial_value,
            is_decimal_allowed=is_decimal_allowed,
            min_value=min_value,
            max_value=max_value,
            dispatch_action_config=dispatch_action_config,
            focus_on_load=focus_on_load,
        )

    _validate_placeholder = validator(
        "placeholder", validate_text_length, max_length=150
    )


RichTextObject = Union[Text, Emoji]


class RichTextPreformatted(Component):
    type: str = "rich_text_preformatted"
    elements: List[RichTextObject] = Field(..., min_length=1)

    def __init__(self, *, elements: List[RichTextObject]):
        super().__init__(elements=elements)


class RichTextQuote(Component):
    type: str = "rich_text_quote"
    elements: List[RichTextObject] = Field(..., min_length=1)

    def __init__(self, *, elements: List[RichTextObject]):
        super().__init__(elements=elements)


class RichTextSection(Component):
    type: str = "rich_text_section"
    elements: List[RichTextObject] = Field(..., min_length=1)

    def __init__(self, *, elements: List[RichTextObject]):
        super().__init__(elements=elements)


class RichTextList(Component):
    type: str = "rich_text_list"
    elements: List[RichTextSection] = Field(..., min_length=1)
    style: Optional[ListStyle] = None
    indent: Optional[int] = Field(..., ge=0, le=8)

    def __init__(
        self,
        *,
        elements: List[RichTextSection],
        style: Optional[ListStyle] = None,
        indent: Optional[int] = None,
    ):
        super().__init__(elements=elements, style=style, indent=indent)


class FileInput(ActionableComponent):
    type: str = "file_input"
    filetypes: Optional[List[str]] = Field(None)
    max_files: Optional[int] = Field(..., gt=0, le=10)

    def __init__(
        self,
        *,
        action_id: Optional[str] = None,
        filetypes: Optional[List[str]] = None,
        max_files: Optional[int] = None,
    ):
        super().__init__(
            action_id=action_id,
            filetypes=filetypes,
            max_files=max_files,
        )

