import pytest

from blockkit import Image, Section, Text

TEST_TEXT = 'The way to get started is to quit _talking_ and begin *doing*'
TEST_IMAGE = 'http://placekitten.com/200/200'
TEST_ALT_TEXT = 'There is a kitten'
TEST_URL = 'https://example.com'
TEST_VALUE = 'test_value'
TEST_ACTION_ID = 'test_action'


@pytest.fixture
def basic_text():
    return Text(TEST_TEXT)


@pytest.fixture
def basic_image():
    return Image(TEST_IMAGE, TEST_ALT_TEXT)


@pytest.fixture
def basic_section(basic_text):
    return Section(basic_text)
