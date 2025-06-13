from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest

from blockkit.core import (
    Actions,
    Button,
    ChannelsSelect,
    Checkboxes,
    ComponentValidationError,
    Confirm,
    Context,
    ConversationFilter,
    ConversationsSelect,
    DatePicker,
    DatetimePicker,
    DispatchActionConfig,
    Divider,
    EmailInput,
    ExternalSelect,
    FieldValidationError,
    File,
    FileInput,
    Header,
    Home,
    Image,
    ImageEl,
    Input,
    InputParameter,
    Markdown,
    Message,
    Modal,
    MultiChannelsSelect,
    MultiConversationsSelect,
    MultiExternalSelect,
    MultiStaticSelect,
    MultiUsersSelect,
    NumberInput,
    Option,
    OptionGroup,
    Overflow,
    PlainTextInput,
    RadioButtons,
    RichBroadcastEl,
    RichChannelEl,
    RichColorEl,
    RichDateEl,
    RichEmojiEl,
    RichLinkEl,
    RichStyle,
    RichText,
    RichTextEl,
    RichTextInput,
    RichTextList,
    RichTextPreformatted,
    RichTextQuote,
    RichTextSection,
    RichUserEl,
    RichUserGroupEl,
    Section,
    SlackFile,
    StaticSelect,
    Text,
    TimePicker,
    Trigger,
    UrlInput,
    UsersSelect,
    Video,
    Workflow,
    WorkflowButton,
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


class TextHexColor:
    def test_invalid(self):
        with pytest.raises(FieldValidationError) as e:
            RichColorEl(value="#F405G3").validate()
        assert "Invalid HEX color, got #F405G3" in str(e.value)

    def test_valid(self):
        RichColorEl(value="#F405B3").validate()


class TestStrings:
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


class TestInts:
    def test_invalid(self):
        with pytest.raises(FieldValidationError) as e:
            FileInput(max_files=11).validate()
        assert "Value must be between 1 and 10 (got 11)" in str(e)

    def test_valid(self):
        FileInput(max_files=10).validate()


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


class TestOnlyOne:
    def test_invalid(self):
        with pytest.raises(ComponentValidationError) as e:
            SlackFile(
                url="https://files.slack.com/files-pri/T0123456-F0123456/xyz.png",
                id="F123456",
            ).validate()
        assert "Only one of the following fields is required 'url', 'id'" in str(e)

    def test_valid(self):
        SlackFile(id="F123456").validate()


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


class TestWithin:
    def test_invalid(self):
        with pytest.raises(ComponentValidationError) as e:
            RadioButtons(
                options=[
                    Option("Approve", "approve"),
                    Option("Decline", "decline"),
                ],
                initial_option=Option("Deny", "deny"),
            ).validate()
        assert "'initial_option' has items that aren't present in the 'options'" in str(
            e
        )

    def test_valid(self):
        RadioButtons(
            options=[Option("Approve", "approve")],
            initial_option=Option("Approve", "approve"),
        ).validate()


class TestRanging:
    def test_invalid(self):
        with pytest.raises(ComponentValidationError) as e:
            NumberInput(
                is_decimal_allowed=False, initial_value=11, min_value=1, max_value=10
            ).validate()
        assert (
            "'initial_value' value must be less than or equal to '10', got '11'"
            in str(e)
        )

        with pytest.raises(ComponentValidationError) as e:
            NumberInput(
                is_decimal_allowed=False, initial_value=0, min_value=1, max_value=10
            ).validate()
        assert (
            "'initial_value' value must be greater than or equal to '1', got '0'"
            in str(e)
        )

    def test_valid(self):
        NumberInput(
            is_decimal_allowed=False, initial_value=7, min_value=1, max_value=10
        ).validate()


class TestDecimalAllowed:
    def test_invalid(self):
        with pytest.raises(ComponentValidationError) as e:
            NumberInput(
                is_decimal_allowed=False, initial_value=3.0, min_value=1, max_value=10
            ).validate()
        assert "'initial_value' decimal values are not allowed, got '3.0'" in str(e)

        with pytest.raises(ComponentValidationError) as e:
            NumberInput(
                is_decimal_allowed=False, initial_value=3, min_value=1.0, max_value=10
            ).validate()
        assert "'min_value' decimal values are not allowed, got '1.0'" in str(e)

        with pytest.raises(ComponentValidationError) as e:
            NumberInput(
                is_decimal_allowed=False, initial_value=3, min_value=1, max_value=10.0
            ).validate()
        assert "'max_value' decimal values are not allowed, got '10.0'" in str(e)


class TestStyledCorrectly:
    def test_invalid(self):
        with pytest.raises(ComponentValidationError) as e:
            RichLinkEl(
                url="https://wonderland.com",
                style=RichStyle(highlight=True),
            ).validate()
        assert (
            "'highlight', 'client_highlight', 'unlink' styles are not allowed" in str(e)
        )

        with pytest.raises(ComponentValidationError) as e:
            RichChannelEl(
                channel_id="C123456789",
                style=RichStyle(code=True),
            ).validate()
        assert "'code' style is not allowed" in str(e)

    def test_valid(self):
        RichLinkEl(
            url="https://wonderland.com",
            style=RichStyle(code=True),
        ).validate()

        RichChannelEl(
            channel_id="C123456789",
            style=RichStyle(highlight=True),
        ).validate()


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


class TestWorkflow:
    def test_builds(self):
        want = {
            "trigger": {
                "url": "https://slack.com/shortcuts/Ft0123ABC456/321zyx",
                "customizable_input_parameters": [
                    {"name": "input_parameter_a", "value": "Value for input param A"},
                    {"name": "input_parameter_b", "value": "Value for input param B"},
                ],
            }
        }

        got = Workflow(
            trigger=Trigger(
                url="https://slack.com/shortcuts/Ft0123ABC456/321zyx",
                customizable_input_parameters=[
                    InputParameter(
                        name="input_parameter_a", value="Value for input param A"
                    ),
                    InputParameter(
                        name="input_parameter_b", value="Value for input param B"
                    ),
                ],
            )
        ).build()
        assert got == want

        got = (
            Workflow()
            .trigger(
                Trigger()
                .url("https://slack.com/shortcuts/Ft0123ABC456/321zyx")
                .add_input_parameter(
                    InputParameter(
                        name="input_parameter_a", value="Value for input param A"
                    )
                )
                .add_input_parameter(
                    InputParameter(
                        name="input_parameter_b", value="Value for input param B"
                    )
                )
            )
            .build()
        )
        assert got == want


class TestSlackFile:
    def test_builds(self):
        want = {"url": "https://files.slack.com/files-pri/T0123456-F0123456/xyz.png"}
        got = SlackFile(
            url="https://files.slack.com/files-pri/T0123456-F0123456/xyz.png"
        ).build()
        assert got == want

        got = (
            SlackFile()
            .url("https://files.slack.com/files-pri/T0123456-F0123456/xyz.png")
            .build()
        )
        assert got == want

        want = {"id": "F0123456"}
        got = SlackFile(id="F0123456").build()
        assert got == want

        got = SlackFile().id("F0123456").build()
        assert got == want


class TestButton:
    def test_builds(self):
        want = {
            "type": "button",
            "text": {"type": "plain_text", "text": "Click me"},
            "action_id": "clicked",
            "value": "1",
            "style": "primary",
            "confirm": {
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
            },
            "accessibility_label": "Click me",
        }

        got = Button(
            "Click me",
            action_id="clicked",
            value="1",
            style="primary",
            confirm=Confirm(
                title="Please confirm",
                text="Proceed?",
                confirm="Yes",
                deny="No",
            ),
            accessibility_label="Click me",
        ).build()
        assert got == want

        got = (
            Button()
            .text("Click me")
            .action_id("clicked")
            .value("1")
            .style("primary")
            .confirm(
                Confirm(
                    title="Please confirm",
                    text="Proceed?",
                    confirm="Yes",
                    deny="No",
                )
            )
            .accessibility_label("Click me")
            .build()
        )
        assert got == want


class TestCheckboxes:
    def test_builds(self):
        want = {
            "type": "checkboxes",
            "action_id": "checkboxes_action",
            "options": [
                {
                    "value": "option_1",
                    "text": {"type": "plain_text", "text": "Option 1"},
                },
                {
                    "value": "option_2",
                    "text": {"type": "plain_text", "text": "Option 2"},
                    "description": {
                        "type": "mrkdwn",
                        "text": "*A description of option two*",
                    },
                },
            ],
            "initial_options": [
                {
                    "value": "option_1",
                    "text": {"type": "plain_text", "text": "Option 1"},
                }
            ],
            "confirm": {
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
            },
            "focus_on_load": True,
        }
        got = Checkboxes(
            action_id="checkboxes_action",
            initial_options=[Option(text="Option 1", value="option_1")],
            options=[
                Option(text="Option 1", value="option_1"),
                Option(
                    text="Option 2",
                    description=Text("*A description of option two*"),
                    value="option_2",
                ),
            ],
            confirm=Confirm(
                title="Please confirm",
                text="Proceed?",
                confirm="Yes",
                deny="No",
            ),
            focus_on_load=True,
        ).build()
        assert got == want

        got = (
            Checkboxes()
            .action_id("checkboxes_action")
            .add_initial_option(Option(text="Option 1", value="option_1"))
            .add_option(
                Option(text="Option 1", value="option_1"),
            )
            .add_option(
                Option(
                    text="Option 2",
                    description=Text("*A description of option two*"),
                    value="option_2",
                ),
            )
            .confirm(
                Confirm(
                    title="Please confirm",
                    text="Proceed?",
                    confirm="Yes",
                    deny="No",
                )
            )
            .focus_on_load()
            .build()
        )
        assert got == want


class TestDatePicker:
    def test_builds(self):
        want = {
            "type": "datepicker",
            "action_id": "datepicker_action",
            "initial_date": "1990-04-28",
            "confirm": {
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
            },
            "focus_on_load": True,
            "placeholder": {
                "type": "plain_text",
                "text": "Select a date",
            },
        }

        got = DatePicker(
            action_id="datepicker_action",
            initial_date=date(1990, 4, 28),
            confirm=Confirm(
                title="Please confirm",
                text="Proceed?",
                confirm="Yes",
                deny="No",
            ),
            focus_on_load=True,
            placeholder="Select a date",
        ).build()
        assert got == want

        got = (
            DatePicker()
            .action_id("datepicker_action")
            .initial_date("1990-04-28")
            .confirm(
                Confirm(
                    title="Please confirm",
                    text="Proceed?",
                    confirm="Yes",
                    deny="No",
                )
            )
            .focus_on_load()
            .placeholder("Select a date")
            .build()
        )
        assert got == want


class TestDatetimePicker:
    def test_builds(self):
        want = {
            "type": "datetimepicker",
            "action_id": "datetimepicker_action",
            "initial_date_time": 1628633820,
            "confirm": {
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
            },
            "placeholder": {
                "type": "plain_text",
                "text": "Select a date",
            },
        }

        got = DatetimePicker(
            action_id="datetimepicker_action",
            initial_date_time=datetime.fromtimestamp(1628633820),
            confirm=Confirm(
                title="Please confirm",
                text="Proceed?",
                confirm="Yes",
                deny="No",
            ),
            placeholder="Select a date",
        ).build()
        assert got == want

        got = (
            DatetimePicker()
            .action_id("datetimepicker_action")
            .initial_date_time(1628633820)
            .confirm(
                Confirm(
                    title="Please confirm",
                    text="Proceed?",
                    confirm="Yes",
                    deny="No",
                )
            )
            .placeholder("Select a date")
            .build()
        )
        assert got == want


class TestEmailInput:
    def test_builds(self):
        want = {
            "type": "email_text_input",
            "action_id": "email_text_input_action",
            "initial_value": "alice@wonderland.com",
            "dispatch_action_config": {
                "trigger_actions_on": [
                    "on_character_entered",
                ]
            },
            "focus_on_load": True,
            "placeholder": {
                "type": "plain_text",
                "text": "Select an email",
            },
        }

        got = EmailInput(
            action_id="email_text_input_action",
            initial_value="alice@wonderland.com",
            dispatch_action_config=DispatchActionConfig(
                trigger_actions_on=["on_character_entered"]
            ),
            focus_on_load=True,
            placeholder="Select an email",
        ).build()
        assert got == want

        got = (
            EmailInput()
            .action_id("email_text_input_action")
            .initial_value("alice@wonderland.com")
            .dispatch_action_config(
                DispatchActionConfig(trigger_actions_on=["on_character_entered"])
            )
            .focus_on_load()
            .placeholder("Select an email")
            .build()
        )
        assert got == want


class TestFileInput:
    def test_builds(self):
        want = {
            "type": "file_input",
            "action_id": "file_input_action",
            "filetypes": ["csv", "yaml"],
            "max_files": 1,
        }

        got = FileInput(
            action_id="file_input_action",
            filetypes=["csv", "yaml"],
            max_files=1,
        ).build()
        assert got == want

        got = (
            FileInput()
            .action_id("file_input_action")
            .filetypes("csv", "yaml")
            .max_files(1)
            .build()
        )
        assert got == want


class TestImageEl:
    def test_builds(self):
        want = {
            "type": "image",
            "alt_text": "alice in wonderland",
            "image_url": "https://wonderland.com/static/alice.png",
        }

        got = ImageEl(
            alt_text="alice in wonderland",
            image_url="https://wonderland.com/static/alice.png",
        ).build()
        assert got == want

        got = (
            ImageEl()
            .alt_text("alice in wonderland")
            .image_url("https://wonderland.com/static/alice.png")
            .build()
        )
        assert got == want

        want = {
            "type": "image",
            "alt_text": "alice in wonderland",
            "slack_file": {"id": "F123456"},
        }

        got = ImageEl(
            alt_text="alice in wonderland",
            slack_file=SlackFile(id="F123456"),
        ).build()
        assert got == want

        got = (
            ImageEl()
            .alt_text("alice in wonderland")
            .slack_file(SlackFile(id="F123456"))
            .build()
        )
        assert got == want


class TestMultiStaticSelect:
    def test_builds_options(self):
        want = {
            "type": "multi_static_select",
            "action_id": "multi_static_select_action",
            "options": [
                {
                    "text": {
                        "type": "plain_text",
                        "text": "Option 1",
                    },
                    "value": "option_1",
                },
                {
                    "text": {
                        "type": "plain_text",
                        "text": "Option 2",
                    },
                    "value": "option_2",
                },
            ],
            "initial_options": [
                {
                    "text": {
                        "type": "plain_text",
                        "text": "Option 1",
                    },
                    "value": "option_1",
                },
            ],
            "confirm": {
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
            },
            "max_selected_items": 2,
            "focus_on_load": True,
            "placeholder": {
                "type": "plain_text",
                "text": "Select items",
            },
        }

        got = MultiStaticSelect(
            action_id="multi_static_select_action",
            options=[
                Option(text="Option 1", value="option_1"),
                Option(text="Option 2", value="option_2"),
            ],
            initial_options=[Option(text="Option 1", value="option_1")],
            confirm=Confirm(
                title="Please confirm",
                text="Proceed?",
                confirm="Yes",
                deny="No",
            ),
            max_selected_items=2,
            focus_on_load=True,
            placeholder="Select items",
        ).build()
        assert got == want

        got = (
            MultiStaticSelect()
            .action_id("multi_static_select_action")
            .add_option(Option(text="Option 1", value="option_1"))
            .add_option(Option(text="Option 2", value="option_2"))
            .add_initial_option(Option(text="Option 1", value="option_1"))
            .confirm(
                Confirm(
                    title="Please confirm",
                    text="Proceed?",
                    confirm="Yes",
                    deny="No",
                )
            )
            .max_selected_items(2)
            .focus_on_load()
            .placeholder("Select items")
            .build()
        )
        assert got == want

    def test_builds_option_groups(self):
        want = {
            "type": "multi_static_select",
            "action_id": "multi_static_select_action",
            "option_groups": [
                {
                    "label": {
                        "type": "plain_text",
                        "text": "Group 1",
                    },
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "Option 1"},
                            "value": "option_1",
                        }
                    ],
                },
                {
                    "label": {
                        "type": "plain_text",
                        "text": "Group 2",
                    },
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "Option 2"},
                            "value": "option_2",
                        }
                    ],
                },
            ],
            "initial_options": [
                {
                    "label": {
                        "type": "plain_text",
                        "text": "Group 1",
                    },
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "Option 1"},
                            "value": "option_1",
                        }
                    ],
                },
            ],
        }
        got = MultiStaticSelect(
            action_id="multi_static_select_action",
            option_groups=[
                OptionGroup(
                    label="Group 1", options=[Option(text="Option 1", value="option_1")]
                ),
                OptionGroup(
                    label="Group 2", options=[Option(text="Option 2", value="option_2")]
                ),
            ],
            initial_options=[
                OptionGroup(
                    label="Group 1", options=[Option(text="Option 1", value="option_1")]
                )
            ],
        ).build()
        assert got == want

        got = (
            MultiStaticSelect()
            .action_id("multi_static_select_action")
            .add_option_group(
                OptionGroup(
                    label="Group 1", options=[Option(text="Option 1", value="option_1")]
                )
            )
            .add_option_group(
                OptionGroup(
                    label="Group 2", options=[Option(text="Option 2", value="option_2")]
                ),
            )
            .add_initial_option(
                OptionGroup(
                    label="Group 1", options=[Option(text="Option 1", value="option_1")]
                )
            )
            .build()
        )
        assert got == want


