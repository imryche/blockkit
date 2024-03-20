from datetime import date, datetime, time

import pytest
from dateutil.tz import gettz
from pydantic import ValidationError

from blockkit.elements import (
    Button,
    ChannelsSelect,
    Checkboxes,
    ConversationsSelect,
    DatePicker,
    DatetimePicker,
    ExternalSelect,
    FileInput,
    Image,
    MultiChannelsSelect,
    MultiConversationsSelect,
    MultiExternalSelect,
    MultiStaticSelect,
    MultiUsersSelect,
    Overflow,
    PlainTextInput,
    RadioButtons,
    RichTextList,
    RichTextPreformatted,
    RichTextQuote,
    RichTextSection,
    StaticSelect,
    TimePicker,
    UsersSelect,
)
from blockkit.objects import (
    Confirm,
    DispatchActionConfig,
    Emoji,
    Filter,
    MarkdownOption,
    MarkdownText,
    OptionGroup,
    PlainOption,
    PlainText,
    Style,
    Text,
)


def test_builds_button():
    assert Button(
        text=PlainText(text="text"),
        action_id="action_id",
        url="https://example.com",
        value="value",
        style="primary",
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
    ).build() == {
        "type": "button",
        "text": {"type": "plain_text", "text": "text"},
        "action_id": "action_id",
        "url": "https://example.com/",
        "value": "value",
        "style": "primary",
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
    }


def test_button_excessive_text_raises_exception():
    with pytest.raises(ValidationError):
        Button(text=PlainText(text="t" * 76))


def test_button_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        Button(text=PlainText(text="text"), action_id="")


def test_button_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        Button(text=PlainText(text="text"), action_id="a" * 256)


def test_button_empty_url_raises_exception():
    with pytest.raises(ValidationError):
        Button(text=PlainText(text="text"), url="")


def test_button_excessive_url_raises_exception():
    with pytest.raises(ValidationError):
        url = "https://example.com/"
        Button(
            text=PlainText(text="text"),
            url=url + "u" * (3001 - len(url)),
        )


def test_button_empty_value_raises_exception():
    with pytest.raises(ValidationError):
        Button(text=PlainText(text="text"), value="")


def test_button_excessive_value_raises_exception():
    with pytest.raises(ValidationError):
        Button(text=PlainText(text="text"), value="v" * 2001)


def test_button_invalid_style_raises_exception():
    with pytest.raises(ValidationError):
        Button(text=PlainText(text="text"), style="secondary")


def test_builds_checkboxes():
    assert Checkboxes(
        action_id="action_id",
        options=[
            PlainOption(text=PlainText(text="option 1"), value="value_1"),
            MarkdownOption(text=MarkdownText(text="_option 2_"), value="value_2"),
        ],
        initial_options=[PlainOption(text=PlainText(text="option 1"), value="value_1")],
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
        focus_on_load=True,
    ).build() == {
        "type": "checkboxes",
        "action_id": "action_id",
        "options": [
            {"text": {"type": "plain_text", "text": "option 1"}, "value": "value_1"},
            {"text": {"type": "mrkdwn", "text": "_option 2_"}, "value": "value_2"},
        ],
        "initial_options": [
            {"text": {"type": "plain_text", "text": "option 1"}, "value": "value_1"},
        ],
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
        "focus_on_load": True,
    }


def test_checkboxes_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        Checkboxes(
            options=[PlainOption(text=PlainText(text="option 1"), value="value_1")],
            action_id="",
        )


def test_checkboxes_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        Checkboxes(
            options=[PlainOption(text=PlainText(text="option 1"), value="value_1")],
            action_id="a" * 256,
        )


def test_checkboxes_empty_options_raise_exception():
    with pytest.raises(ValidationError):
        Checkboxes(options=[])


def test_checkboxes_excessive_options_raise_exception():
    with pytest.raises(ValidationError):
        Checkboxes(
            options=[
                PlainOption(text=PlainText(text=f"option {o}"), value=f"value_{o}")
                for o in range(11)
            ]
        )


def test_checkboxes_empty_initial_options_raise_exception():
    with pytest.raises(ValidationError):
        Checkboxes(
            options=[PlainOption(text=PlainText(text="option 1"), value="value_1")],
            initial_options=[],
        )


def test_checkboxes_initial_options_arent_within_options_raise_exception():
    with pytest.raises(ValidationError):
        Checkboxes(
            options=[PlainOption(text=PlainText(text="option 1"), value="value_1")],
            initial_options=[
                PlainOption(text=PlainText(text="option 2"), value="value_2")
            ],
        )


