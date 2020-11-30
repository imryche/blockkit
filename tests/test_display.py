import io
import sys

import pytest

from blockkit import Message, Section
from blockkit.display import create_block_kit_builder_url


def test_create_block_kit_builder_url_success_with_object():
    message = Message(
        blocks=[
            Section(text="HELLLOOOO WORLD!")
        ]
    )

    captured_output = io.StringIO()
    sys.stdout = captured_output

    create_block_kit_builder_url(message)

    sys.stdout = sys.__stdout__  # Re-direct output to console

    resulting_message = "Block kit builder example/validation:  " \
                        "\n\thttps://app.slack.com/block-kit-builder/#%7B%22blocks%22:%20%5B%7B%22type%22:%20" \
                        "%22section%22%2C%20%22text%22:%20%7B%22text%22:%20%22HELLLOOOO%20WORLD%21%22%2C%20%22type%22" \
                        ":%20%22plain_text%22%2C%20%22emoji%22:%20true%7D%7D%5D%7D\n"

    assert captured_output.getvalue() == resulting_message


def test_create_block_kit_builder_url_success_with_object_build():
    message = Message(
        blocks=[
            Section(text="HELLLOOOO WORLD!")
        ]
    )

    captured_output = io.StringIO()
    sys.stdout = captured_output

    create_block_kit_builder_url(message.build())

    sys.stdout = sys.__stdout__  # Re-direct output to console

    resulting_message = "Block kit builder example/validation:  " \
                        "\n\thttps://app.slack.com/block-kit-builder/#%7B%22blocks%22:%20%5B%7B%22type%22:%20" \
                        "%22section%22%2C%20%22text%22:%20%7B%22text%22:%20%22HELLLOOOO%20WORLD%21%22%2C%20%22type%22" \
                        ":%20%22plain_text%22%2C%20%22emoji%22:%20true%7D%7D%5D%7D\n"

    assert captured_output.getvalue() == resulting_message


def test_create_block_kit_builder_url_throws_with_invalid_object():
    with pytest.raises(Exception):
        create_block_kit_builder_url(None)