class TestMultiExternalSelect:
    def test_builds_options(self):
        want = {
            "type": "multi_external_select",
            "action_id": "multi_external_select_action",
            "min_query_length": 3,
            "initial_options": [
                {
                    "text": {
                        "type": "plain_text",
                        "text": "Option 1",
                    },
                    "value": "option_1",
                },
            ],
            "confirm": {
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
            },
            "max_selected_items": 3,
            "focus_on_load": True,
            "placeholder": {
                "type": "plain_text",
                "text": "Select items",
            },
        }

        got = MultiExternalSelect(
            action_id="multi_external_select_action",
            min_query_length=3,
            initial_options=[Option(text="Option 1", value="option_1")],
            confirm=Confirm(
                title="Please confirm",
                text="Proceed?",
                confirm="Yes",
                deny="No",
            ),
            max_selected_items=3,
            focus_on_load=True,
            placeholder="Select items",
        ).build()
        assert got == want

        got = (
            MultiExternalSelect()
            .action_id("multi_external_select_action")
            .min_query_length(3)
            .add_initial_option(Option(text="Option 1", value="option_1"))
            .confirm(
                Confirm(
                    title="Please confirm",
                    text="Proceed?",
                    confirm="Yes",
                    deny="No",
                )
            )
            .max_selected_items(3)
            .focus_on_load()
            .placeholder("Select items")
            .build()
        )
        assert got == want

    def test_builds_option_groups(self):
        want = {
            "type": "multi_external_select",
            "action_id": "multi_external_select_action",
            "initial_options": [
                {
                    "label": {
                        "type": "plain_text",
                        "text": "Group 1",
                    },
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "Option 1"},
                            "value": "option_1",
                        }
                    ],
                },
            ],
        }

        got = (
            MultiExternalSelect()
            .action_id("multi_external_select_action")
            .add_initial_option(
                OptionGroup(label="Group 1").add_option(
                    Option(text="Option 1", value="option_1")
                )
            )
        ).build()
        assert got == want