def test_builds_datepicker():
    assert DatePicker(
        action_id="action_id",
        placeholder=PlainText(text="placeholder"),
        initial_date=date(2021, 9, 14),
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
        focus_on_load=True,
    ).build() == {
        "type": "datepicker",
        "action_id": "action_id",
        "placeholder": {"type": "plain_text", "text": "placeholder"},
        "initial_date": "2021-09-14",
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
        "focus_on_load": True,
    }


def test_datepicker_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        DatePicker(action_id="")


def test_datepicker_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        DatePicker(action_id="a" * 256)


def test_datepicker_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        DatePicker(placeholder=PlainText(text="p" * 151))


def test_datepicker_invalid_initial_date_raises_exception():
    with pytest.raises(ValidationError):
        DatePicker(initial_date="YEAR-MON-DAY")


def test_builds_datetimepicker():
    assert DatetimePicker(
        action_id="action_id",
        initial_date_time=datetime(
            year=2023,
            month=1,
            day=2,
            hour=3,
            minute=4,
            tzinfo=gettz("America/New_York"),
        ),
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
        focus_on_load=True,
    ).build() == {
        "type": "datetimepicker",
        "action_id": "action_id",
        "initial_date_time": 1672646640,
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
        "focus_on_load": True,
    }


def test_datetimepicker_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        DatetimePicker(action_id="")


def test_datetimepicker_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        DatetimePicker(action_id="a" * 256)


def test_datetimepicker_invalid_initial_datetime_raises_exception():
    with pytest.raises(ValidationError):
        DatetimePicker(initial_date_time=1672646640123)


def test_builds_image():
    assert Image(
        image_url="http://placekitten.com/100/100", alt_text="kitten"
    ).build() == {
        "type": "image",
        "image_url": "http://placekitten.com/100/100",
        "alt_text": "kitten",
    }


def test_image_empty_alt_text_raises_exception():
    with pytest.raises(ValidationError):
        Image(image_url="http://placekitten.com/100/100", alt_text="")


def test_image_excessive_alt_text_raises_exception():
    with pytest.raises(ValidationError):
        Image(image_url="http://placekitten.com/100/100", alt_text="k" * 2001)


def test_builds_static_select_with_options():
    assert StaticSelect(
        placeholder="placeholder",
        action_id="action_id",
        options=[
            PlainOption(text="option 1", value="value_1"),
            PlainOption(text=PlainText(text="option 2"), value="value_2"),
        ],
        initial_option=PlainOption(text=PlainText(text="option 1"), value="value_1"),
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
        focus_on_load=True,
    ).build() == {
        "type": "static_select",
        "placeholder": {"type": "plain_text", "text": "placeholder", "emoji": True},
        "action_id": "action_id",
        "options": [
            {
                "text": {"type": "plain_text", "text": "option 1", "emoji": True},
                "value": "value_1",
            },
            {"text": {"type": "plain_text", "text": "option 2"}, "value": "value_2"},
        ],
        "initial_option": {
            "text": {"type": "plain_text", "text": "option 1"},
            "value": "value_1",
        },
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
        "focus_on_load": True,
    }


def test_builds_static_select_with_option_groups():
    assert StaticSelect(
        placeholder=PlainText(text="placeholder"),
        action_id="action_id",
        option_groups=[
            OptionGroup(
                label=PlainText(text="group 1"),
                options=[PlainOption(text=PlainText(text="option 1"), value="value_1")],
            ),
        ],
        initial_option=PlainOption(text=PlainText(text="option 1"), value="value_1"),
        focus_on_load=True,
    ).build() == {
        "type": "static_select",
        "placeholder": {"type": "plain_text", "text": "placeholder"},
        "action_id": "action_id",
        "option_groups": [
            {
                "label": {"type": "plain_text", "text": "group 1"},
                "options": [
                    {
                        "text": {"type": "plain_text", "text": "option 1"},
                        "value": "value_1",
                    }
                ],
            },
        ],
        "initial_option": {
            "text": {"type": "plain_text", "text": "option 1"},
            "value": "value_1",
        },
        "focus_on_load": True,
    }


def test_static_select_without_options_and_option_groups_raises_exception():
    with pytest.raises(ValidationError):
        StaticSelect(placeholder=PlainText(text="placeholder"))


