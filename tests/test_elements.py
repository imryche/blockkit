import pytest
from blockkit import (
    Button,
    ChannelsSelect,
    Checkboxes,
    ConversationsSelect,
    DatePicker,
    ExternalSelect,
    Image,
    MultiChannelsSelect,
    MultiConversationsSelect,
    MultiExternalSelect,
    MultiStaticSelect,
    MultiUsersSelect,
    Overflow,
    PlainTextInput,
    RadioButtons,
    StaticSelect,
    UsersSelect,
)
from blockkit.objects import (
    Confirm,
    Filter,
    MarkdownText,
    Option,
    OptionGroup,
    PlainText,
)
from pydantic import ValidationError


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
        "url": "https://example.com",
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


def test_button_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        Button(text=PlainText(text="text"), action_id="a" * 256)


def test_button_excessive_url_raises_exception():
    with pytest.raises(ValidationError):
        url = "https://example.com/"
        Button(
            text=PlainText(text="text"),
            url=url + "u" * (3001 - len(url)),
        )


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
            Option(text=PlainText(text="option 1"), value="value_1"),
            Option(text=PlainText(text="option 2"), value="value_2"),
        ],
        initial_options=[Option(text=PlainText(text="option 1"), value="value_1")],
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
    ).build() == {
        "type": "checkboxes",
        "action_id": "action_id",
        "options": [
            {"text": {"type": "plain_text", "text": "option 1"}, "value": "value_1"},
            {"text": {"type": "plain_text", "text": "option 2"}, "value": "value_2"},
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
    }


def test_checkboxes_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        Checkboxes(
            options=[Option(text=PlainText(text="option 1"), value="value_1")],
            action_id="a" * 256,
        )


def test_checkboxes_empty_options_raise_exception():
    with pytest.raises(ValidationError):
        Checkboxes(options=[])


def test_checkboxes_excessive_options_raise_exception():
    with pytest.raises(ValidationError):
        Checkboxes(
            options=[
                Option(text=PlainText(text=f"option {o}"), value=f"value_{o}")
                for o in range(11)
            ]
        )


def test_checkboxes_empty_initial_options_raise_exception():
    with pytest.raises(ValidationError):
        Checkboxes(
            options=[Option(text=PlainText(text="option 1"), value="value_1")],
            initial_options=[],
        )


def test_checkboxes_initial_options_arent_within_options_raise_exception():
    with pytest.raises(ValidationError):
        Checkboxes(
            options=[Option(text=PlainText(text=f"option 1"), value=f"value_1")],
            initial_options=[
                Option(text=PlainText(text=f"option 2"), value=f"value_2")
            ],
        )


def test_builds_datepicker():
    assert DatePicker(
        action_id="action_id",
        placeholder=PlainText(text="placeholder"),
        initial_date="2021-09-14",
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
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
    }


def test_datepicker_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        DatePicker(action_id="a" * 256)


def test_datepicker_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        DatePicker(placeholder=PlainText(text="p" * 151))


def test_datepicker_invalid_initial_date_raises_exception():
    with pytest.raises(ValidationError):
        DatePicker(initial_date="YEAR-MON-DAY")


def test_builds_image():
    assert Image(
        image_url="http://placekitten.com/100/100", alt_text="kitten"
    ).build() == {
        "type": "image",
        "image_url": "http://placekitten.com/100/100",
        "alt_text": "kitten",
    }


def test_builds_static_select_with_options():
    assert StaticSelect(
        placeholder=PlainText(text="placeholder"),
        action_id="action_id",
        options=[
            Option(text=PlainText(text="option 1"), value="value_1"),
            Option(text=PlainText(text="option 2"), value="value_2"),
        ],
        initial_option=Option(text=PlainText(text="option 1"), value="value_1"),
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
    ).build() == {
        "type": "static_select",
        "placeholder": {"type": "plain_text", "text": "placeholder"},
        "action_id": "action_id",
        "options": [
            {"text": {"type": "plain_text", "text": "option 1"}, "value": "value_1"},
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
    }


def test_builds_static_select_with_option_groups():
    assert StaticSelect(
        placeholder=PlainText(text="placeholder"),
        action_id="action_id",
        option_groups=[
            OptionGroup(
                label=PlainText(text="group 1"),
                options=[Option(text=PlainText(text="option 1"), value="value_1")],
            ),
            OptionGroup(
                label=PlainText(text="group 2"),
                options=[Option(text=PlainText(text="option 2"), value="value_2")],
            ),
        ],
        initial_option=Option(text=PlainText(text="option 1"), value="value_1"),
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
            {
                "label": {"type": "plain_text", "text": "group 2"},
                "options": [
                    {
                        "text": {"type": "plain_text", "text": "option 2"},
                        "value": "value_2",
                    }
                ],
            },
        ],
        "initial_option": {
            "text": {"type": "plain_text", "text": "option 1"},
            "value": "value_1",
        },
    }


def test_static_select_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        StaticSelect(
            placeholder=PlainText(text="p" * 151),
            options=[
                Option(text=PlainText(text="option 1"), value="value_1"),
            ],
        )


def test_static_select_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        StaticSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="a" * 256,
            options=[
                Option(text=PlainText(text="option 1"), value="value_1"),
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
                Option(text=PlainText(text=f"option {o}"), value=f"value_{o}")
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
                        Option(text=PlainText(text=f"option {o}"), value=f"value_{o}")
                    ],
                )
                for o in range(101)
            ],
        )