class TestMultiUsersSelect:
    def test_builds(self):
        want = {
            "type": "multi_users_select",
            "action_id": "multi_users_select_action",
            "initial_users": ["U02A1B2C3D4", "U1X9Y8Z7W6V", "U5L4K3J2H1G"],
            "confirm": {
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
            },
            "max_selected_items": 3,
            "focus_on_load": True,
            "placeholder": {
                "type": "plain_text",
                "text": "Select users",
            },
        }

        got = MultiUsersSelect(
            action_id="multi_users_select_action",
            initial_users=["U02A1B2C3D4", "U1X9Y8Z7W6V", "U5L4K3J2H1G"],
            confirm=Confirm(
                title="Please confirm",
                text="Proceed?",
                confirm="Yes",
                deny="No",
            ),
            max_selected_items=3,
            focus_on_load=True,
            placeholder="Select users",
        ).build()
        assert got == want

        got = (
            MultiUsersSelect()
            .action_id("multi_users_select_action")
            .add_initial_user("U02A1B2C3D4")
            .add_initial_user("U1X9Y8Z7W6V")
            .add_initial_user("U5L4K3J2H1G")
            .confirm(
                Confirm(
                    title="Please confirm",
                    text="Proceed?",
                    confirm="Yes",
                    deny="No",
                )
            )
            .max_selected_items(3)
            .focus_on_load()
            .placeholder("Select users")
            .build()
        )
        assert got == want


class TestMultiConversationsSelect:
    def test_builds(self):
        want = {
            "type": "multi_conversations_select",
            "action_id": "multi_conversations_select_action",
            "initial_conversations": ["C01AB2CD3EF", "C9X8Y7Z6W5V", "C4T3R2Q1P0O"],
            "default_to_current_conversation": True,
            "confirm": {
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
            },
            "max_selected_items": 3,
            "filter": {
                "include": ["public", "private"],
            },
            "focus_on_load": True,
            "placeholder": {
                "type": "plain_text",
                "text": "Select conversations",
            },
        }

        got = MultiConversationsSelect(
            action_id="multi_conversations_select_action",
            initial_conversations=["C01AB2CD3EF", "C9X8Y7Z6W5V", "C4T3R2Q1P0O"],
            default_to_current_conversation=True,
            confirm=Confirm(
                title="Please confirm",
                text="Proceed?",
                confirm="Yes",
                deny="No",
            ),
            filter=ConversationFilter(include=["public", "private"]),
            max_selected_items=3,
            focus_on_load=True,
            placeholder="Select conversations",
        ).build()
        assert got == want

        got = (
            MultiConversationsSelect()
            .action_id("multi_conversations_select_action")
            .add_initial_conversation("C01AB2CD3EF")
            .add_initial_conversation("C9X8Y7Z6W5V")
            .add_initial_conversation("C4T3R2Q1P0O")
            .default_to_current_conversation()
            .confirm(
                Confirm(
                    title="Please confirm",
                    text="Proceed?",
                    confirm="Yes",
                    deny="No",
                )
            )
            .filter(ConversationFilter(include=["public", "private"]))
            .max_selected_items(3)
            .focus_on_load()
            .placeholder("Select conversations")
            .build()
        )
        assert got == want


class TestMultiChannelsSelect:
    def test_builds(self):
        want = {
            "type": "multi_channels_select",
            "action_id": "multi_channels_select_action",
            "initial_channels": ["C01AB2CD3EF", "C9X8Y7Z6W5V", "C4T3R2Q1P0O"],
            "confirm": {
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
            },
            "max_selected_items": 3,
            "focus_on_load": True,
            "placeholder": {
                "type": "plain_text",
                "text": "Select channels",
            },
        }

        got = MultiChannelsSelect(
            action_id="multi_channels_select_action",
            initial_channels=["C01AB2CD3EF", "C9X8Y7Z6W5V", "C4T3R2Q1P0O"],
            confirm=Confirm(
                title="Please confirm",
                text="Proceed?",
                confirm="Yes",
                deny="No",
            ),
            max_selected_items=3,
            focus_on_load=True,
            placeholder="Select channels",
        ).build()
        assert got == want

        got = (
            MultiChannelsSelect()
            .action_id("multi_channels_select_action")
            .add_initial_channel("C01AB2CD3EF")
            .add_initial_channel("C9X8Y7Z6W5V")
            .add_initial_channel("C4T3R2Q1P0O")
            .confirm(
                Confirm(
                    title="Please confirm",
                    text="Proceed?",
                    confirm="Yes",
                    deny="No",
                )
            )
            .max_selected_items(3)
            .focus_on_load()
            .placeholder("Select channels")
            .build()
        )
        assert got == want


