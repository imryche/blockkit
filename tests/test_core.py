import pytest

from blockkit.core import (
    Button,
    Component,
    MarkdownText,
    MaxLength,
    NonEmpty,
    Required,
    Typed,
    ValidationError,
)


@pytest.fixture
def plain_text():
    class PlainText(Component):
        def __init__(self, text=None):
            super().__init__()
            self.text(text)

        def text(self, text):
            self._add_field("text", text)

    return PlainText()


@pytest.fixture
def button():
    class Button(Component):
        def __init__(self, text=None):
            super().__init__()
            self.text(text)

        def text(self, text):
            self._add_field("text", text)

    return Button()


class TestRequired:
    def test_invalid(self, plain_text):
        plain_text._add_validator("text", Required())
        with pytest.raises(ValidationError) as e:
            plain_text.validate()
        assert "Value is required" in str(e.value)

    def test_valid(self, plain_text):
        plain_text.text("hello alice")
        plain_text._add_validator("text", Required())
        plain_text.validate()


class TestNonEmpty:
    def test_invalid(self, plain_text):
        plain_text.text("")
        plain_text._add_validator("text", NonEmpty())
        with pytest.raises(ValidationError) as e:
            plain_text.validate()
        assert "Value cannot be empty" in str(e.value)

    def test_valid(self, plain_text):
        plain_text.text("hello, alice!")
        plain_text._add_validator("text", NonEmpty())
        plain_text.validate()


class TestMaxLength:
    def test_invalid(self, plain_text):
        plain_text.text("hello, alice!")
        plain_text._add_validator("text", MaxLength(10))
        with pytest.raises(ValidationError) as e:
            plain_text.validate()
        assert "Length must be less or equal 10" in str(e.value)

    def test_valid(self, plain_text):
        plain_text.text("hello, alice!")
        plain_text._add_validator("text", MaxLength(13))
        plain_text.validate()


class TestTyped:
    def test_invalid(self, button, plain_text):
        button.text(123)
        button._add_validator("text", Typed(str, type(plain_text)))
        with pytest.raises(ValidationError) as e:
            button.validate()
        assert "Expected types 'str, PlainText', got 'int'" in str(e.value)

    def test_valid(self, button, plain_text):
        button.text("click me")
        button._add_validator("text", Typed(str, type(plain_text)))
        button.validate()


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
