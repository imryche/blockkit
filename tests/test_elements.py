import pytest

from blockkit import (
    Button,
    DatePicker,
    Image,
    MultiExternalSelect,
    MultiStaticSelect,
    MultiUsersSelect,
    MultiConversationsSelect,
    MultiChannelsSelect,
    StaticSelect,
)
from blockkit.validators import ValidationError


def test_builds_button(values, plain_text, confirm):
    button = Button(
        plain_text, values.action_id, values.url, values.value, Button.primary, confirm
    )

    assert button.build() == {
        "type": "button",
        "text": plain_text.build(),
        "action_id": values.action_id,
        "url": values.url,
        "value": values.value,
        "style": Button.primary,
        "confirm": confirm.build(),
    }


def test_builds_datepicker(values, plain_text, confirm):
    datepicker = DatePicker(values.action_id, plain_text, values.date, confirm)

    assert datepicker.build() == {
        "type": "datepicker",
        "action_id": values.action_id,
        "placeholder": plain_text.build(),
        "initial_date": values.date,
        "confirm": confirm.build(),
    }


def test_builds_image(values):
    image = Image(values.image_url, values.alt_text)

    assert image.build() == {
        "type": "image",
        "image_url": values.image_url,
        "alt_text": values.alt_text,
    }


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
        **{field: [required_option for _ in range(3)]}
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


@pytest.mark.parametrize(
    "required_option, field",
    [("option_group", "option_groups"), ("option", "options")],
    indirect=["required_option"],
)
def test_builds_static_select(required_option, field, plain_text, values, confirm):
    select = StaticSelect(
        plain_text,
        values.action_id,
        confirm=confirm,
        initial_option=required_option,
        **{field: [required_option for _ in range(3)]}
    )

    assert select.build() == {
        "type": "static_select",
        "placeholder": plain_text.build(),
        "action_id": values.action_id,
        field: [required_option.build() for _ in range(3)],
        "initial_option": required_option.build(),
        "confirm": confirm.build(),
    }


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


def test_builds_conversations_multiselect(plain_text, values, confirm):
    initial_conversations = ["C123456", "C654321"]

    multiselect = MultiConversationsSelect(
        plain_text,
        values.action_id,
        confirm=confirm,
        max_selected_items=3,
        initial_conversations=initial_conversations,
    )

    assert multiselect.build() == {
        "type": "multi_conversations_select",
        "placeholder": plain_text.build(),
        "action_id": values.action_id,
        "confirm": confirm.build(),
        "max_selected_items": 3,
        "initial_conversations": initial_conversations,
    }


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