class TestNumberInput:
    def test_builds(self):
        want = {
            "type": "number_input",
            "is_decimal_allowed": False,
            "action_id": "number_input_action",
            "initial_value": "7",
            "min_value": "1",
            "max_value": "10",
            "dispatch_action_config": {
                "trigger_actions_on": [
                    "on_character_entered",
                ]
            },
            "focus_on_load": True,
            "placeholder": {
                "type": "plain_text",
                "text": "Select a number",
            },
        }

        got = NumberInput(
            is_decimal_allowed=False,
            action_id="number_input_action",
            initial_value=7,
            min_value=1,
            max_value=10,
            dispatch_action_config=DispatchActionConfig(
                trigger_actions_on=["on_character_entered"]
            ),
            focus_on_load=True,
            placeholder="Select a number",
        ).build()
        assert got == want

        got = (
            NumberInput()
            .is_decimal_allowed(False)
            .action_id("number_input_action")
            .initial_value(7)
            .min_value(1)
            .max_value(10)
            .dispatch_action_config(
                DispatchActionConfig(trigger_actions_on=["on_character_entered"])
            )
            .focus_on_load()
            .placeholder("Select a number")
            .build()
        )
        assert got == want


class TestOverflow:
    def test_builds(self):
        want = {
            "type": "overflow",
            "action_id": "overflow_action",
            "options": [
                {
                    "text": {
                        "type": "plain_text",
                        "text": "Option 1",
                    },
                    "value": "option_1",
                },
                {
                    "text": {
                        "type": "plain_text",
                        "text": "Option 2",
                    },
                    "value": "option_2",
                },
            ],
            "confirm": {
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
            },
        }

        got = Overflow(
            action_id="overflow_action",
            options=[
                Option(text="Option 1", value="option_1"),
                Option(text="Option 2", value="option_2"),
            ],
            confirm=Confirm(
                title="Please confirm",
                text="Proceed?",
                confirm="Yes",
                deny="No",
            ),
        ).build()
        assert got == want

        got = (
            Overflow()
            .action_id("overflow_action")
            .add_option(Option(text="Option 1", value="option_1"))
            .add_option(Option(text="Option 2", value="option_2"))
            .confirm(
                Confirm(
                    title="Please confirm",
                    text="Proceed?",
                    confirm="Yes",
                    deny="No",
                )
            )
            .build()
        )
        assert got == want


class TestPlainTextInput:
    def test_builds(self):
        want = {
            "type": "plain_text_input",
            "action_id": "plain_text_input_action",
            "initial_value": "Initial value",
            "multiline": True,
            "min_length": 10,
            "max_length": 2000,
            "dispatch_action_config": {
                "trigger_actions_on": [
                    "on_character_entered",
                ]
            },
            "focus_on_load": True,
            "placeholder": {
                "type": "plain_text",
                "text": "Enter some text",
            },
        }

        got = PlainTextInput(
            action_id="plain_text_input_action",
            initial_value="Initial value",
            multiline=True,
            min_length=10,
            max_length=2000,
            dispatch_action_config=DispatchActionConfig(
                trigger_actions_on=["on_character_entered"]
            ),
            focus_on_load=True,
            placeholder="Enter some text",
        ).build()
        assert got == want

        got = (
            PlainTextInput()
            .action_id("plain_text_input_action")
            .initial_value("Initial value")
            .multiline()
            .min_length(10)
            .max_length(2000)
            .dispatch_action_config(
                DispatchActionConfig(trigger_actions_on=["on_character_entered"])
            )
            .focus_on_load()
            .placeholder("Enter some text")
            .build()
        )
        assert got == want


class TestRadioButtons:
    def test_builds(self):
        want = {
            "type": "radio_buttons",
            "action_id": "radio_buttons_action",
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
            "initial_option": {
                "text": {"type": "plain_text", "text": "Option 1"},
                "value": "option_1",
            },
            "confirm": {
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
            },
            "focus_on_load": True,
        }

        got = RadioButtons(
            action_id="radio_buttons_action",
            options=[
                Option(text="Option 1", value="option_1"),
                Option(text="Option 2", value="option_2"),
            ],
            initial_option=Option(text="Option 1", value="option_1"),
            confirm=Confirm(
                title="Please confirm",
                text="Proceed?",
                confirm="Yes",
                deny="No",
            ),
            focus_on_load=True,
        ).build()
        assert got == want


class TestRichTextInput:
    def test_builds(self):
        want = {
            "type": "rich_text_input",
            "action_id": "rich_text_input_action",
            "initial_value": {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "Curiouser and curiouser!",
                                "style": {
                                    "bold": True,
                                },
                            },
                        ],
                    },
                ],
            },
            "dispatch_action_config": {
                "trigger_actions_on": [
                    "on_character_entered",
                ]
            },
            "focus_on_load": True,
            "placeholder": {
                "type": "plain_text",
                "text": "Enter something",
            },
        }

        got = RichTextInput(
            action_id="rich_text_input_action",
            initial_value=RichText(
                elements=[
                    RichTextSection(
                        elements=[
                            RichTextEl(
                                "Curiouser and curiouser!", style=RichStyle(bold=True)
                            )
                        ]
                    )
                ]
            ),
            dispatch_action_config=DispatchActionConfig(
                trigger_actions_on=["on_character_entered"]
            ),
            focus_on_load=True,
            placeholder="Enter something",
        ).build()
        assert got == want

        got = (
            RichTextInput()
            .action_id("rich_text_input_action")
            .initial_value(
                RichText().add_element(
                    RichTextSection().add_element(
                        RichTextEl()
                        .text("Curiouser and curiouser!")
                        .style(RichStyle().bold())
                    )
                )
            )
            .dispatch_action_config(
                DispatchActionConfig(trigger_actions_on=["on_character_entered"])
            )
            .focus_on_load()
            .placeholder("Enter something")
            .build()
        )
        assert got == want


