import pytest
from pydantic import ValidationError

from blockkit.objects import (
    Confirm,
    DispatchActionConfig,
    Emoji,
    Filter,
    Include,
    MarkdownText,
    OptionGroup,
    PlainOption,
    PlainText,
    Style,
    Text,
    TriggerActionsOn,
)


def test_builds_markdown_text():
    assert MarkdownText(text="*markdown* text", verbatim=True).build() == {
        "type": "mrkdwn",
        "text": "*markdown* text",
        "verbatim": True,
    }


def test_markdown_text_empty_text_raises_exception():
    with pytest.raises(ValidationError):
        MarkdownText(text="")


def test_builds_plain_text():
    assert PlainText(text="plain text", emoji=True).build() == {
        "type": "plain_text",
        "text": "plain text",
        "emoji": True,
    }


def test_plain_text_empty_text_raises_exception():
    with pytest.raises(ValidationError):
        PlainText(text="")


def test_builds_confirm():
    assert Confirm(
        title=PlainText(text="title"),
        text=MarkdownText(text="*markdown* text"),
        confirm=PlainText(text="confirm"),
        deny=PlainText(text="deny"),
        style="primary",
    ).build() == {
        "title": {"type": "plain_text", "text": "title"},
        "text": {"type": "mrkdwn", "text": "*markdown* text"},
        "confirm": {"type": "plain_text", "text": "confirm"},
        "deny": {"type": "plain_text", "text": "deny"},
        "style": "primary",
    }


def test_confirm_excessive_title_raises_exception():
    with pytest.raises(ValidationError):
        Confirm(
            title=PlainText(text="t" * 101),
            text=MarkdownText(text="*markdown* text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
            style="primary",
        )


def test_confirm_excessive_text_raises_exception():
    with pytest.raises(ValidationError):
        Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="m" * 301),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
            style="primary",
        )


def test_confirm_excessive_confirm_raises_exception():
    with pytest.raises(ValidationError):
        Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="*markdown* text"),
            confirm=PlainText(text="c" * 31),
            deny=PlainText(text="deny"),
            style="primary",
        )


def test_confirm_excessive_deny_raises_exception():
    with pytest.raises(ValidationError):
        Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="*markdown* text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny" * 31),
            style="primary",
        )


def test_confirm_incorrect_style_raises_exception():
    with pytest.raises(ValidationError):
        Confirm(
            title=PlainText(text="title"),
            text=MarkdownText(text="*markdown* text"),
            confirm=PlainText(text="confirm"),
            deny=PlainText(text="deny"),
            style="secondary",
        )


def test_builds_option():
    assert PlainOption(
        text=PlainText(text="text"),
        value="value",
        description=PlainText(text="description"),
        url="https://example.com",
    ).build() == {
        "text": {"type": "plain_text", "text": "text"},
        "value": "value",
        "description": {"type": "plain_text", "text": "description"},
        "url": "https://example.com/",
    }


def test_option_excessive_text_raises_exception():
    with pytest.raises(ValidationError):
        PlainOption(
            text=PlainText(text="t" * 76),
            value="value",
        )


def test_option_empty_value_raises_exception():
    with pytest.raises(ValidationError):
        PlainOption(
            text=PlainText(text="text"),
            value="",
        )


def test_option_excessive_value_raises_exception():
    with pytest.raises(ValidationError):
        PlainOption(
            text=PlainText(text="text"),
            value="v" * 76,
        )


def test_option_excessive_description_raises_exception():
    with pytest.raises(ValidationError):
        PlainOption(
            text=PlainText(text="text"),
            value="value",
            description=PlainText(text="d" * 76),
        )


def test_option_empty_url_raises_exception():
    with pytest.raises(ValidationError):
        PlainOption(
            text=PlainText(text="text"),
            value="value",
            url="",
        )


def test_option_excessive_url_raises_exception():
    with pytest.raises(ValidationError):
        url = "https://example.com/"
        PlainOption(
            text=PlainText(text="text"),
            value="value",
            url=url + "u" * (3001 - len(url)),
        )


def test_builds_option_group():
    assert OptionGroup(
        label=PlainText(text="label"),
        options=[
            PlainOption(text=PlainText(text="option 1"), value="value_1"),
            PlainOption(text=PlainText(text="option 2"), value="value_2"),
        ],
    ).build() == {
        "label": {"type": "plain_text", "text": "label"},
        "options": [
            {"text": {"type": "plain_text", "text": "option 1"}, "value": "value_1"},
            {"text": {"type": "plain_text", "text": "option 2"}, "value": "value_2"},
        ],
    }


def test_option_group_excessive_label_raises_exception():
    with pytest.raises(ValidationError):
        OptionGroup(
            label=PlainText(text="l" * 76),
            options=[PlainOption(text=PlainText(text="option 1"), value="value_1")],
        )


def test_option_group_excessive_options_raise_exception():
    with pytest.raises(ValidationError):
        OptionGroup(
            label=PlainText(text="label"),
            options=[
                PlainOption(text=PlainText(text=f"option {o}"), value=f"value_{0}")
                for o in range(101)
            ],
        )


def test_option_group_empty_options_raise_exception():
    with pytest.raises(ValidationError):
        OptionGroup(label=PlainText(text="label"), options=[])


def test_builds_dispatch_action_config():
    assert DispatchActionConfig(
        trigger_actions_on=[
            TriggerActionsOn.on_enter_pressed,
            TriggerActionsOn.on_character_entered,
        ]
    ).build() == {"trigger_actions_on": ["on_enter_pressed", "on_character_entered"]}


def test_dispatch_action_config_incorrect_trigger_raises_exception():
    with pytest.raises(ValidationError):
        DispatchActionConfig(trigger_actions_on=["on_something_happened"])


def test_dispatch_action_config_empty_triggers_raise_exception():
    with pytest.raises(ValidationError):
        DispatchActionConfig(trigger_actions_on=[])


def test_dispatch_action_config_excessive_triggers_raise_exception():
    with pytest.raises(ValidationError):
        DispatchActionConfig(
            trigger_actions_on=[
                TriggerActionsOn.on_enter_pressed,
                TriggerActionsOn.on_enter_pressed,
                TriggerActionsOn.on_enter_pressed,
            ]
        )


def test_builds_filter():
    assert Filter(
        include=[Include.im, Include.mpim, Include.private, Include.public],
        exclude_external_shared_channels=False,
        exclude_bot_users=False,
    ).build() == {
        "include": ["im", "mpim", "private", "public"],
        "exclude_external_shared_channels": False,
        "exclude_bot_users": False,
    }


def test_empty_filter_raises_exception():
    with pytest.raises(ValidationError):
        Filter()


def test_filter_with_incorrect_include_raises_exception():
    with pytest.raises(ValidationError):
        Filter(include=["group"])


def test_builds_emoji():
    assert Emoji(name="raised_hands").build() == {
        "type": "emoji",
        "name": "raised_hands",
    }


def test_empty_emoji_raises_exception():
    with pytest.raises(ValidationError):
        Emoji(name="")


def test_builds_style():
    assert Style(bold=True, italic=False, strike=None, code=True).build() == {
        "bold": True,
        "italic": False,
        "code": True,
    }


def test_empty_style_is_ok():
    assert Style().build() == {}


def test_builds_text():
    assert Text(text="text", style=Style(bold=True, code=True)).build() == {
        "type": "text",
        "text": "text",
        "style": {"code": True, "bold": True},
    }


def test_empty_text_raises_exception():
    with pytest.raises(ValidationError):
        Text(text="")
