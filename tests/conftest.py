from collections import namedtuple

import pytest

from blockkit import Option, Text

TestValues = namedtuple(
    "TestValues",
    (
        "title text short_text image_url alt_text url "
        "action_id confirm_text deny_text value"
    ),
)


@pytest.fixture
def values():
    return TestValues(
        title="Bot thought",
        text="The way to get started is to quit _talking_ and begin *doing*",
        short_text="Do it well",
        image_url="http://placekitten.com/200/200",
        alt_text="There is a kitten",
        url="https://example.com",
        action_id="test_action",
        confirm_text="Confirm",
        deny_text="Deny",
        value="value",
    )


@pytest.fixture
def basic_text(values):
    return Text(values.text)


@pytest.fixture
def short_text(values):
    return Text(values.short_text, type=Text.plain)


@pytest.fixture
def plain_text(values):
    return Text(values.text, type=Text.plain)


@pytest.fixture
def basic_option(plain_text, values):
    return Option(plain_text, values.value)