class TestStaticSelect:
    def test_builds_options(self):
        want = {
            "type": "static_select",
            "action_id": "static_select_action",
            "options": [
                {
                    "text": {
                        "type": "plain_text",
                        "text": "Option 1",
                    },
                    "value": "option_1",
                },
                {
                    "text": {
                        "type": "plain_text",
                        "text": "Option 2",
                    },
                    "value": "option_2",
                },
            ],
            "initial_option": {
                "text": {
                    "type": "plain_text",
                    "text": "Option 1",
                },
                "value": "option_1",
            },
            "confirm": {
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
            },
            "focus_on_load": True,
            "placeholder": {
                "type": "plain_text",
                "text": "Select an item",
            },
        }

        got = StaticSelect(
            action_id="static_select_action",
            options=[
                Option(text="Option 1", value="option_1"),
                Option(text="Option 2", value="option_2"),
            ],
            initial_option=Option(text="Option 1", value="option_1"),
            confirm=Confirm(
                title="Please confirm",
                text="Proceed?",
                confirm="Yes",
                deny="No",
            ),
            focus_on_load=True,
            placeholder="Select an item",
        ).build()
        assert got == want

        got = (
            StaticSelect()
            .action_id("static_select_action")
            .add_option(Option(text="Option 1", value="option_1"))
            .add_option(Option(text="Option 2", value="option_2"))
            .initial_option(Option(text="Option 1", value="option_1"))
            .confirm(
                Confirm(
                    title="Please confirm",
                    text="Proceed?",
                    confirm="Yes",
                    deny="No",
                )
            )
            .focus_on_load()
            .placeholder("Select an item")
            .build()
        )
        assert got == want

    def test_builds_option_groups(self):
        want = {
            "type": "static_select",
            "action_id": "static_select_action",
            "option_groups": [
                {
                    "label": {
                        "type": "plain_text",
                        "text": "Group 1",
                    },
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "Option 1"},
                            "value": "option_1",
                        }
                    ],
                },
                {
                    "label": {
                        "type": "plain_text",
                        "text": "Group 2",
                    },
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "Option 2"},
                            "value": "option_2",
                        }
                    ],
                },
            ],
            "initial_option": {
                "label": {
                    "type": "plain_text",
                    "text": "Group 1",
                },
                "options": [
                    {
                        "text": {"type": "plain_text", "text": "Option 1"},
                        "value": "option_1",
                    }
                ],
            },
        }
        got = StaticSelect(
            action_id="static_select_action",
            option_groups=[
                OptionGroup(
                    label="Group 1", options=[Option(text="Option 1", value="option_1")]
                ),
                OptionGroup(
                    label="Group 2", options=[Option(text="Option 2", value="option_2")]
                ),
            ],
            initial_option=OptionGroup(
                label="Group 1", options=[Option(text="Option 1", value="option_1")]
            ),
        ).build()
        assert got == want

        got = (
            StaticSelect()
            .action_id("static_select_action")
            .add_option_group(
                OptionGroup(
                    label="Group 1", options=[Option(text="Option 1", value="option_1")]
                )
            )
            .add_option_group(
                OptionGroup(
                    label="Group 2", options=[Option(text="Option 2", value="option_2")]
                ),
            )
            .initial_option(
                OptionGroup(
                    label="Group 1", options=[Option(text="Option 1", value="option_1")]
                )
            )
            .build()
        )
        assert got == want


class TestExternalSelect:
    def test_builds_options(self):
        want = {
            "type": "external_select",
            "action_id": "external_select_action",
            "min_query_length": 3,
            "initial_option": {
                "text": {
                    "type": "plain_text",
                    "text": "Option 1",
                },
                "value": "option_1",
            },
            "confirm": {
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
            },
            "focus_on_load": True,
            "placeholder": {
                "type": "plain_text",
                "text": "Select an item",
            },
        }

        got = ExternalSelect(
            action_id="external_select_action",
            min_query_length=3,
            initial_option=Option(text="Option 1", value="option_1"),
            confirm=Confirm(
                title="Please confirm",
                text="Proceed?",
                confirm="Yes",
                deny="No",
            ),
            focus_on_load=True,
            placeholder="Select an item",
        ).build()
        assert got == want

        got = (
            ExternalSelect()
            .action_id("external_select_action")
            .min_query_length(3)
            .initial_option(Option(text="Option 1", value="option_1"))
            .confirm(
                Confirm(
                    title="Please confirm",
                    text="Proceed?",
                    confirm="Yes",
                    deny="No",
                )
            )
            .focus_on_load()
            .placeholder("Select an item")
            .build()
        )
        assert got == want

    def test_builds_option_groups(self):
        want = {
            "type": "external_select",
            "action_id": "external_select_action",
            "initial_option": {
                "label": {
                    "type": "plain_text",
                    "text": "Group 1",
                },
                "options": [
                    {
                        "text": {"type": "plain_text", "text": "Option 1"},
                        "value": "option_1",
                    }
                ],
            },
        }

        got = (
            ExternalSelect()
            .action_id("external_select_action")
            .initial_option(
                OptionGroup(label="Group 1").add_option(
                    Option(text="Option 1", value="option_1")
                )
            )
        ).build()
        assert got == want


class TestUsersSelect:
    def test_builds(self):
        want = {
            "type": "users_select",
            "action_id": "users_select_action",
            "initial_user": "U02A1B2C3D4",
            "confirm": {
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
            },
            "focus_on_load": True,
            "placeholder": {
                "type": "plain_text",
                "text": "Select a user",
            },
        }

        got = UsersSelect(
            action_id="users_select_action",
            initial_user="U02A1B2C3D4",
            confirm=Confirm(
                title="Please confirm",
                text="Proceed?",
                confirm="Yes",
                deny="No",
            ),
            focus_on_load=True,
            placeholder="Select a user",
        ).build()
        assert got == want

        got = (
            UsersSelect()
            .action_id("users_select_action")
            .initial_user("U02A1B2C3D4")
            .confirm(
                Confirm(
                    title="Please confirm",
                    text="Proceed?",
                    confirm="Yes",
                    deny="No",
                )
            )
            .focus_on_load()
            .placeholder("Select a user")
            .build()
        )
        assert got == want


class TestConversationsSelect:
    def test_builds(self):
        want = {
            "type": "conversations_select",
            "action_id": "conversations_select_action",
            "initial_conversation": "C01AB2CD3EF",
            "default_to_current_conversation": True,
            "confirm": {
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
            },
            "response_url_enabled": True,
            "filter": {
                "include": ["public", "private"],
            },
            "focus_on_load": True,
            "placeholder": {
                "type": "plain_text",
                "text": "Select a conversation",
            },
        }

        got = ConversationsSelect(
            action_id="conversations_select_action",
            initial_conversation="C01AB2CD3EF",
            default_to_current_conversation=True,
            confirm=Confirm(
                title="Please confirm",
                text="Proceed?",
                confirm="Yes",
                deny="No",
            ),
            response_url_enabled=True,
            filter=ConversationFilter(include=["public", "private"]),
            focus_on_load=True,
            placeholder="Select a conversation",
        ).build()
        assert got == want

        got = (
            ConversationsSelect()
            .action_id("conversations_select_action")
            .initial_conversation("C01AB2CD3EF")
            .default_to_current_conversation()
            .confirm(
                Confirm(
                    title="Please confirm",
                    text="Proceed?",
                    confirm="Yes",
                    deny="No",
                )
            )
            .response_url_enabled()
            .filter(ConversationFilter(include=["public", "private"]))
            .focus_on_load()
            .placeholder("Select a conversation")
            .build()
        )
        assert got == want


class TestChannelsSelect:
    def test_builds(self):
        want = {
            "type": "channels_select",
            "action_id": "channels_select_action",
            "initial_channel": "C01AB2CD3EF",
            "confirm": {
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
            },
            "response_url_enabled": True,
            "focus_on_load": True,
            "placeholder": {
                "type": "plain_text",
                "text": "Select a channel",
            },
        }

        got = ChannelsSelect(
            action_id="channels_select_action",
            initial_channel="C01AB2CD3EF",
            confirm=Confirm(
                title="Please confirm",
                text="Proceed?",
                confirm="Yes",
                deny="No",
            ),
            response_url_enabled=True,
            focus_on_load=True,
            placeholder="Select a channel",
        ).build()
        assert got == want

        got = (
            ChannelsSelect()
            .action_id("channels_select_action")
            .initial_channel("C01AB2CD3EF")
            .confirm(
                Confirm(
                    title="Please confirm",
                    text="Proceed?",
                    confirm="Yes",
                    deny="No",
                )
            )
            .response_url_enabled()
            .focus_on_load()
            .placeholder("Select a channel")
            .build()
        )
        assert got == want


class TestTimePicker:
    def test_builds(self):
        want = {
            "type": "timepicker",
            "action_id": "timepicker_action",
            "initial_time": "13:00",
            "confirm": {
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
            },
            "focus_on_load": True,
            "placeholder": {
                "type": "plain_text",
                "text": "Select a time",
            },
            "timezone": "Europe/Warsaw",
        }

        got = TimePicker(
            action_id="timepicker_action",
            initial_time="13:00",
            confirm=Confirm(
                title="Please confirm",
                text="Proceed?",
                confirm="Yes",
                deny="No",
            ),
            focus_on_load=True,
            placeholder="Select a time",
            timezone="Europe/Warsaw",
        ).build()
        assert got == want

        got = (
            TimePicker()
            .action_id("timepicker_action")
            .initial_time(time.fromisoformat("13:00:00"))
            .confirm(
                Confirm(
                    title="Please confirm",
                    text="Proceed?",
                    confirm="Yes",
                    deny="No",
                )
            )
            .focus_on_load()
            .placeholder("Select a time")
            .timezone(ZoneInfo("Europe/Warsaw"))
            .build()
        )
        assert got == want


