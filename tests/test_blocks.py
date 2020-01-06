from blockkit import Section, Divider


def test_builds_section(values, basic_text, button):
    section = Section(
        basic_text,
        block_id=values.block_id,
        fields=[basic_text for _ in range(2)],
        accessory=button,
    )

    assert section.build() == {
        "type": "section",
        "text": basic_text.build(),
        "block_id": values.block_id,
        "fields": [basic_text.build() for _ in range(2)],
        "accessory": button.build(),
    }


def test_builds_divider(values):
    divider = Divider(values.block_id)

    assert divider.build() == {
        "type": "divider",
        "block_id": values.block_id,
    }
