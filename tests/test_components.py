from blockkit import Confirm, Context, Image


def test_expands_str():
    assert Confirm(
        title="title",
        text="*markdown* text",
        confirm="confirm",
        deny="deny",
        style="primary",
    ).build() == {
        "title": {"type": "plain_text", "text": "title", "emoji": True},
        "text": {"type": "mrkdwn", "text": "*markdown* text"},
        "confirm": {"type": "plain_text", "text": "confirm", "emoji": True},
        "deny": {"type": "plain_text", "text": "deny", "emoji": True},
        "style": "primary",
    }


def test_expands_str_list():
    assert Context(
        elements=[
            Image(image_url="http://placekitten.com/300/200", alt_text="kitten"),
            "element 1",
            "element 2",
        ]
    ).build() == {
        "type": "context",
        "elements": [
            {
                "type": "image",
                "image_url": "http://placekitten.com/300/200",
                "alt_text": "kitten",
            },
            {
                "type": "mrkdwn",
                "text": "element 1",
            },
            {
                "type": "mrkdwn",
                "text": "element 2",
            },
        ],
    }