class TestUrlInput:
    def test_builds(self):
        want = {
            "type": "url_text_input",
            "action_id": "url_text_input_action",
            "initial_value": "https://botsignals.co",
            "dispatch_action_config": {
                "trigger_actions_on": [
                    "on_character_entered",
                ]
            },
            "focus_on_load": True,
            "placeholder": {
                "type": "plain_text",
                "text": "Enter a URL",
            },
        }

        got = UrlInput(
            action_id="url_text_input_action",
            initial_value="https://botsignals.co",
            dispatch_action_config=DispatchActionConfig(
                trigger_actions_on=["on_character_entered"]
            ),
            focus_on_load=True,
            placeholder="Enter a URL",
        ).build()
        assert got == want

        got = (
            UrlInput()
            .action_id("url_text_input_action")
            .initial_value("https://botsignals.co")
            .dispatch_action_config(
                DispatchActionConfig(trigger_actions_on=["on_character_entered"])
            )
            .focus_on_load()
            .placeholder("Enter a URL")
            .build()
        )
        assert got == want


class TestWorkflowButton:
    def test_builds(self):
        want = {
            "type": "workflow_button",
            "text": {
                "type": "plain_text",
                "text": "Run workflow",
            },
            "workflow": {
                "trigger": {
                    "url": "https://slack.com/shortcuts/Ft0123ABC456/321zyx",
                    "customizable_input_parameters": [
                        {
                            "name": "input_parameter_a",
                            "value": "Value for input param A",
                        },
                        {
                            "name": "input_parameter_b",
                            "value": "Value for input param B",
                        },
                    ],
                }
            },
            "action_id": "workflow_button_action",
            "style": "primary",
            "accessibility_label": "Run workflow",
        }

        got = WorkflowButton(
            text="Run workflow",
            workflow=Workflow(
                trigger=Trigger(
                    url="https://slack.com/shortcuts/Ft0123ABC456/321zyx",
                    customizable_input_parameters=[
                        InputParameter(
                            name="input_parameter_a", value="Value for input param A"
                        ),
                        InputParameter(
                            name="input_parameter_b", value="Value for input param B"
                        ),
                    ],
                )
            ),
            action_id="workflow_button_action",
            style="primary",
            accessibility_label="Run workflow",
        ).build()
        assert got == want


class TestActions:
    def test_builds(self):
        want = {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click me"},
                    "action_id": "button_action",
                }
            ],
            "block_id": "actions_block",
        }

        got = Actions(
            elements=[
                Button(
                    text="Click me",
                    action_id="button_action",
                ),
            ],
            block_id="actions_block",
        ).build()
        assert got == want

        got = (
            Actions()
            .add_element(
                Button(
                    text="Click me",
                    action_id="button_action",
                )
            )
            .block_id("actions_block")
            .build()
        )
        assert got == want


class TestContext:
    def test_builds(self):
        want = {
            "type": "context",
            "elements": [
                {
                    "type": "image",
                    "alt_text": "alice in wonderland",
                    "image_url": "https://wonderland.com/static/alice.png",
                },
                {
                    "type": "mrkdwn",
                    "text": "*Alice in wonderland*",
                },
            ],
            "block_id": "context_block",
        }

        got = Context(
            elements=[
                ImageEl(
                    alt_text="alice in wonderland",
                    image_url="https://wonderland.com/static/alice.png",
                ),
                Text(text="*Alice in wonderland*"),
            ],
            block_id="context_block",
        ).build()
        assert got == want

        got = (
            Context()
            .add_element(
                ImageEl(
                    alt_text="alice in wonderland",
                    image_url="https://wonderland.com/static/alice.png",
                )
            )
            .add_element(Text(text="*Alice in wonderland*"))
            .block_id("context_block")
            .build()
        )
        assert got == want


class TestDivider:
    def test_builds(self):
        want = {
            "type": "divider",
            "block_id": "divider_block",
        }

        got = Divider(block_id="divider_block").build()
        assert got == want

        got = Divider().block_id("divider_block").build()
        assert got == want


class TestFile:
    def test_builds(self):
        want = {
            "type": "file",
            "external_id": "F123456789",
            "source": "remote",
            "block_id": "file_block",
        }

        got = File(
            external_id="F123456789",
            source="remote",
            block_id="file_block",
        ).build()
        assert got == want

        got = (
            File()
            .external_id("F123456789")
            .source("remote")
            .block_id("file_block")
            .build()
        )
        assert got == want


class TestHeader:
    def test_builds(self):
        want = {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Welcome to Wonderland!",
            },
            "block_id": "header_block",
        }

        got = Header(
            text="Welcome to Wonderland!",
            block_id="header_block",
        ).build()
        assert got == want

        got = Header().text("Welcome to Wonderland!").block_id("header_block").build()
        assert got == want


class TestImage:
    def test_builds(self):
        want = {
            "type": "image",
            "alt_text": "alice in wonderland",
            "image_url": "https://wonderland.com/static/alice.png",
            "title": {
                "type": "plain_text",
                "text": "alice in wonderland",
            },
            "block_id": "image_block",
        }

        got = Image(
            alt_text="alice in wonderland",
            image_url="https://wonderland.com/static/alice.png",
            title="alice in wonderland",
            block_id="image_block",
        ).build()
        assert got == want

        got = (
            Image()
            .alt_text("alice in wonderland")
            .image_url("https://wonderland.com/static/alice.png")
            .title("alice in wonderland")
            .block_id("image_block")
            .build()
        )
        assert got == want


class TestInput:
    def test_builds(self):
        want = {
            "type": "input",
            "label": {
                "type": "plain_text",
                "text": "Who in the world am I?",
            },
            "element": {
                "type": "plain_text_input",
            },
            "dispatch_action": True,
            "hint": {
                "type": "plain_text",
                "text": "She's changing sizes",
            },
            "optional": True,
            "block_id": "input_block",
        }

        got = Input(
            label="Who in the world am I?",
            element=PlainTextInput(),
            dispatch_action=True,
            hint="She's changing sizes",
            optional=True,
            block_id="input_block",
        ).build()
        assert got == want

        got = (
            Input()
            .label("Who in the world am I?")
            .element(PlainTextInput())
            .dispatch_action()
            .hint("She's changing sizes")
            .optional()
            .block_id("input_block")
            .build()
        )
        assert got == want


class TestMarkdown:
    def test_builds(self):
        want = {
            "type": "markdown",
            "text": "**Shrinking, growing, talking to animals "
            "- no wonder she's confused!**",
            "block_id": "markdown_block",
        }

        got = Markdown(
            text="**Shrinking, growing, talking to animals "
            "- no wonder she's confused!**",
            block_id="markdown_block",
        ).build()
        assert got == want

        got = (
            Markdown()
            .text(
                "**Shrinking, growing, talking to animals - no wonder she's confused!**"
            )
            .block_id("markdown_block")
            .build()
        )
        assert got == want


class TestRichStyle:
    def test_builds(self):
        want = {
            "bold": True,
            "italic": True,
            "strike": True,
            "highlight": True,
            "client_highlight": True,
            "unlink": True,
        }

        got = RichStyle(
            bold=True,
            italic=True,
            strike=True,
            highlight=True,
            client_highlight=True,
            unlink=True,
        ).build()
        assert got == want

        got = (
            RichStyle()
            .bold()
            .italic()
            .strike()
            .highlight()
            .client_highlight()
            .unlink()
            .build()
        )
        assert got == want


class TestRichBroadcastEl:
    def test_builds(self):
        want = {
            "type": "broadcast",
            "range": "everyone",
        }

        got = RichBroadcastEl(range="everyone").build()
        assert got == want

        got = RichBroadcastEl().range("everyone").build()
        assert got == want