def test_static_select_with_options_and_option_groups_raises_exception():
    with pytest.raises(ValidationError):
        StaticSelect(
            placeholder=PlainText(text="placeholder"),
            options=[
                PlainOption(text=PlainText(text="option 1"), value="value_1"),
            ],
            option_groups=[
                OptionGroup(
                    label=PlainText(text="group 1"),
                    options=[
                        PlainOption(text=PlainText(text="option 1"), value="value_1")
                    ],
                ),
                OptionGroup(
                    label=PlainText(text="group 2"),
                    options=[
                        PlainOption(text=PlainText(text="option 2"), value="value_2")
                    ],
                ),
            ],
        )


def test_static_select_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        StaticSelect(
            placeholder=PlainText(text="p" * 151),
            options=[
                PlainOption(text=PlainText(text="option 1"), value="value_1"),
            ],
        )


def test_static_select_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        StaticSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="",
            options=[
                PlainOption(text=PlainText(text="option 1"), value="value_1"),
            ],
        )


def test_static_select_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        StaticSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="a" * 256,
            options=[
                PlainOption(text=PlainText(text="option 1"), value="value_1"),
            ],
        )


def test_static_select_empty_options_raise_exception():
    with pytest.raises(ValidationError):
        StaticSelect(placeholder=PlainText(text="placeholder"), options=[])


def test_static_select_excessive_options_raise_exception():
    with pytest.raises(ValidationError):
        StaticSelect(
            placeholder=PlainText(text="placeholder"),
            options=[
                PlainOption(text=PlainText(text=f"option {o}"), value=f"value_{o}")
                for o in range(101)
            ],
        )


def test_static_select_empty_option_groups_raise_exception():
    with pytest.raises(ValidationError):
        StaticSelect(placeholder=PlainText(text="placeholder"), option_groups=[])


def test_static_select_excessive_option_groups_raise_exception():
    with pytest.raises(ValidationError):
        StaticSelect(
            placeholder=PlainText(text="placeholder"),
            option_groups=[
                OptionGroup(
                    label=PlainText(text=f"group {o}"),
                    options=[
                        PlainOption(
                            text=PlainText(text=f"option {o}"), value=f"value_{o}"
                        )
                    ],
                )
                for o in range(101)
            ],
        )


def test_static_select_initial_option_isnt_within_options():
    with pytest.raises(ValidationError):
        StaticSelect(
            placeholder=PlainText(text="placeholder"),
            options=[PlainOption(text=PlainText(text="option 1"), value="value_1")],
            initial_option=PlainOption(
                text=PlainText(text="option 2"), value="value_2"
            ),
        )


def test_static_select_initial_option_isnt_within_option_groups():
    with pytest.raises(ValidationError):
        StaticSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="action_id",
            option_groups=[
                OptionGroup(
                    label=PlainText(text="group 1"),
                    options=[
                        PlainOption(text=PlainText(text="option 1"), value="value_1")
                    ],
                ),
            ],
            initial_option=PlainOption(
                text=PlainText(text="option 2"), value="value_2"
            ),
        )


def test_builds_multi_static_select_with_options():
    assert MultiStaticSelect(
        placeholder=PlainText(text="placeholder"),
        action_id="action_id",
        options=[
            PlainOption(text=PlainText(text="option 1"), value="value_1"),
            PlainOption(text=PlainText(text="option 2"), value="value_2"),
        ],
        initial_options=[PlainOption(text=PlainText(text="option 1"), value="value_1")],
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
        max_selected_items=5,
        focus_on_load=True,
    ).build() == {
        "type": "multi_static_select",
        "placeholder": {"type": "plain_text", "text": "placeholder"},
        "action_id": "action_id",
        "options": [
            {"text": {"type": "plain_text", "text": "option 1"}, "value": "value_1"},
            {"text": {"type": "plain_text", "text": "option 2"}, "value": "value_2"},
        ],
        "initial_options": [
            {
                "text": {"type": "plain_text", "text": "option 1"},
                "value": "value_1",
            }
        ],
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
        "max_selected_items": 5,
        "focus_on_load": True,
    }


def test_builds_multi_static_select_with_option_groups():
    assert MultiStaticSelect(
        placeholder=PlainText(text="placeholder"),
        action_id="action_id",
        option_groups=[
            OptionGroup(
                label=PlainText(text="group 1"),
                options=[PlainOption(text=PlainText(text="option 1"), value="value_1")],
            ),
        ],
        initial_options=[PlainOption(text=PlainText(text="option 1"), value="value_1")],
        focus_on_load=True,
    ).build() == {
        "type": "multi_static_select",
        "placeholder": {"type": "plain_text", "text": "placeholder"},
        "action_id": "action_id",
        "option_groups": [
            {
                "label": {"type": "plain_text", "text": "group 1"},
                "options": [
                    {
                        "text": {"type": "plain_text", "text": "option 1"},
                        "value": "value_1",
                    }
                ],
            }
        ],
        "initial_options": [
            {
                "text": {"type": "plain_text", "text": "option 1"},
                "value": "value_1",
            }
        ],
        "focus_on_load": True,
    }


