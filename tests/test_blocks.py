import pytest

from blockkit import Section

from .conftest import TEST_ALT_TEXT, TEST_IMAGE, TEST_TEXT


def test_section_builds_correctly(basic_text, basic_image):
    section = Section(basic_text,
                      fields=[basic_text, basic_text],
                      accessory=basic_image,
                      block_id='test_block')

    assert section.build() == {
        'type':
        'section',
        'block_id':
        'test_block',
        'text': {
            'type': 'mrkdwn',
            'text': TEST_TEXT
        },
        'fields': [{
            'type': 'mrkdwn',
            'text': TEST_TEXT
        }, {
            'type': 'mrkdwn',
            'text': TEST_TEXT
        }],
        'accessory': {
            'type': 'image',
            'image_url': TEST_IMAGE,
            'alt_text': TEST_ALT_TEXT
        }
    }


def test_section_incorrect_text_raises_exception(basic_image):
    with pytest.raises(ValueError):
        Section(basic_image)


def test_section_empty_fields_raises_exception(basic_text):
    with pytest.raises(ValueError):
        Section(basic_text, fields=[])


def test_section_with_incorrect_fields_raises_exception(
        basic_text, basic_image):
    with pytest.raises(ValueError):
        Section(basic_text, fields=[basic_image])


def test_section_with_incorrect_accessory_raises_exception(basic_text):
    with pytest.raises(ValueError):
        Section(basic_text, accessory=basic_text)
