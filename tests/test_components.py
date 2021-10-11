from blockkit.objects import Confirm


def test_converts_str():
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