class TestRichColorEl:
    def test_builds(self):
        want = {
            "type": "color",
            "value": "#F405B3",
        }

        got = RichColorEl(value="#F405B3").build()
        assert got == want

        got = RichColorEl().value("#F405B3").build()
        assert got == want


class TestRichChannelEl:
    def test_builds(self):
        want = {
            "type": "channel",
            "channel_id": "C123456789",
            "style": {
                "bold": True,
            },
        }

        got = RichChannelEl(
            channel_id="C123456789",
            style=RichStyle(bold=True),
        ).build()
        assert got == want

        got = RichChannelEl().channel_id("C123456789").style(RichStyle().bold()).build()
        assert got == want


class TestRichDateEl:
    def test_builds(self):
        want = {
            "type": "date",
            "timestamp": 1747124856,
            "format": "{date_num} at {time}",
            "url": "https://wonderland.com",
            "fallback": "Time won't stand still",
        }

        got = RichDateEl(
            timestamp=1747124856,
            format="{date_num} at {time}",
            url="https://wonderland.com",
            fallback="Time won't stand still",
        ).build()
        assert got == want

        got = (
            RichDateEl()
            .timestamp(datetime.fromtimestamp(1747124856))
            .format("{date_num} at {time}")
            .url("https://wonderland.com")
            .fallback("Time won't stand still")
            .build()
        )
        assert got == want


class TestRichEmojiEl:
    def test_builds(self):
        want = {
            "type": "emoji",
            "name": "rabbit",
            "unicode": "1f407",
        }

        got = RichEmojiEl(name="rabbit", unicode="1f407").build()
        assert got == want

        got = RichEmojiEl().name("rabbit").unicode("1f407").build()
        assert got == want


class TestRichLinkEl:
    def test_builds(self):
        want = {
            "type": "link",
            "url": "https://wonderland.com",
            "text": "wonderland",
            "unsafe": True,
            "style": {
                "italic": True,
            },
        }

        got = RichLinkEl(
            url="https://wonderland.com",
            text="wonderland",
            unsafe=True,
            style=RichStyle(italic=True),
        ).build()
        assert got == want

        got = (
            RichLinkEl()
            .url("https://wonderland.com")
            .text("wonderland")
            .unsafe()
            .style(RichStyle(italic=True))
            .build()
        )
        assert got == want


class TestRichTextEl:
    def test_builds(self):
        want = {
            "type": "text",
            "text": "Curiouser and curiouser!",
            "style": {
                "bold": True,
            },
        }

        got = RichTextEl(
            text="Curiouser and curiouser!",
            style=RichStyle(bold=True),
        ).build()
        assert got == want

        got = (
            RichTextEl()
            .text("Curiouser and curiouser!")
            .style(RichStyle(bold=True))
            .build()
        )
        assert got == want


class TestRichUserEl:
    def test_builds(self):
        want = {
            "type": "user",
            "user_id": "U123456789",
            "style": {
                "italic": True,
            },
        }

        got = RichUserEl(
            user_id="U123456789",
            style=RichStyle(italic=True),
        ).build()
        assert got == want

        got = RichUserEl().user_id("U123456789").style(RichStyle(italic=True)).build()
        assert got == want


class TestRichUserGroupEl:
    def test_builds(self):
        want = {
            "type": "usergroup",
            "usergroup_id": "G123456789",
            "style": {
                "italic": True,
            },
        }

        got = RichUserGroupEl(
            usergroup_id="G123456789",
            style=RichStyle(italic=True),
        ).build()
        assert got == want

        got = (
            RichUserGroupEl()
            .usergroup_id("G123456789")
            .style(RichStyle(italic=True))
            .build()
        )
        assert got == want


class TestRichTextSection:
    def test_builds(self):
        want = {
            "type": "rich_text_section",
            "elements": [
                {
                    "type": "text",
                    "text": "Curiouser and curiouser!",
                    "style": {
                        "bold": True,
                    },
                },
                {
                    "type": "emoji",
                    "name": "rabbit",
                },
            ],
        }

        got = RichTextSection(
            elements=[
                RichTextEl(
                    text="Curiouser and curiouser!",
                    style=RichStyle(bold=True),
                ),
                RichEmojiEl(name="rabbit"),
            ]
        ).build()
        assert got == want

        got = (
            RichTextSection()
            .add_element(
                RichTextEl(
                    text="Curiouser and curiouser!",
                    style=RichStyle(bold=True),
                )
            )
            .add_element(RichEmojiEl(name="rabbit"))
            .build()
        )
        assert got == want


class TestRichTextList:
    def test_builds(self):
        want = {
            "type": "rich_text_list",
            "style": "bullet",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": "Cheshire Cat",
                        }
                    ],
                },
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": "Mad Hatter",
                        }
                    ],
                },
            ],
            "indent": 0,
            "offset": 0,
            "border": 0,
        }

        got = RichTextList(
            style="bullet",
            elements=[
                RichTextSection(
                    elements=[RichTextEl("Cheshire Cat")],
                ),
                RichTextSection(
                    elements=[RichTextEl("Mad Hatter")],
                ),
            ],
            indent=0,
            offset=0,
            border=0,
        ).build()
        assert got == want

        got = (
            RichTextList()
            .style("bullet")
            .add_element(RichTextSection().add_element(RichTextEl("Cheshire Cat")))
            .add_element(RichTextSection().add_element(RichTextEl("Mad Hatter")))
            .indent(0)
            .offset(0)
            .border(0)
            .build()
        )
        assert got == want


class TestRichTextPreformatted:
    def test_builds(self):
        want = {
            "type": "rich_text_preformatted",
            "elements": [
                {
                    "type": "text",
                    "text": "Curiouser and curiouser!",
                    "style": {
                        "bold": True,
                    },
                },
                {
                    "type": "emoji",
                    "name": "rabbit",
                },
            ],
            "border": 0,
        }

        got = RichTextPreformatted(
            elements=[
                RichTextEl(
                    text="Curiouser and curiouser!",
                    style=RichStyle(bold=True),
                ),
                RichEmojiEl(name="rabbit"),
            ],
            border=0,
        ).build()
        assert got == want

        got = (
            RichTextPreformatted()
            .add_element(
                RichTextEl(
                    text="Curiouser and curiouser!",
                    style=RichStyle(bold=True),
                )
            )
            .add_element(RichEmojiEl(name="rabbit"))
            .border(0)
            .build()
        )
        assert got == want


class TestRichTextQuote:
    def test_builds(self):
        want = {
            "type": "rich_text_quote",
            "elements": [
                {
                    "type": "text",
                    "text": "Curiouser and curiouser!",
                    "style": {
                        "bold": True,
                    },
                },
                {
                    "type": "emoji",
                    "name": "rabbit",
                },
            ],
            "border": 0,
        }

        got = RichTextQuote(
            elements=[
                RichTextEl(
                    text="Curiouser and curiouser!",
                    style=RichStyle(bold=True),
                ),
                RichEmojiEl(name="rabbit"),
            ],
            border=0,
        ).build()
        assert got == want

        got = (
            RichTextQuote()
            .add_element(
                RichTextEl(
                    text="Curiouser and curiouser!",
                    style=RichStyle(bold=True),
                )
            )
            .add_element(RichEmojiEl(name="rabbit"))
            .border(0)
            .build()
        )
        assert got == want


