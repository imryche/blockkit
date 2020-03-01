from blockkit import Section, Message, Modal, Home


def test_builds_message(values, markdown_text, button):
    blocks = [Section(markdown_text, accessory=button)]
    attachments = [
        {
            "color": "#36a64f",
            "mrkdwn_in": ["text"],
            "text": "Optional `text` that appears within the attachment",
        }
    ]
    thread_ts = "1233333456.33"
    mrkdwn = True

    message = Message(
        values.text,
        blocks=blocks,
        attachments=attachments,
        thread_ts=thread_ts,
        mrkdwn=mrkdwn,
    )

    assert message.build() == {
        "text": values.text,
        "blocks": [b.build() for b in blocks],
        "attachments": attachments,
        "thread_ts": thread_ts,
        "mrkdwn": mrkdwn,
    }


def test_builds_modal(values, modal_text, markdown_text, button):
    blocks = [Section(markdown_text, accessory=button)]
    private_metadata = "foobar"
    callback_id = "view_callback"
    clear_on_close = True
    notify_on_close = False
    external_id = "external"

    modal = Modal(
        modal_text,
        blocks,
        close=modal_text,
        submit=modal_text,
        private_metadata=private_metadata,
        callback_id=callback_id,
        clear_on_close=clear_on_close,
        notify_on_close=notify_on_close,
        external_id=external_id,
    )

    assert modal.build() == {
        "type": "modal",
        "title": modal_text.build(),
        "blocks": [b.build() for b in blocks],
        "close": modal_text.build(),
        "submit": modal_text.build(),
        "private_metadata": private_metadata,
        "callback_id": callback_id,
        "clear_on_close": clear_on_close,
        "notify_on_close": notify_on_close,
        "external_id": external_id,
    }


def test_builds_home(values, markdown_text, button):
    blocks = [Section(markdown_text, accessory=button)]
    private_metadata = "foobar"
    callback_id = "view_callback"
    external_id = "external"

    home = Home(
        blocks,
        private_metadata=private_metadata,
        callback_id=callback_id,
        external_id=external_id,
    )

    assert home.build() == {
        "type": "home",
        "blocks": [b.build() for b in blocks],
        "private_metadata": private_metadata,
        "callback_id": callback_id,
        "external_id": external_id,
    }
