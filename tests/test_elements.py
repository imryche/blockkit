import pytest

from blockkit import Button, Image, Text

from .conftest import (TEST_ALT_TEXT, TEST_IMAGE, TEST_TEXT, TEST_URL,
                       TEST_VALUE, TEST_ACTION_ID)


def test_builds_text_button_with_style_and_value(plain_text):
    button = Button(plain_text,
                    value=TEST_VALUE,
                    style=Button.PRIMARY,
                    action_id=TEST_ACTION_ID)

    assert button.build() == {
        'type': Button.TYPE,
        'action_id': TEST_ACTION_ID,
        'style': Button.PRIMARY,
        'text': {
            'type': Text.PLAIN,
            'text': TEST_TEXT
        },
        'value': TEST_VALUE
    }


def test_builds_url_button(plain_text):
    button = Button(plain_text, url=TEST_URL)
    assert button.build() == {
        'type': Button.TYPE,
        'text': {
            'type': Text.PLAIN,
            'text': TEST_TEXT
        },
        'url': TEST_URL
    }


def test_button_with_incorrect_text_raises_exception(basic_image):
    with pytest.raises(ValueError):
        Button(basic_image)


def test_button_with_markdown_text_raises_exception(basic_text):
    with pytest.raises(ValueError):
        Button(basic_text)


def test_button_with_incorrect_url_raises_exception(plain_text):
    with pytest.raises(ValueError):
        Button(plain_text, url='bad_url')


def test_button_with_incorrect_style_raises_exception(plain_text):
    with pytest.raises(ValueError):
        Button(plain_text, style='warning')


def test_builds_image(basic_image):
    assert basic_image.build() == {
        'type': Image.TYPE,
        'image_url': TEST_IMAGE,
        'alt_text': TEST_ALT_TEXT
    }


def test_image_with_incorrect_url_raises_exception():
    with pytest.raises(ValueError):
        Image('bad_url', 'Bad Url')