class TestRichText:
    def test_builds(self):
        want = {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": "Curiouser and curiouser!",
                            "style": {
                                "bold": True,
                            },
                        },
                        {
                            "type": "emoji",
                            "name": "rabbit",
                        },
                    ],
                },
                {
                    "type": "rich_text_list",
                    "style": "bullet",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": "Cheshire Cat",
                                }
                            ],
                        },
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": "Mad Hatter",
                                }
                            ],
                        },
                    ],
                },
            ],
            "block_id": "rich_text_block",
        }

        got = RichText(
            elements=[
                RichTextSection(
                    elements=[
                        RichTextEl(
                            text="Curiouser and curiouser!",
                            style=RichStyle(bold=True),
                        ),
                        RichEmojiEl(name="rabbit"),
                    ]
                ),
                RichTextList(
                    style="bullet",
                    elements=[
                        RichTextSection(
                            elements=[RichTextEl("Cheshire Cat")],
                        ),
                        RichTextSection(
                            elements=[RichTextEl("Mad Hatter")],
                        ),
                    ],
                ),
            ],
            block_id="rich_text_block",
        ).build()
        assert got == want

        got = (
            RichText()
            .add_element(
                RichTextSection()
                .add_element(
                    RichTextEl(
                        text="Curiouser and curiouser!",
                        style=RichStyle(bold=True),
                    )
                )
                .add_element(RichEmojiEl(name="rabbit"))
            )
            .add_element(
                RichTextList()
                .style("bullet")
                .add_element(RichTextSection().add_element(RichTextEl("Cheshire Cat")))
                .add_element(RichTextSection().add_element(RichTextEl("Mad Hatter")))
            )
            .block_id("rich_text_block")
            .build()
        )
        assert got == want


class TestSection:
    def test_builds_text(self):
        want = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "_Who in the world am I?_",
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Find out",
                },
                "action_id": "button_action",
            },
            "expand": False,
            "block_id": "section_block",
        }

        got = Section(
            text="_Who in the world am I?_",
            accessory=Button(text="Find out", action_id="button_action"),
            expand=False,
            block_id="section_block",
        ).build()
        assert got == want

        got = (
            Section()
            .text("_Who in the world am I?_")
            .accessory(Button(text="Find out", action_id="button_action"))
            .expand(False)
            .block_id("section_block")
            .build()
        )
        assert got == want

    def test_builds_fields(self):
        want = {
            "type": "section",
            "fields": [
                {
                    "type": "plain_text",
                    "text": "Eat me",
                },
                {
                    "type": "plain_text",
                    "text": "Drink me",
                },
            ],
        }

        got = Section(
            fields=[
                Text(text="Eat me"),
                Text(text="Drink me"),
            ]
        ).build()
        assert got == want

        got = (
            Section()
            .add_field(Text(text="Eat me"))
            .add_field(Text(text="Drink me"))
            .build()
        )
        assert got == want


class TestVideo:
    def test_builds(self):
        want = {
            "type": "video",
            "title": {
                "type": "plain_text",
                "text": "Down the rabbit hole",
            },
            "title_url": "https://wonderland.com/video/intro.mp4",
            "description": {
                "type": "plain_text",
                "text": "The adventure begins below",
            },
            "alt_text": "Alice falls down the rabbit hole",
            "video_url": "https://wonderland.com/video/intro.mp4",
            "thumbnail_url": "https://wonderland.com/static/hole.png",
            "provider_icon_url": "https://wonderland.com/static/provider.png",
            "provider_name": "wonderland",
            "author_name": "Lewis Carroll",
            "block_id": "video_block",
        }

        got = Video(
            title="Down the rabbit hole",
            title_url="https://wonderland.com/video/intro.mp4",
            description="The adventure begins below",
            alt_text="Alice falls down the rabbit hole",
            video_url="https://wonderland.com/video/intro.mp4",
            thumbnail_url="https://wonderland.com/static/hole.png",
            provider_icon_url="https://wonderland.com/static/provider.png",
            provider_name="wonderland",
            author_name="Lewis Carroll",
            block_id="video_block",
        ).build()
        assert got == want

        got = (
            Video()
            .title("Down the rabbit hole")
            .title_url("https://wonderland.com/video/intro.mp4")
            .description("The adventure begins below")
            .alt_text("Alice falls down the rabbit hole")
            .video_url("https://wonderland.com/video/intro.mp4")
            .thumbnail_url("https://wonderland.com/static/hole.png")
            .provider_icon_url("https://wonderland.com/static/provider.png")
            .provider_name("wonderland")
            .author_name("Lewis Carroll")
            .block_id("video_block")
            .build()
        )
        assert got == want


class TestMessage:
    def test_builds(self):
        want = {
            "text": "You've tumbled into something curious...",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Welcome to Wonderland!",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Things are getting *curiouser and curiouser* - "
                        "follow the white rabbit to see what's next. :rabbit:",
                    },
                },
            ],
            "thread_ts": "1716203456.789012",
            "mrkdwn": True,
        }

        got = Message(
            text="You've tumbled into something curious...",
            blocks=[
                Header(text="Welcome to Wonderland!"),
                Section(
                    text=Text(
                        "Things are getting *curiouser and curiouser* - "
                        "follow the white rabbit to see what's next. :rabbit:"
                    )
                ),
            ],
            thread_ts=1716203456.789012,
            mrkdwn=True,
        ).build()
        assert got == want

        got = (
            Message()
            .text("You've tumbled into something curious...")
            .add_block(Header(text="Welcome to Wonderland!"))
            .add_block(
                Section(
                    text=Text(
                        "Things are getting *curiouser and curiouser* - "
                        "follow the white rabbit to see what's next. :rabbit:"
                    )
                )
            )
            .thread_ts("1716203456.789012")
            .mrkdwn()
            .build()
        )
        assert got == want


class TestModal:
    def test_builds(self):
        want = {
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": "Enter Wonderland",
            },
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Welcome to Wonderland!",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Tell us _who you are_ before you dive in.",
                    },
                },
                {
                    "type": "input",
                    "label": {
                        "type": "plain_text",
                        "text": "Your name",
                    },
                    "element": {
                        "type": "plain_text_input",
                    },
                },
            ],
            "submit": {
                "type": "plain_text",
                "text": "Let's go!",
            },
            "close": {
                "type": "plain_text",
                "text": "Not now",
            },
            "private_metadata": '{"scene": "fall"}',
            "callback_id": "enter_wonderland",
            "clear_on_close": True,
            "notify_on_close": True,
            "external_id": "alice_intro",
            "submit_disabled": False,
        }

        got = Modal(
            title="Enter Wonderland",
            blocks=[
                Header(text="Welcome to Wonderland!"),
                Section(text="Tell us _who you are_ before you dive in."),
                Input(label="Your name", element=PlainTextInput()),
            ],
            submit="Let's go!",
            close="Not now",
            private_metadata={"scene": "fall"},
            callback_id="enter_wonderland",
            clear_on_close=True,
            notify_on_close=True,
            external_id="alice_intro",
            submit_disabled=False,
        ).build()
        assert got == want

        got = (
            Modal()
            .title("Enter Wonderland")
            .add_block(Header(text="Welcome to Wonderland!"))
            .add_block(Section(text="Tell us _who you are_ before you dive in."))
            .add_block(Input(label="Your name", element=PlainTextInput()))
            .submit("Let's go!")
            .close("Not now")
            .private_metadata({"scene": "fall"})
            .callback_id("enter_wonderland")
            .clear_on_close()
            .notify_on_close()
            .external_id("alice_intro")
            .submit_disabled(False)
            .build()
        )
        assert got == want


class TestAppHome:
    def test_builds(self):
        want = {
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Welcome to Wonderland!",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "I can't go back to yesterday because "
                        "I was a different person then.",
                    },
                },
            ],
            "private_metadata": '{"scene": "fall"}',
            "callback_id": "enter_wonderland",
            "external_id": "alice_intro",
        }

        got = Home(
            blocks=[
                Header(text="Welcome to Wonderland!"),
                Section(
                    text="I can't go back to yesterday because "
                    "I was a different person then."
                ),
            ],
            private_metadata={"scene": "fall"},
            callback_id="enter_wonderland",
            external_id="alice_intro",
        ).build()
        assert got == want

        got = (
            Home()
            .add_block(Header(text="Welcome to Wonderland!"))
            .add_block(
                Section(
                    text="I can't go back to yesterday because "
                    "I was a different person then."
                )
            )
            .private_metadata({"scene": "fall"})
            .callback_id("enter_wonderland")
            .external_id("alice_intro")
            .build()
        )