def test_multi_static_select_without_options_and_option_groups_raises_exception():
    with pytest.raises(ValidationError):
        MultiStaticSelect(placeholder=PlainText(text="placeholder"))


def test_multi_static_select_with_options_and_option_groups_raises_exception():
    with pytest.raises(ValidationError):
        MultiStaticSelect(
            placeholder=PlainText(text="placeholder"),
            options=[
                PlainOption(text=PlainText(text="option 1"), value="value_1"),
            ],
            option_groups=[
                OptionGroup(
                    label=PlainText(text="group 1"),
                    options=[
                        PlainOption(text=PlainText(text="option 1"), value="value_1")
                    ],
                )
            ],
        )


def test_multi_static_select_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        MultiStaticSelect(
            placeholder=PlainText(text="p" * 151),
            options=[
                PlainOption(text=PlainText(text="option 1"), value="value_1"),
            ],
        )


def test_multi_static_select_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        MultiStaticSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="",
            options=[
                PlainOption(text=PlainText(text="option 1"), value="value_1"),
            ],
        )


def test_multi_static_select_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        MultiStaticSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="a" * 256,
            options=[
                PlainOption(text=PlainText(text="option 1"), value="value_1"),
            ],
        )


def test_multi_static_select_empty_options_raise_exception():
    with pytest.raises(ValidationError):
        MultiStaticSelect(placeholder=PlainText(text="placeholder"), options=[])


def test_multi_static_select_excessive_options_raise_exception():
    with pytest.raises(ValidationError):
        MultiStaticSelect(
            placeholder=PlainText(text="placeholder"),
            options=[
                PlainOption(text=PlainText(text=f"option {o}"), value=f"value_{o}")
                for o in range(101)
            ],
        )


def test_multi_static_select_empty_option_groups_raise_exception():
    with pytest.raises(ValidationError):
        MultiStaticSelect(placeholder=PlainText(text="placeholder"), option_groups=[])


def test_multi_static_select_excessive_option_groups_raise_exception():
    with pytest.raises(ValidationError):
        MultiStaticSelect(
            placeholder=PlainText(text="placeholder"),
            option_groups=[
                OptionGroup(
                    label=PlainText(text=f"group {o}"),
                    options=[
                        PlainOption(
                            text=PlainText(text=f"option {o}"), value=f"value_{o}"
                        )
                    ],
                )
                for o in range(101)
            ],
        )


def test_multi_static_select_initial_options_arent_within_options():
    with pytest.raises(ValidationError):
        MultiStaticSelect(
            placeholder=PlainText(text="placeholder"),
            options=[PlainOption(text=PlainText(text="option 1"), value="value_1")],
            initial_options=[
                PlainOption(text=PlainText(text="option 2"), value="value_2")
            ],
        )


def test_multi_static_select_initial_options_arent_within_option_groups():
    with pytest.raises(ValidationError):
        MultiStaticSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="action_id",
            option_groups=[
                OptionGroup(
                    label=PlainText(text="group 1"),
                    options=[
                        PlainOption(text=PlainText(text="option 1"), value="value_1")
                    ],
                ),
            ],
            initial_options=[
                PlainOption(text=PlainText(text="option 2"), value="value_2")
            ],
        )


def test_multi_static_select_zero_max_selected_items_raises_exception():
    with pytest.raises(ValidationError):
        MultiStaticSelect(
            placeholder=PlainText(text="placeholder"),
            options=[PlainOption(text=PlainText(text="option 1"), value="value_1")],
            max_selected_items=0,
        )


def test_builds_external_select():
    assert ExternalSelect(
        placeholder=PlainText(text="placeholder"),
        action_id="action_id",
        min_query_length=2,
        initial_option=PlainOption(text=PlainText(text="option 1"), value="value_1"),
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
        focus_on_load=True,
    ).build() == {
        "type": "external_select",
        "placeholder": {"type": "plain_text", "text": "placeholder"},
        "action_id": "action_id",
        "min_query_length": 2,
        "initial_option": {
            "text": {"type": "plain_text", "text": "option 1"},
            "value": "value_1",
        },
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
        "focus_on_load": True,
    }


def test_external_select_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        ExternalSelect(placeholder=PlainText(text="p" * 151))


