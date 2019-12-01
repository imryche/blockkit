import pytest

from blockkit import Confirm, Option, OptionGroup, Text
from blockkit.validators import ValidationError

from .conftest import CONFIRM_TEXT, DENY_TEXT, TEXT, URL, VALUE


def test_builds_markdown_text():
    assert Text(TEXT).build() == {"type": "mrkdwn", "text": TEXT}


def test_builds_plain_text_with_emoji():
    text = Text(TEXT, type=Text.PLAIN, emoji=True)
    assert text.build() == {"type": Text.PLAIN, "text": TEXT, "emoji": True}


def test_builds_markdown_text_with_no_emoji_and_verbatim():
    text = Text(TEXT, type=Text.MARKDOWN, emoji=False, verbatim=True)

    assert text.build() == {
        "type": Text.MARKDOWN,
        "text": TEXT,
        "emoji": False,
        "verbatim": True,
    }


def test_mrkdwn_text_with_emoji_raises_exception():
    with pytest.raises(ValidationError):
        Text(TEXT, type=Text.MARKDOWN, emoji=True)


def test_plain_text_with_verbatim_raises_exception():
    with pytest.raises(ValidationError):
        Text(TEXT, type=Text.PLAIN, verbatim=True)


def test_builds_confirm(plain_text, basic_text):
    confirm = Confirm(
        plain_text,
        basic_text,
        Text(CONFIRM_TEXT, type=Text.PLAIN),
        Text(DENY_TEXT, type=Text.PLAIN),
    )

    assert confirm.build() == {
        "title": {"type": Text.PLAIN, "text": TEXT},
        "text": {"type": Text.MARKDOWN, "text": TEXT},
        "confirm": {"type": Text.PLAIN, "text": CONFIRM_TEXT},
        "deny": {"type": Text.PLAIN, "text": DENY_TEXT},
    }


def test_builds_option(plain_text):
    option = Option(plain_text, VALUE, URL)

    assert option.build() == {
        "text": {"type": Text.PLAIN, "text": TEXT},
        "value": VALUE,
        "url": URL,
    }


def test_builds_option_group(plain_text, basic_option):
    option_group = OptionGroup(plain_text, [basic_option for _ in range(3)])

    assert option_group.build() == {
        "label": {"type": Text.PLAIN, "text": TEXT},
        "options": [basic_option.build() for _ in range(3)],
    }
