import pytest

from blockkit import Image

from .conftest import TEST_IMAGE, TEST_ALT_TEXT


def test_builds_image(basic_image):
    assert basic_image.build() == {
        'type': 'image',
        'image_url': TEST_IMAGE,
        'alt_text': TEST_ALT_TEXT
    }


def test_image_with_incorrect_url_raises_exception():
    with pytest.raises(ValueError):
        Image('bad_url', 'Bad Url')
