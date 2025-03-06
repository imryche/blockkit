import pytest

from blockkit.core import (
    Button,
    Component,
    ComponentValidationError,
    Confirm,
    ConversationFilter,
    DispatchActionConfig,
    Either,
    FieldValidationError,
    MarkdownText,
    MaxLength,
    NonEmpty,
    Option,
    OptionGroup,
    PlainText,
    Required,
    Text,
    Typed,
    Values,
)


@pytest.fixture
def plain_text():
    class PlainText(Component):
        def __init__(self, text=None):
            super().__init__()
            self.text(text)

        def text(self, text):
            self._add_field("text", text)
            return self

    return PlainText()


@pytest.fixture
def button():
    class Button(Component):
        def __init__(self, text=None):
            super().__init__()
            self.text(text)

        def text(self, text):
            self._add_field("text", text)
            return self

    return Button()


@pytest.fixture
def conversation_filter():
    class ConversationFilter(Component):
        def __init__(self, include=None, exclude_bot_users=None):
            super().__init__()
            self.include(include)
            self.exclude_bot_users(exclude_bot_users)

        def include(self, include):
            self._add_field("include", include)
            return self

        def exclude_bot_users(self, exclude_bot_users):
            self._add_field("exclude_bot_users", exclude_bot_users)
            return self

    return ConversationFilter()


class TestRequired:
    def test_invalid(self, plain_text):
        plain_text._add_validator(Required(), field_name="text")
        with pytest.raises(FieldValidationError) as e:
            plain_text.validate()
        assert "Value is required" in str(e.value)

    def test_valid(self, plain_text):
        plain_text.text("hello alice")
        plain_text._add_validator(Required(), field_name="text")
        plain_text.validate()


class TestNonEmpty:
    def test_invalid(self, plain_text):
        plain_text.text("")
        plain_text._add_validator(NonEmpty(), field_name="text")
        with pytest.raises(FieldValidationError) as e:
            plain_text.validate()
        assert "Value cannot be empty" in str(e.value)

    def test_valid(self, plain_text):
        plain_text.text("hello, alice!")
        plain_text._add_validator(NonEmpty(), field_name="text")
        plain_text.validate()


class TestMaxLength:
    def test_invalid(self, plain_text):
        plain_text.text("hello, alice!")
        plain_text._add_validator(MaxLength(10), field_name="text")
        with pytest.raises(FieldValidationError) as e:
            plain_text.validate()
        assert "Length must be less or equal 10" in str(e.value)

    def test_valid(self, plain_text):
        plain_text.text("hello, alice!")
        plain_text._add_validator(MaxLength(13), field_name="text")
        plain_text.validate()


class TestValues:
    def test_invalid_single(self, plain_text):
        plain_text.text("hello, charlie!")
        plain_text._add_validator(
            Values("hello, alice!", "hello, bob!"), field_name="text"
        )
        with pytest.raises(FieldValidationError) as e:
            plain_text.validate()
        assert (
            "Expected values 'hello, alice!', 'hello, bob!', got 'hello, charlie!'"
            in str(e.value)
        )

    def test_valid_single(self, plain_text):
        plain_text.text("hello, alice!")
        plain_text._add_validator(Values("hello, alice!"), field_name="text")
        plain_text.validate()

    def test_invalid_multi(self, conversation_filter):
        conversation_filter.include(["im", "external"])
        conversation_filter._add_validator(
            Values("im", "mpim", "private", "public"), field_name="include"
        )
        with pytest.raises(FieldValidationError) as e:
            conversation_filter.validate()
        assert (
            "Expected values 'im', 'mpim', 'private', 'public', "
            "got unexpected 'external'" in str(e.value)
        )

    def test_valid_multi(self, conversation_filter):
        conversation_filter.include(["private", "public"])
        conversation_filter._add_validator(
            Values("im", "mpim", "private", "public"), field_name="include"
        )
        conversation_filter.validate()


class TestTyped:
    def test_invalid_basic(self, button, plain_text):
        button.text(123)
        button._add_validator(Typed(str, type(plain_text)), field_name="text")
        with pytest.raises(FieldValidationError) as e:
            button.validate()
        assert "Expected types 'str', 'PlainText', got 'int'" in str(e.value)

    def test_valid_basic(self, button, plain_text):
        button.text("click me")
        button._add_validator(Typed(str, type(plain_text)), field_name="text")
        button.validate()

    def test_invalid_list(self, conversation_filter):
        conversation_filter.include(["im", 123])
        conversation_filter._add_validator(Typed(str), field_name="include")
        with pytest.raises(FieldValidationError) as e:
            conversation_filter.validate()
        assert "Expected type 'str', got 'int'" in str(e.value)

    def test_valid_list(self, conversation_filter):
        conversation_filter.include(["im", "public"])
        conversation_filter._add_validator(Typed(str), field_name="include")
        conversation_filter.validate()