def test_static_select_initial_option_isnt_within_options():
    with pytest.raises(ValidationError):
        StaticSelect(
            placeholder=PlainText(text="placeholder"),
            options=[Option(text=PlainText(text=f"option 1"), value=f"value_1")],
            initial_option=Option(text=PlainText(text=f"option 2"), value=f"value_2"),
        )


def test_static_select_initial_option_isnt_within_option_groups():
    with pytest.raises(ValidationError):
        StaticSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="action_id",
            option_groups=[
                OptionGroup(
                    label=PlainText(text="group 1"),
                    options=[Option(text=PlainText(text="option 1"), value="value_1")],
                ),
            ],
            initial_option=Option(text=PlainText(text="option 2"), value="value_2"),
        )


def test_builds_external_select():
    assert ExternalSelect(
        placeholder=PlainText(text="placeholder"),
        action_id="action_id",
        initial_option=Option(text=PlainText(text="option 1"), value="value_1"),
        min_query_length=2,
        confirm=Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
        ),
    ).build() == {
        "type": "external_select",
        "placeholder": {"type": "plain_text", "text": "placeholder"},
        "action_id": "action_id",
        "initial_option": {
            "text": {"type": "plain_text", "text": "option 1"},
            "value": "value_1",
        },
        "min_query_length": 2,
        "confirm": {
            "title": {"type": "plain_text", "text": "title"},
            "text": {"type": "mrkdwn", "text": "text"},
            "confirm": {"type": "plain_text", "text": "confirm"},
            "deny": {"type": "plain_text", "text": "deny"},
        },
    }


def test_external_select_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        ExternalSelect(placeholder=PlainText(text="p" * 151))


def test_external_select_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        ExternalSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="a" * 256,
        )


def test_external_select_negative_min_query_length_raises_exception():
    with pytest.raises(ValidationError):
        ExternalSelect(placeholder=PlainText(text="placeholder"), min_query_length=-1)


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
    }


def test_users_select_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        UsersSelect(placeholder=PlainText(text="p" * 151))


def test_users_select_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        UsersSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="a" * 256,
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
    }


def test_conversations_select_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        ConversationsSelect(placeholder=PlainText(text="p" * 151))


def test_conversations_select_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        ConversationsSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="a" * 256,
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
    }


def test_channels_select_excessive_placeholder_raises_exception():
    with pytest.raises(ValidationError):
        ChannelsSelect(placeholder=PlainText(text="p" * 151))


def test_channels_select_excessive_action_id_raises_exception():
    with pytest.raises(ValidationError):
        ChannelsSelect(
            placeholder=PlainText(text="placeholder"),
            action_id="a" * 256,
        )


@pytest.mark.skip
@pytest.mark.parametrize(
    "required_option, field",
    [("option_group", "option_groups"), ("option", "options")],
    indirect=["required_option"],
)
def test_builds_static_multiselect(required_option, field, plain_text, values, confirm):
    multiselect = MultiStaticSelect(
        plain_text,
        values.action_id,
        confirm=confirm,
        max_selected_items=3,
        initial_options=[required_option],
        **{field: [required_option for _ in range(3)]},
    )

    assert multiselect.build() == {
        "type": "multi_static_select",
        "placeholder": plain_text.build(),
        "action_id": values.action_id,
        "confirm": confirm.build(),
        "max_selected_items": 3,
        "initial_options": [required_option.build()],
        field: [required_option.build() for _ in range(3)],
    }


