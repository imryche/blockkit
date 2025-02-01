import pytest

from blockkit.core import Button, MarkdownText, ValidationError


class TestMarkdownText:
    def test_builds(self):
        got = MarkdownText("hello alice!").build()
        want = {"type": "mrkdwn", "text": "hello alice!"}
        assert got == want

        got = MarkdownText("hello alice!", verbatim=True).build()
        want = {"type": "mrkdwn", "text": "hello alice!", "verbatim": True}
        assert got == want

        got = MarkdownText().text("hello alice!").verbatim().build()
        want = {"type": "mrkdwn", "text": "hello alice!", "verbatim": True}
        assert got == want

    def test_validates_empty_text(self):
        with pytest.raises(ValidationError):
            MarkdownText("").build()

    def test_validates_required_fields(self):
        with pytest.raises(ValidationError):
            MarkdownText().build()


class TestButton:
    def test_builds(self):
        got = Button(
            "Click me",
            action_id="button_clicked",
            value="1",
            style="primary",
        ).build()
        want = {
            "type": "button",
            "text": {
                "type": "mrkdwn",
                "text": "Click me",
            },
            "action_id": "button_clicked",
            "value": "1",
            "style": "primary",
        }
        assert got == want

    def test_validates_extra_long_text(self):
        with pytest.raises(ValidationError):
            Button("C" * 76).build()