class TestEither:
    def test_invalid(self, conversation_filter):
        conversation_filter._add_validator(Either("include", "exclude_bot_users"))
        with pytest.raises(ComponentValidationError) as e:
            conversation_filter.validate()
        assert (
            "At least one of the following fields is required "
            "'include', 'exclude_bot_users'" in str(e.value)
        )

    def test_valid(self, conversation_filter):
        conversation_filter.include(["private", "public"])
        conversation_filter.validate()


class TestConfirm:
    def test_builds(self):
        want = {
            "title": {
                "type": "plain_text",
                "text": "Please confirm",
            },
            "text": {
                "type": "plain_text",
                "text": "Proceed?",
            },
            "confirm": {
                "type": "plain_text",
                "text": "Yes",
            },
            "deny": {
                "type": "plain_text",
                "text": "No",
            },
            "style": "danger",
        }

        got = Confirm(
            title=PlainText(text="Please confirm"),
            text=PlainText(text="Proceed?"),
            confirm=PlainText(text="Yes"),
            deny=PlainText(text="No"),
            style="danger",
        ).build()
        assert got == want

        got = Confirm(
            title="Please confirm",
            text="Proceed?",
            confirm="Yes",
            deny="No",
            style="danger",
        ).build()
        assert got == want

        got = (
            Confirm()
            .title("Please confirm")
            .text("Proceed?")
            .confirm("Yes")
            .deny("No")
            .style("danger")
            .build()
        )
        assert got == want


class TestConversationFilter:
    def test_builds(self):
        want = {
            "include": ["public", "mpim"],
            "exclude_external_shared_channels": True,
            "exclude_bot_users": True,
        }

        got = ConversationFilter(
            include=["public", "mpim"],
            exclude_external_shared_channels=True,
            exclude_bot_users=True,
        ).build()
        assert got == want

        got = (
            ConversationFilter()
            .include(["public", "mpim"])
            .exclude_bot_users()
            .exclude_external_shared_channels()
            .build()
        )
        assert got == want


class TestDispatchActionConfig:
    def test_builds(self):
        want = {
            "trigger_actions_on": [
                "on_character_entered",
            ]
        }

        got = DispatchActionConfig(
            trigger_actions_on=["on_character_entered"],
        ).build()
        assert got == want

        got = (
            DispatchActionConfig()
            .trigger_actions_on(
                ["on_character_entered"],
            )
            .build()
        )
        assert got == want


class TestOption:
    def test_builds(self):
        want = {
            "text": {
                "type": "plain_text",
                "text": "Option 1",
            },
            "value": "option_1",
            "description": {
                "type": "plain_text",
                "text": "This is option 1",
            },
            "url": "https://example.com",
        }

        got = Option(
            text="Option 1",
            value="option_1",
            description="This is option 1",
            url="https://example.com",
        ).build()
        assert got == want

        got = (
            Option()
            .text("Option 1")
            .value("option_1")
            .description("This is option 1")
            .url("https://example.com")
            .build()
        )
        assert got == want


class TestOptionGroup:
    def test_builds(self):
        want = {
            "label": {
                "type": "plain_text",
                "text": "Options",
            },
            "options": [
                {
                    "text": {"type": "plain_text", "text": "Option 1"},
                    "value": "option_1",
                },
                {
                    "text": {"type": "plain_text", "text": "Option 2"},
                    "value": "option_2",
                },
            ],
        }

        got = OptionGroup(
            label="Options",
            options=[
                Option(text="Option 1", value="option_1"),
                Option(text="Option 2", value="option_2"),
            ],
        ).build()
        assert got == want

        got = (
            OptionGroup()
            .label("Options")
            .options(
                Option(text="Option 1", value="option_1"),
                Option(text="Option 2", value="option_2"),
            )
        ).build()
        assert got == want

        got = (
            OptionGroup()
            .label("Options")
            .add_option(Option(text="Option 1", value="option_1"))
            .add_option(Option(text="Option 2", value="option_2"))
        ).build()
        assert got == want


class TestText:
    def test_plain_text(self):
        want = {
            "type": "plain_text",
            "text": "hello, alice!",
            "emoji": True,
        }
        got = Text("hello, alice!", emoji=True).build()
        assert got == want

    def test_mrkdwn_text(self):
        want = {
            "type": "mrkdwn",
            "text": "_hello, alice!_",
            "verbatim": True,
        }
        got = Text("_hello, alice!_", verbatim=True).build()
        assert got == want


class TestMarkdownText:
    def test_builds(self):
        want = {"type": "mrkdwn", "text": "hello alice!", "verbatim": True}

        got = MarkdownText("hello alice!", verbatim=True).build()
        assert got == want

        got = MarkdownText().text("hello alice!").verbatim().build()
        assert got == want


class TestButton:
    def test_builds(self):
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