def test_external_select_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        ExternalSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="",
        )


def test_external_select_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        ExternalSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="a" * 256,
        )


def test_external_select_negative_min_query_length_raises_exception():
    with pytest.raises(ValidationError):
        ExternalSelect(placeholder=PlainText(text="placeholder"), min_query_length=-1)


def test_builds_multi_external_select():
    assert MultiExternalSelect(
        placeholder=PlainText(text="placeholder"),
        action_id="action_id",
        min_query_length=2,
        initial_options=[PlainOption(text=PlainText(text="option 1"), value="value_1")],
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
        max_selected_items=5,
        focus_on_load=True,
    ).build() == {
        "type": "multi_external_select",
        "placeholder": {"type": "plain_text", "text": "placeholder"},
        "action_id": "action_id",
        "min_query_length": 2,
        "initial_options": [
            {
                "text": {"type": "plain_text", "text": "option 1"},
                "value": "value_1",
            }
        ],
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
        "max_selected_items": 5,
        "focus_on_load": True,
    }


def test_multi_external_select_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        MultiExternalSelect(placeholder=PlainText(text="p" * 151))


def test_multi_external_select_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        MultiExternalSelect(placeholder=PlainText(text="placeholder"), action_id="")


def test_multi_external_select_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        MultiExternalSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="a" * 256,
        )


def test_multi_external_select_negative_min_query_length_raises_exception():
    with pytest.raises(ValidationError):
        MultiExternalSelect(
            placeholder=PlainText(text="placeholder"), min_query_length=-1
        )


def test_multi_external_select_zero_max_selected_items_raises_exception():
    with pytest.raises(ValidationError):
        MultiExternalSelect(
            placeholder=PlainText(text="placeholder"), max_selected_items=0
        )


def test_builds_users_select():
    assert UsersSelect(
        placeholder=PlainText(text="placeholder"),
        action_id="action_id",
        initial_user="U01P9A6F9HC",
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
        focus_on_load=True,
    ).build() == {
        "type": "users_select",
        "placeholder": {"type": "plain_text", "text": "placeholder"},
        "action_id": "action_id",
        "initial_user": "U01P9A6F9HC",
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
        "focus_on_load": True,
    }


def test_users_select_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        UsersSelect(placeholder=PlainText(text="p" * 151))


def test_users_select_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        UsersSelect(placeholder=PlainText(text="placeholder"), action_id="")


def test_users_select_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        UsersSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="a" * 256,
        )


def test_users_select_empty_initial_user_raises_exception():
    with pytest.raises(ValidationError):
        UsersSelect(placeholder=PlainText(text="placeholder"), initial_user="")


def test_builds_multi_users_select():
    assert MultiUsersSelect(
        placeholder=PlainText(text="placeholder"),
        action_id="action_id",
        initial_users=["U01P9A6F9HC", "U02P8A6F9HD"],
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
        max_selected_items=5,
        focus_on_load=True,
    ).build() == {
        "type": "multi_users_select",
        "placeholder": {"type": "plain_text", "text": "placeholder"},
        "action_id": "action_id",
        "initial_users": ["U01P9A6F9HC", "U02P8A6F9HD"],
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
        "max_selected_items": 5,
        "focus_on_load": True,
    }


def test_multi_users_select_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        MultiUsersSelect(placeholder=PlainText(text="p" * 151))


def test_multi_users_select_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        MultiUsersSelect(placeholder=PlainText(text="placeholder"), action_id="")


def test_multi_users_select_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        MultiUsersSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="a" * 256,
        )


def test_multi_users_select_zero_max_selected_items_raises_exception():
    with pytest.raises(ValidationError):
        MultiUsersSelect(
            placeholder=PlainText(text="placeholder"), max_selected_items=0
        )


def test_builds_conversations_select():
    assert ConversationsSelect(
        placeholder=PlainText(text="placeholder"),
        action_id="action_id",
        initial_conversation="U01P9A6F9HC",
        default_to_current_conversation=True,
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
        response_url_enabled=True,
        filter=Filter(include=["public"]),
        focus_on_load=True,
    ).build() == {
        "type": "conversations_select",
        "placeholder": {"type": "plain_text", "text": "placeholder"},
        "action_id": "action_id",
        "initial_conversation": "U01P9A6F9HC",
        "default_to_current_conversation": True,
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
        "response_url_enabled": True,
        "filter": {"include": ["public"]},
        "focus_on_load": True,
    }


def test_conversations_select_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        ConversationsSelect(placeholder=PlainText(text="p" * 151))


