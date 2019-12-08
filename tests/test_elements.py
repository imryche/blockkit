from blockkit import Button, DatePicker, Image


def test_builds_button(values, plain_text, confirm):
    button = Button(
        plain_text, values.action_id, values.url, values.value, Button.primary, confirm
    )

    assert button.build() == {
        "type": "button",
        "text": plain_text.build(),
        "action_id": values.action_id,
        "url": values.url,
        "value": values.value,
        "style": Button.primary,
        "confirm": confirm.build(),
    }


def test_builds_datepicker(values, plain_text, confirm):
    datepicker = DatePicker(values.action_id, plain_text, values.date, confirm)

    assert datepicker.build() == {
        "type": "datepicker",
        "action_id": values.action_id,
        "placeholder": plain_text.build(),
        "initial_date": values.date,
        "confirm": confirm.build(),
    }


def test_builds_image(values):
    image = Image(values.image_url, values.alt_text)

    assert image.build() == {
        "type": "image",
        "image_url": values.image_url,
        "alt_text": values.alt_text
    }
