from blockkit import Section, Divider, ImageBlock, Actions, Context


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


def test_builds_divider(values):
    divider = Divider(values.block_id)

    assert divider.build() == {
        "type": "divider",
        "block_id": values.block_id,
    }


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


def test_builds_actions(values, button):
    actions = Actions(
        [button for _ in range(4)],
        values.block_id,
    )

    assert actions.build() == {
        "type": "actions",
        "elements": [button.build() for _ in range(4)],
        "block_id": values.block_id,
    }


def test_builds_context(values, plain_text, image):
    context = Context(
        [plain_text, image],
        values.block_id,
    )

    assert context.build() == {
        "type": "context",
        "elements": [plain_text.build(), image.build()],
        "block_id": values.block_id,
    }