def test_conversations_select_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        ConversationsSelect(placeholder=PlainText(text="placeholder"), action_id="")


def test_conversations_select_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        ConversationsSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="a" * 256,
        )


def test_conversations_select_empty_initial_conversation_raises_exception():
    with pytest.raises(ValidationError):
        ConversationsSelect(
            placeholder=PlainText(text="placeholder"), initial_conversation=""
        )


def test_builds_multi_conversations_select():
    assert MultiConversationsSelect(
        placeholder=PlainText(text="placeholder"),
        action_id="action_id",
        initial_conversations=["U01P9A6F9HC", "U02P8A6F9HD"],
        default_to_current_conversation=True,
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
        max_selected_items=5,
        filter=Filter(include=["public"]),
        focus_on_load=True,
    ).build() == {
        "type": "multi_conversations_select",
        "placeholder": {"type": "plain_text", "text": "placeholder"},
        "action_id": "action_id",
        "initial_conversations": ["U01P9A6F9HC", "U02P8A6F9HD"],
        "default_to_current_conversation": True,
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
        "max_selected_items": 5,
        "filter": {"include": ["public"]},
        "focus_on_load": True,
    }


def test_multi_conversations_select_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        MultiConversationsSelect(placeholder=PlainText(text="p" * 151))


def test_multi_conversations_select_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        MultiConversationsSelect(
            placeholder=PlainText(text="placeholder"), action_id=""
        )


def test_multi_conversations_select_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        MultiConversationsSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="a" * 256,
        )


def test_multi_conversations_select_zero_max_selected_items_raises_exception():
    with pytest.raises(ValidationError):
        MultiConversationsSelect(
            placeholder=PlainText(text="placeholder"), max_selected_items=0
        )


def test_builds_channels_select():
    assert ChannelsSelect(
        placeholder=PlainText(text="placeholder"),
        action_id="action_id",
        initial_channel="CSK3A8P2M",
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
        response_url_enabled=True,
        focus_on_load=True,
    ).build() == {
        "type": "channels_select",
        "placeholder": {"type": "plain_text", "text": "placeholder"},
        "action_id": "action_id",
        "initial_channel": "CSK3A8P2M",
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
        "response_url_enabled": True,
        "focus_on_load": True,
    }


def test_channels_select_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        ChannelsSelect(placeholder=PlainText(text="p" * 151))


def test_channels_select_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        ChannelsSelect(placeholder=PlainText(text="placeholder"), action_id="")


def test_channels_select_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        ChannelsSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="a" * 256,
        )


def test_channels_select_empty_initial_channel_raises_exception():
    with pytest.raises(ValidationError):
        ChannelsSelect(placeholder=PlainText(text="placeholder"), initial_channel="")


def test_builds_multi_channels_select():
    assert MultiChannelsSelect(
        placeholder=PlainText(text="placeholder"),
        action_id="action_id",
        initial_channels=["CSK3A8P2M", "CSM4A0P2M"],
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
        max_selected_items=5,
        focus_on_load=True,
    ).build() == {
        "type": "multi_channels_select",
        "placeholder": {"type": "plain_text", "text": "placeholder"},
        "action_id": "action_id",
        "initial_channels": ["CSK3A8P2M", "CSM4A0P2M"],
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
        "max_selected_items": 5,
        "focus_on_load": True,
    }


def test_multi_channels_select_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        MultiChannelsSelect(placeholder=PlainText(text="p" * 151))


def test_multi_channels_select_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        MultiChannelsSelect(placeholder=PlainText(text="placeholder"), action_id="")


def test_multi_channels_select_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        MultiChannelsSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="a" * 256,
        )


def test_multi_channels_select_zero_max_selected_items_raises_exception():
    with pytest.raises(ValidationError):
        MultiChannelsSelect(
            placeholder=PlainText(text="placeholder"), max_selected_items=0
        )


def test_builds_overflow():
    assert Overflow(
        action_id="action_id",
        options=[
            PlainOption(text=PlainText(text="option 1"), value="value_1"),
            PlainOption(text=PlainText(text="option 2"), value="value_2"),
        ],
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
    ).build() == {
        "type": "overflow",
        "action_id": "action_id",
        "options": [
            {"text": {"type": "plain_text", "text": "option 1"}, "value": "value_1"},
            {"text": {"type": "plain_text", "text": "option 2"}, "value": "value_2"},
        ],
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
    }


def test_overflow_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        Overflow(
            action_id="",
            options=[
                PlainOption(text=PlainText(text="option 1"), value="value_1"),
            ],
        )


