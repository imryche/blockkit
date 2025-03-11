import pytest

from blockkit.core import (
    ComponentValidationError,
    Confirm,
    ConversationFilter,
    DispatchActionConfig,
    FieldValidationError,
    Option,
    OptionGroup,
    Text,
)


class TestRequired:
    def test_invalid(self):
        with pytest.raises(FieldValidationError) as e:
            Text().validate()
        assert "Value is required" in str(e.value)

    def test_valid(self):
        Text("hello, alice!").validate()


class TestPlain:
    def test_invalid(self):
        with pytest.raises(FieldValidationError) as e:
            Confirm(title="title", confirm="confirm", deny="deny").text(
                Text("Click me").type(Text.MD)
            ).validate()
        assert "Only plain_text is allowed" in str(e)

    def test_valid(self):
        Confirm(title="title", confirm="confirm", deny="deny").text(
            Text("Click me").type(Text.PLAIN)
        ).validate()


class TestLength:
    def test_invalid_upper(self):
        with pytest.raises(FieldValidationError) as e:
            Text("hello, alice!" * 300).validate()
        assert "Length must be between 1 and 3000" in str(e.value)

    def test_invalid_lower(self):
        with pytest.raises(FieldValidationError) as e:
            Text("").validate()
        assert "Length must be between 1 and 3000" in str(e.value)

    def test_valid(self):
        Text("hello, alice!").validate()


class TestValues:
    def test_invalid_single(self):
        with pytest.raises(FieldValidationError) as e:
            Confirm(title="title", text="text", confirm="confirm", deny="deny").style(
                "warning"
            ).validate()
        assert "Expected values 'primary', 'danger', got 'warning'" in str(e.value)

    def test_valid_single(self):
        Confirm(title="title", text="text", confirm="confirm", deny="deny").style(
            "primary"
        ).validate()

    def test_invalid_multi(self):
        with pytest.raises(FieldValidationError) as e:
            ConversationFilter(include=["im", "external"]).validate()
        assert (
            "Expected values 'im', 'mpim', 'private', 'public', "
            "got unexpected 'external'" in str(e.value)
        )

    def test_valid_multi(self):
        ConversationFilter(include=["private", "public"]).validate()


class TestTyped:
    def test_invalid_basic(self):
        with pytest.raises(FieldValidationError) as e:
            Text(123).validate()
        assert "Expected type 'str', got 'int'" in str(e.value)

    def test_valid_basic(self):
        Text("hello, alice!").validate()

    def test_invalid_list(self):
        with pytest.raises(FieldValidationError) as e:
            ConversationFilter(include=["im", 123]).validate()
        assert "Expected type 'str', got 'int'" in str(e.value)

    def test_valid_list(self):
        ConversationFilter(include=["im", "public"]).validate()


class TestEither:
    def test_invalid(self):
        with pytest.raises(ComponentValidationError) as e:
            ConversationFilter().validate()
        assert (
            "At least one of the following fields is required "
            "'include', 'exclude_bot_users', 'exclude_external_shared_channels'"
            in str(e.value)
        )

    def test_valid(self):
        ConversationFilter(include=["private", "public"]).validate()


class TestOnlyIf:
    def test_invalid(self):
        with pytest.raises(ComponentValidationError) as e:
            Text("hello, alice!", verbatim=True).type(Text.PLAIN).validate()
        assert "'verbatim' is only allowed when 'type' is 'mrkdwn'" in str(e)

        with pytest.raises(ComponentValidationError) as e:
            Text("_hello, alice!_", emoji=True).type(Text.MD).validate()
        assert "'emoji' is only allowed when 'type' is 'plain_text'" in str(e)

    def test_valid(self):
        Text("hello, alice!", emoji=True).type(Text.PLAIN).validate()
        Text("_hello, alice!_", verbatim=True).type(Text.MD).validate()


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
            title=Text(text="Please confirm"),
            text=Text(text="Proceed?"),
            confirm=Text(text="Yes"),
            deny=Text(text="No"),
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

        got = Text().text("hello, alice!").emoji().build()
        assert got == want

    def test_mrkdwn_text(self):
        want = {
            "type": "mrkdwn",
            "text": "_hello, alice!_",
            "verbatim": True,
        }

        got = Text("_hello, alice!_", verbatim=True).build()
        assert got == want

        got = Text().text("_hello, alice!_").verbatim().build()
        assert got == want


# class TestButton:
#     def test_builds(self):
#         want = {
#             "type": "button",
#             "text": {"type": "plain_text", "text": "Click me"},
#             "action_id": "clicked",
#             "value": "1",
#             "style": "primary",
#         }
#
#         got = Button(
#             "Click me",
#             action_id="clicked",
#             value="1",
#             style="primary",
#         ).build()
#         assert got == want
#
#         got = (
#             Button()
#             .text("Click me")
#             .action_id("clicked")
#             .value("1")
#             .style("primary")
#             .build()
#         )
#         assert got == want
