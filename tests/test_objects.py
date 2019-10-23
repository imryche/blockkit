import pytest

from blockkit import Text, Confirm

TEST_TEXT = 'The way to get started is to quit _talking_ and begin *doing*'


def test_builds_markdown_text():
    assert Text(TEST_TEXT).build() == {'type': 'mrkdwn', 'text': TEST_TEXT}


def test_builds_plain_text_with_emoji():
    assert Text(TEST_TEXT, type=Text.PLAIN, emoji=True).build() == {
        'type': Text.PLAIN,
        'text': TEST_TEXT,
        'emoji': True
    }


def test_builds_plain_text_with_no_emoji_and_verbatim():
    text = Text(TEST_TEXT, type=Text.PLAIN, emoji=False, verbatim=True)

    assert text.build() == {
        'type': Text.PLAIN,
        'text': TEST_TEXT,
        'emoji': False,
        'verbatim': True
    }


def test_text_with_incorrect_type_raises_exception():
    with pytest.raises(ValueError):
        Text(TEST_TEXT, type='html')


def test_text_with_incorrect_emoji_type_raises_exception():
    with pytest.raises(ValueError):
        Text(TEST_TEXT, Text.PLAIN, emoji='true')


def test_mrkdwn_text_with_emoji_raises_exception():
    with pytest.raises(ValueError):
        Text(TEST_TEXT, type='mrkdwn', emoji=True)


def test_text_with_incorrect_verbatim_raises_exception():
    with pytest.raises(ValueError):
        Text(TEST_TEXT, verbatim='true')


def test_builds_confirm_dialog(plain_text, basic_text):
    confirm_text = 'Confirm'
    deny_text = 'Deny'

    confirm = Confirm(plain_text, basic_text,
                      Text(confirm_text, type=Text.PLAIN),
                      Text(deny_text, type=Text.PLAIN))

    assert confirm.build() == {
        'title': {
            'type': Text.PLAIN,
            'text': TEST_TEXT
        },
        'text': {
            'type': Text.MARKDOWN,
            'text': TEST_TEXT
        },
        'confirm': {
            'type': Text.PLAIN,
            'text': confirm_text,
        },
        'deny': {
            'type': Text.PLAIN,
            'text': deny_text
        }
    }


def test_confirm_with_markdown_title_raises_exception(basic_text, plain_text):
    with pytest.raises(ValueError):
        Confirm(basic_text, plain_text, plain_text, plain_text)


def test_confirm_with_markdown_confirm_raises_exception(
        basic_text, plain_text):
    with pytest.raises(ValueError):
        Confirm(plain_text, basic_text, basic_text, plain_text)


def test_confirm_with_markdown_deny_raises_exception(basic_text, plain_text):
    with pytest.raises(ValueError):
        Confirm(plain_text, basic_text, plain_text, basic_text)
