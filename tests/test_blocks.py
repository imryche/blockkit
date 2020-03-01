import pytest

from blockkit import (
    Actions,
    Context,
    Divider,
    File,
    ImageBlock,
    Input,
    PlainTextInput,
    Section,
)
from blockkit.fields import ValidationError


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


def test_section_without_text_and_fields_raises_exception(values, button):
    with pytest.raises(ValidationError):
        Section(accessory=button)


def test_builds_divider(values):
    divider = Divider(values.block_id)

    assert divider.build() == {
        "type": "divider",
        "block_id": values.block_id,
    }


def test_builds_image_block(values, plain_text):
    image = ImageBlock(
        values.image_url, values.text, title=plain_text, block_id=values.block_id,
    )

    assert image.build() == {
        "type": "image",
        "image_url": values.image_url,
        "alt_text": values.text,
        "title": plain_text.build(),
        "block_id": values.block_id,
    }


def test_builds_actions(values, button):
    actions = Actions([button for _ in range(4)], values.block_id,)

    assert actions.build() == {
        "type": "actions",
        "elements": [button.build() for _ in range(4)],
        "block_id": values.block_id,
    }


def test_builds_context(values, plain_text, image):
    context = Context([plain_text, image], values.block_id,)

    assert context.build() == {
        "type": "context",
        "elements": [plain_text.build(), image.build()],
        "block_id": values.block_id,
    }


def test_builds_input(values, plain_text):
    optional = True
    text_input = PlainTextInput(values.action_id)

    input_ = Input(
        plain_text,
        text_input,
        block_id=values.block_id,
        hint=plain_text,
        optional=optional,
    )

    assert input_.build() == {
        "type": "input",
        "label": plain_text.build(),
        "element": text_input.build(),
        "block_id": values.block_id,
        "hint": plain_text.build(),
        "optional": optional,
    }


def test_builds_file(values):
    external_id = "dfj345g"
    source = "remote"

    file_ = File(external_id, source, values.block_id,)

    assert file_.build() == {
        "type": "file",
        "external_id": external_id,
        "source": source,
        "block_id": values.block_id,
    }