@pytest.mark.skip
@pytest.mark.parametrize("select_class", [StaticSelect, MultiStaticSelect])
def test_static_multiselect_with_options_and_option_groups_raises_exception(
    select_class, plain_text, values, option, option_group, confirm
):
    with pytest.raises(ValidationError):
        select_class(
            plain_text,
            values.action_id,
            options=[option for _ in range(2)],
            option_groups=[option_group for _ in range(2)],
        )


@pytest.mark.skip
def test_builds_external_multiselect(option, plain_text, values, confirm):
    multiselect = MultiExternalSelect(
        plain_text,
        values.action_id,
        confirm=confirm,
        max_selected_items=3,
        initial_options=[option],
        min_query_length=2,
    )

    assert multiselect.build() == {
        "type": "multi_external_select",
        "placeholder": plain_text.build(),
        "action_id": values.action_id,
        "confirm": confirm.build(),
        "max_selected_items": 3,
        "initial_options": [option.build()],
        "min_query_length": 2,
    }


@pytest.mark.skip
def test_builds_users_multiselect(plain_text, values, confirm):
    initial_users = ["U123456", "U654321"]

    multiselect = MultiUsersSelect(
        plain_text,
        values.action_id,
        confirm=confirm,
        max_selected_items=3,
        initial_users=initial_users,
    )

    assert multiselect.build() == {
        "type": "multi_users_select",
        "placeholder": plain_text.build(),
        "action_id": values.action_id,
        "confirm": confirm.build(),
        "max_selected_items": 3,
        "initial_users": initial_users,
    }


@pytest.mark.skip
def test_builds_conversations_multiselect(plain_text, values, confirm, filter_object):
    initial_conversations = ["C123456", "C654321"]

    multiselect = MultiConversationsSelect(
        plain_text,
        values.action_id,
        confirm=confirm,
        max_selected_items=3,
        initial_conversations=initial_conversations,
        filter=filter_object,
    )

    assert multiselect.build() == {
        "type": "multi_conversations_select",
        "placeholder": plain_text.build(),
        "action_id": values.action_id,
        "confirm": confirm.build(),
        "max_selected_items": 3,
        "initial_conversations": initial_conversations,
        "filter": filter_object.build(),
    }


@pytest.mark.skip
def test_builds_channels_multiselect(plain_text, values, confirm):
    initial_channels = ["C123456", "C654321"]

    multiselect = MultiChannelsSelect(
        plain_text,
        values.action_id,
        confirm=confirm,
        max_selected_items=3,
        initial_channels=initial_channels,
    )

    assert multiselect.build() == {
        "type": "multi_channels_select",
        "placeholder": plain_text.build(),
        "action_id": values.action_id,
        "confirm": confirm.build(),
        "max_selected_items": 3,
        "initial_channels": initial_channels,
    }


@pytest.mark.skip
def test_builds_overflow(values, option, confirm):
    overflow = Overflow(
        values.action_id,
        [option for _ in range(2)],
        confirm=confirm,
    )

    assert overflow.build() == {
        "type": "overflow",
        "action_id": values.action_id,
        "options": [option.build() for _ in range(2)],
        "confirm": confirm.build(),
    }


@pytest.mark.skip
def test_builds_plain_input(values, plain_text, dispatch_action_config):
    min_length = 2
    max_length = 10
    multiline = False

    text_input = PlainTextInput(
        values.action_id,
        placeholder=plain_text,
        initial_value=values.value,
        multiline=multiline,
        min_length=min_length,
        max_length=max_length,
        dispatch_action_config=dispatch_action_config,
    )

    assert text_input.build() == {
        "type": "plain_text_input",
        "action_id": values.action_id,
        "placeholder": plain_text.build(),
        "initial_value": values.value,
        "multiline": multiline,
        "min_length": min_length,
        "max_length": max_length,
        "dispatch_action_config": dispatch_action_config.build(),
    }


@pytest.mark.skip
def test_builds_radio_buttons(values, option, confirm):
    radio_buttons = RadioButtons(
        values.action_id,
        [option for _ in range(3)],
        initial_option=option,
        confirm=confirm,
    )

    assert radio_buttons.build() == {
        "type": "radio_buttons",
        "action_id": values.action_id,
        "options": [option.build() for _ in range(3)],
        "initial_option": option.build(),
        "confirm": confirm.build(),
    }
