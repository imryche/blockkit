from collections import namedtuple

import pytest

from blockkit import Confirm, Option, OptionGroup, Text

TestValues = namedtuple(
    "TestValues",
    (
        "title text short_text image_url alt_text url "
        "action_id confirm_text deny_text value date"
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
        date="2019-12-08",
    )


@pytest.fixture
def basic_text(values):
    return Text(values.text, type_=Text.markdown)


@pytest.fixture
def short_text(values):
    return Text(values.short_text, type_=Text.plain)


@pytest.fixture
def plain_text(values):
    return Text(values.text, type_=Text.plain)


@pytest.fixture
def basic_option(plain_text, values):
    return Option(plain_text, values.value)


@pytest.fixture
def confirm(values, plain_text, basic_text):
    return Confirm(
        plain_text,
        basic_text,
        Text(values.confirm_text, type_=Text.plain),
        Text(values.deny_text, type_=Text.plain),
    )


@pytest.fixture
def option(values, plain_text):
    return Option(plain_text, values.value)


@pytest.fixture
def option_group(values, plain_text, option):
    return OptionGroup(plain_text, [option for _ in range(2)])


@pytest.fixture
def required_option(request, option, option_group):
    return {
        'option': option,
        'option_group': option_group
    }[request.param]
