import pytest

from blockkit import Text, Option

TITLE = "Bot thought"
TEXT = "The way to get started is to quit _talking_ and begin *doing*"
SHORT_TEXT = "Do it well"
IMAGE = "http://placekitten.com/200/200"
ALT_TEXT = "There is a kitten"
URL = "https://example.com"
VALUE = "test_value"
ACTION_ID = "test_action"
CONFIRM_TEXT = "Confirm"
DENY_TEXT = "Deny"
VALUE = "value"


@pytest.fixture
def basic_text():
    return Text(TEXT)


@pytest.fixture
def short_text():
    return Text(SHORT_TEXT, type=Text.plain)


@pytest.fixture
def plain_text():
    return Text(TEXT, type=Text.plain)


@pytest.fixture
def basic_option(plain_text):
    return Option(plain_text, VALUE)
