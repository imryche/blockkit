from blockkit import Section, Message


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
