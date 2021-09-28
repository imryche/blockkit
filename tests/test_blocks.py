import pytest
from blockkit import (
    Actions,
    Context,
    Divider,
    File,
    Header,
    ImageBlock,
    Input,
    PlainText,
    PlainTextInput,
    Section,
    UsersSelect,
)
from blockkit.elements import Button, Image
from blockkit.objects import MarkdownText
from pydantic import ValidationError


def test_builds_actions():
    assert Actions(
        elements=[
            Button(text=PlainText(text="text"), action_id="action_id_button"),
            UsersSelect(
                placeholder=PlainText(text="placeholder"), action_id="action_id_select"
            ),
        ],
        block_id="block_id",
    ).build() == {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "text"},
                "action_id": "action_id_button",
            },
            {
                "type": "users_select",
                "placeholder": {"type": "plain_text", "text": "placeholder"},
                "action_id": "action_id_select",
            },
        ],
        "block_id": "block_id",
    }


def test_actions_excessive_block_id_raises_exception():
    with pytest.raises(ValidationError):
        Actions(
            elements=[Button(text=PlainText(text="text"), action_id="action_id")],
            block_id="b" * 256,
        )


def test_actions_empty_elements_raise_exception():
    with pytest.raises(ValidationError):
        Actions(elements=[])


def test_actions_excessive_elements_raise_exception():
    with pytest.raises(ValidationError):
        Actions(
            elements=[
                Button(text=PlainText(text=f"text"), action_id=f"action_id")
                for _ in range(6)
            ]
        )


def test_builds_context():
    assert Context(
        elements=[
            Image(image_url="http://placekitten.com/100/100", alt_text="kitten"),
            MarkdownText(text="*markdown* text"),
        ],
        block_id="block_id",
    ).build() == {
        "type": "context",
        "elements": [
            {
                "type": "image",
                "image_url": "http://placekitten.com/100/100",
                "alt_text": "kitten",
            },
            {"type": "mrkdwn", "text": "*markdown* text"},
        ],
        "block_id": "block_id",
    }


def test_context_excessive_block_id_raises_exception():
    with pytest.raises(ValidationError):
        Context(
            elements=[MarkdownText(text="*markdown* text")],
            block_id="b" * 256,
        )


def test_context_empty_elements_raise_exception():
    with pytest.raises(ValidationError):
        Context(elements=[])


def test_context_excessive_elements_raise_exception():
    with pytest.raises(ValidationError):
        Context(elements=[MarkdownText(text="*markdown* text") for _ in range(11)])


def test_builds_divider():
    assert Divider(block_id="block_id").build() == {
        "type": "divider",
        "block_id": "block_id",
    }


@pytest.mark.skip
def test_builds_section(values, markdown_text, button):
    section = Section(
        markdown_text,
        block_id=values.block_id,
        fields=[markdown_text for _ in range(2)],
        accessory=button,
    )

    assert section.build() == {
        "type": "section",
        "text": markdown_text.build(),
        "block_id": values.block_id,
        "fields": [markdown_text.build() for _ in range(2)],
        "accessory": button.build(),
    }


@pytest.mark.skip
def test_section_without_text_and_fields_raises_exception(values, button):
    with pytest.raises(ValidationError):
        Section(accessory=button)


@pytest.mark.skip
def test_builds_image_block(values, plain_text):
    image = ImageBlock(
        values.image_url,
        values.text,
        title=plain_text,
        block_id=values.block_id,
    )

    assert image.build() == {
        "type": "image",
        "image_url": values.image_url,
        "alt_text": values.text,
        "title": plain_text.build(),
        "block_id": values.block_id,
    }


@pytest.mark.skip
def test_builds_input(values, plain_text):
    optional = True
    dispatch_action = True
    text_input = PlainTextInput(values.action_id)

    input_ = Input(
        plain_text,
        text_input,
        dispatch_action=dispatch_action,
        block_id=values.block_id,
        hint=plain_text,
        optional=optional,
    )

    assert input_.build() == {
        "type": "input",
        "label": plain_text.build(),
        "element": text_input.build(),
        "dispatch_action": dispatch_action,
        "block_id": values.block_id,
        "hint": plain_text.build(),
        "optional": optional,
    }


@pytest.mark.skip
def test_builds_file(values):
    external_id = "dfj345g"
    source = "remote"

    file_ = File(
        external_id,
        source,
        values.block_id,
    )

    assert file_.build() == {
        "type": "file",
        "external_id": external_id,
        "source": source,
        "block_id": values.block_id,
    }


@pytest.mark.skip
def test_builds_header(values, plain_text):
    header = Header(plain_text, values.block_id)

    assert header.build() == {
        "type": "header",
        "text": plain_text.build(),
        "block_id": values.block_id,
    }