def test_overflow_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        Overflow(
            action_id="a" * 256,
            options=[
                PlainOption(text=PlainText(text="option 1"), value="value_1"),
            ],
        )


def test_overflow_empty_options_raise_exception():
    with pytest.raises(ValidationError):
        Overflow(options=[])


def test_overflow_excessive_options_raise_exception():
    with pytest.raises(ValidationError):
        Overflow(
            options=[
                PlainOption(text=PlainText(text=f"option {o}"), value=f"value_{o}")
                for o in range(6)
            ]
        )


def test_builds_plain_text_input():
    assert PlainTextInput(
        action_id="action_id",
        placeholder=PlainText(text="placeholder"),
        initial_value="initial value",
        multiline=True,
        min_length=5,
        max_length=500,
        dispatch_action_config=DispatchActionConfig(
            trigger_actions_on=["on_character_entered"]
        ),
        focus_on_load=True,
    ).build() == {
        "type": "plain_text_input",
        "action_id": "action_id",
        "placeholder": {"type": "plain_text", "text": "placeholder"},
        "initial_value": "initial value",
        "multiline": True,
        "min_length": 5,
        "max_length": 500,
        "dispatch_action_config": {"trigger_actions_on": ["on_character_entered"]},
        "focus_on_load": True,
    }


def test_plain_text_input_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        PlainTextInput(action_id="")


def test_plain_text_input_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        PlainTextInput(action_id="a" * 256)


def test_plain_text_input_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        PlainTextInput(placeholder=PlainText(text="p" * 151))


def test_plain_text_input_empty_initial_value_raises_exception():
    with pytest.raises(ValidationError):
        PlainTextInput(initial_value="")


def test_plain_text_input_negative_min_length_raises_exception():
    with pytest.raises(ValidationError):
        PlainTextInput(min_length=-1)


def test_plain_text_input_excessive_min_length_raises_exception():
    with pytest.raises(ValidationError):
        PlainTextInput(min_length=3001)


def test_plain_text_input_negative_max_length_raises_exception():
    with pytest.raises(ValidationError):
        PlainTextInput(max_length=-1)


def test_plain_text_input_excessive_max_length_raises_exception():
    with pytest.raises(ValidationError):
        PlainTextInput(max_length=3001)


def test_builds_radio_buttons():
    assert RadioButtons(
        action_id="action_id",
        options=[
            PlainOption(text=PlainText(text="option 1"), value="value_1"),
            MarkdownOption(text=MarkdownText(text="_option 2_"), value="value_2"),
        ],
        initial_option=PlainOption(text=PlainText(text="option 1"), value="value_1"),
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
        focus_on_load=True,
    ).build() == {
        "type": "radio_buttons",
        "action_id": "action_id",
        "options": [
            {"text": {"type": "plain_text", "text": "option 1"}, "value": "value_1"},
            {"text": {"type": "mrkdwn", "text": "_option 2_"}, "value": "value_2"},
        ],
        "initial_option": {
            "text": {"type": "plain_text", "text": "option 1"},
            "value": "value_1",
        },
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
        "focus_on_load": True,
    }


def test_radio_buttons_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        RadioButtons(
            options=[PlainOption(text=PlainText(text="option 1"), value="value_1")],
            action_id="",
        )


def test_radio_buttons_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        RadioButtons(
            options=[PlainOption(text=PlainText(text="option 1"), value="value_1")],
            action_id="a" * 256,
        )


def test_radio_buttons_empty_options_raise_exception():
    with pytest.raises(ValidationError):
        RadioButtons(options=[])


def test_radio_buttons_excessive_options_raise_exception():
    with pytest.raises(ValidationError):
        RadioButtons(
            options=[
                PlainOption(text=PlainText(text=f"option {o}"), value=f"value_{o}")
                for o in range(11)
            ]
        )


def test_radio_buttons_initial_options_arent_within_options_raise_exception():
    with pytest.raises(ValidationError):
        RadioButtons(
            options=[PlainOption(text=PlainText(text="option 1"), value="value_1")],
            initial_option=PlainOption(
                text=PlainText(text="option 2"), value="value_2"
            ),
        )


def test_builds_rich_text_preformatted():
    assert RichTextPreformatted(
        elements=[
            Text(text="Well "),
            Text(text="done ", style=Style(bold=True)),
            Text(text="is better than well "),
            Text(text="said.", style=Style(bold=True, strike=True)),
            Emoji(name="wink"),
        ]
    ).build() == {
        "type": "rich_text_preformatted",
        "elements": [
            {"type": "text", "text": "Well "},
            {"type": "text", "text": "done ", "style": {"bold": True}},
            {"type": "text", "text": "is better than well "},
            {"type": "text", "text": "said.", "style": {"bold": True, "strike": True}},
            {"type": "emoji", "name": "wink"},
        ],
    }


