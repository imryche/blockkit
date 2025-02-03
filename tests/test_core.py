import pytest

from blockkit.core import (
    Button,
    Component,
    MarkdownText,
    MaxLength,
    NonEmpty,
    Required,
    ValidationError,
)


class TestValidators:
    def test_required(self):
        class PlainText(Component):
            def __init__(self, text=None):
                super().__init__()
                self.text(text)

            def text(self, text):
                self._add_field("text", text, validators=[Required()])

        with pytest.raises(ValidationError):
            PlainText().validate()

    def test_non_empty(self):
        class PlainText(Component):
            def __init__(self, text=None):
                super().__init__()
                self.text(text)

            def text(self, text):
                self._add_field("text", text, validators=[NonEmpty()])

        with pytest.raises(ValidationError):
            PlainText("").validate()

    def test_max_length(self):
        class PlainText(Component):
            def __init__(self, text=None):
                super().__init__()
                self.text(text)

            def text(self, text):
                self._add_field("text", text, validators=[MaxLength(3)])

        with pytest.raises(ValidationError):
            PlainText("aaaa").validate()


class TestMarkdownText:
    def test_builds(self):
        got = MarkdownText("hello alice!").build()
        want = {"type": "mrkdwn", "text": "hello alice!"}
        assert got == want

        want = {"type": "mrkdwn", "text": "hello alice!", "verbatim": True}
        got = MarkdownText("hello alice!", verbatim=True).build()
        assert got == want

        got = MarkdownText().text("hello alice!").verbatim().build()
        assert got == want


class TestButton:
    def test_builds(self):
        got = Button("Click me").build()
        want = {"type": "button", "text": {"type": "plain_text", "text": "Click me"}}
        assert got == want

        want = {
            "type": "button",
            "text": {"type": "plain_text", "text": "Click me"},
            "action_id": "clicked",
            "value": "1",
            "style": "primary",
        }

        got = Button(
            "Click me",
            action_id="clicked",
            value="1",
            style="primary",
        ).build()
        assert got == want

        got = (
            Button()
            .text("Click me")
            .action_id("clicked")
            .value("1")
            .style("primary")
            .build()
        )
        assert got == want
