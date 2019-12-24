import pytest

from blockkit import Confirm, Option, OptionGroup, Text, MarkdownText, PlainText
from blockkit.validators import ValidationError


def test_builds_markdown_text(values):
    assert MarkdownText(values.text, verbatim=True).build() == {
        "type": Text.markdown,
        "text": values.text,
        "verbatim": True,
    }


def test_builds_plain_text_with_emoji(values):
    text = PlainText(values.text, emoji=True)
    assert text.build() == {"type": Text.plain, "text": values.text, "emoji": True}


def test_mrkdwn_text_with_emoji_raises_exception(values):
    with pytest.raises(ValidationError):
        Text(values.text, type_=Text.markdown, emoji=True)


def test_plain_text_with_verbatim_raises_exception(values):
    with pytest.raises(ValidationError):
        Text(values.text, type_=Text.plain, verbatim=True)


def test_builds_confirm(plain_text, basic_text, values):
    confirm = Confirm(
        plain_text,
        basic_text,
        Text(values.confirm_text, type_=Text.plain),
        Text(values.deny_text, type_=Text.plain),
    )

    assert confirm.build() == {
        "title": {"type": Text.plain, "text": values.text},
        "text": {"type": Text.markdown, "text": values.text},
        "confirm": {"type": Text.plain, "text": values.confirm_text},
        "deny": {"type": Text.plain, "text": values.deny_text},
    }


def test_builds_option(plain_text, values):
    option = Option(plain_text, values.value, values.url)

    assert option.build() == {
        "text": {"type": Text.plain, "text": values.text},
        "value": values.value,
        "url": values.url,
    }


def test_builds_option_group(plain_text, basic_option, values):
    option_group = OptionGroup(plain_text, [basic_option for _ in range(3)])

    assert option_group.build() == {
        "label": {"type": Text.plain, "text": values.text},
        "options": [basic_option.build() for _ in range(3)],
    }