def test_empty_rich_text_preformatted_raises_exception():
    with pytest.raises(ValidationError):
        RichTextPreformatted(elements=[])


def test_builds_rich_text_quote():
    assert RichTextQuote(
        elements=[
            Text(text="Well "),
            Text(text="done ", style=Style(bold=True)),
            Text(text="is better than well "),
            Text(text="said.", style=Style(bold=True, strike=True)),
            Emoji(name="wink"),
        ]
    ).build() == {
        "type": "rich_text_quote",
        "elements": [
            {"type": "text", "text": "Well "},
            {"type": "text", "text": "done ", "style": {"bold": True}},
            {"type": "text", "text": "is better than well "},
            {"type": "text", "text": "said.", "style": {"bold": True, "strike": True}},
            {"type": "emoji", "name": "wink"},
        ],
    }


def test_empty_rich_text_quote_raises_exception():
    with pytest.raises(ValidationError):
        RichTextQuote(elements=[])


def test_builds_rich_text_section():
    assert RichTextSection(
        elements=[
            Text(text="Well "),
            Text(text="done ", style=Style(bold=True)),
            Text(text="is better than well "),
            Text(text="said.", style=Style(bold=True, strike=True)),
            Emoji(name="wink"),
        ]
    ).build() == {
        "type": "rich_text_section",
        "elements": [
            {"type": "text", "text": "Well "},
            {"type": "text", "text": "done ", "style": {"bold": True}},
            {"type": "text", "text": "is better than well "},
            {"type": "text", "text": "said.", "style": {"bold": True, "strike": True}},
            {"type": "emoji", "name": "wink"},
        ],
    }


def test_empty_rich_text_section_raises_exception():
    with pytest.raises(ValidationError):
        RichTextSection(elements=[])


def test_builds_rich_text_list():
    assert RichTextList(
        style="ordered",
        indent=1,
        elements=[
            RichTextSection(elements=[Text(text="My first bullet point")]),
            RichTextSection(elements=[Text(text="My second bullet point")]),
        ],
    ).build() == {
        "type": "rich_text_list",
        "style": "ordered",
        "indent": 1,
        "elements": [
            {
                "type": "rich_text_section",
                "elements": [{"type": "text", "text": "My first bullet point"}],
            },
            {
                "type": "rich_text_section",
                "elements": [{"type": "text", "text": "My second bullet point"}],
            },
        ],
    }


def test_empty_rich_text_list_raises_exception():
    with pytest.raises(ValidationError):
        RichTextList(elements=[])


@pytest.fixture(scope="module")
def minimal_rich_text_list_elements():
    return [RichTextSection(elements=[Text(text="a")])]


def test_invalid_rich_text_list_style_raises_exception(minimal_rich_text_list_elements):
    with pytest.raises(ValidationError):
        RichTextList(elements=minimal_rich_text_list_elements, style="invalid")


def test_invalid_rich_text_list_indent_raises_exception(
    minimal_rich_text_list_elements,
):
    with pytest.raises(ValidationError):
        RichTextList(elements=minimal_rich_text_list_elements, indent=-1)
    with pytest.raises(ValidationError):
        RichTextList(elements=minimal_rich_text_list_elements, indent=9)


def test_builds_timepicker():
    assert TimePicker(
        action_id="action_id",
        placeholder=PlainText(text="placeholder"),
        initial_time=time(hour=22, minute=55),
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
        focus_on_load=True,
    ).build() == {
        "type": "timepicker",
        "action_id": "action_id",
        "placeholder": {"type": "plain_text", "text": "placeholder"},
        "initial_time": "22:55",
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
        "focus_on_load": True,
    }


def test_timepicker_empty_action_id_raises_exception():
    with pytest.raises(ValidationError):
        TimePicker(action_id="")


def test_timepicker_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        TimePicker(action_id="a" * 256)


def test_timepicker_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        TimePicker(placeholder=PlainText(text="p" * 151))


def test_builds_fileinput():
    assert FileInput(
        action_id="action_id",
        filetypes=["file"],
        max_files=1,
    ).build() == {
        "type": "file_input",
        "action_id": "action_id",
        "filetypes": ["file"],
        "max_files": 1,
    }


def test_fileinput_excessive_max_files_raises_exception():
    with pytest.raises(ValidationError):
        FileInput(max_files=11)

