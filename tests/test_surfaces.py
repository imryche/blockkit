import pytest
from blockkit.blocks import Input, RichText, RichTextSection, Section
from blockkit.elements import Button, PlainTextInput
from blockkit.objects import MarkdownText, PlainText, Text
from blockkit.surfaces import Home, Message, Modal, WorkflowStep
from pydantic import ValidationError


def test_builds_home():
    assert Home(
        blocks=[
            Section(
                text=MarkdownText(text="*markdown* text"),
                accessory=Button(text=PlainText(text="button"), action_id="action_id"),
            )
        ],
        private_metadata="private_metadata",
        callback_id="callback_id",
        external_id="external_id",
    ).build() == {
        "type": "home",
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*markdown* text"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "button"},
                    "action_id": "action_id",
                },
            }
        ],
        "private_metadata": "private_metadata",
        "callback_id": "callback_id",
        "external_id": "external_id",
    }


def test_home_empty_blocks_raise_exception():
    with pytest.raises(ValidationError):
        Home(blocks=[])


def test_home_excessive_blocks_raise_exception():
    with pytest.raises(ValidationError):
        Home(
            blocks=[
                Section(text=MarkdownText(text="*markdown* text")) for _ in range(101)
            ]
        )


def test_home_excessive_private_metadata_raise_exception():
    with pytest.raises(ValidationError):
        Home(
            blocks=[Section(text=MarkdownText(text="*markdown* text"))],
            private_metadata="p" * 3001,
        )


def test_home_excessive_callback_id_raise_exception():
    with pytest.raises(ValidationError):
        Home(
            blocks=[Section(text=MarkdownText(text="*markdown* text"))],
            callback_id="c" * 256,
        )


def test_home_excessive_external_id_raise_exception():
    with pytest.raises(ValidationError):
        Home(
            blocks=[Section(text=MarkdownText(text="*markdown* text"))],
            external_id="c" * 256,
        )


def test_builds_modal():
    assert Modal(
        title=PlainText(text="title"),
        blocks=[
            Section(
                text=MarkdownText(text="*markdown* text"),
                accessory=Button(text=PlainText(text="button"), action_id="action_id"),
            )
        ],
        close=PlainText(text="close"),
        submit=PlainText(text="submit"),
        private_metadata="private_metadata",
        callback_id="callback_id",
        clear_on_close=True,
        notify_on_close=True,
        external_id="external_id",
        submit_disabled=True,
    ).build() == {
        "type": "modal",
        "title": {"type": "plain_text", "text": "title"},
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*markdown* text"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "button"},
                    "action_id": "action_id",
                },
            }
        ],
        "close": {"type": "plain_text", "text": "close"},
        "submit": {"type": "plain_text", "text": "submit"},
        "private_metadata": "private_metadata",
        "callback_id": "callback_id",
        "clear_on_close": True,
        "notify_on_close": True,
        "external_id": "external_id",
        "submit_disabled": True,
    }


def test_modal_excessive_title_raises_exception():
    with pytest.raises(ValidationError):
        Modal(
            title=PlainText(text="t" * 25),
            blocks=[Section(text=MarkdownText(text="*markdown* text"))],
        )


def test_modal_empty_blocks_raise_exception():
    with pytest.raises(ValidationError):
        Modal(title=PlainText(text="title"), blocks=[])


def test_modal_excessive_blocks_raise_exception():
    with pytest.raises(ValidationError):
        Modal(
            title=PlainText(text="title"),
            blocks=[
                Section(text=MarkdownText(text="*markdown* text")) for _ in range(101)
            ],
        )


def test_modal_excessive_close_raises_exception():
    with pytest.raises(ValidationError):
        Modal(
            title=PlainText(text="title"),
            blocks=[Section(text=MarkdownText(text="*markdown* text"))],
            close=PlainText(text="c" * 25),
        )


def test_modal_excessive_submit_raises_exception():
    with pytest.raises(ValidationError):
        Modal(
            title=PlainText(text="title"),
            blocks=[Section(text=MarkdownText(text="*markdown* text"))],
            submit=PlainText(text="s" * 25),
        )


def test_modal_input_without_submit_raises_exception():
    with pytest.raises(ValidationError):
        Modal(
            title=PlainText(text="title"),
            blocks=[Input(label=PlainText(text="label"), element=PlainTextInput())],
        )


def test_modal_excessive_private_metadata_raises_exception():
    with pytest.raises(ValidationError):
        Modal(
            title=PlainText(text="title"),
            blocks=[Section(text=MarkdownText(text="*markdown* text"))],
            private_metadata="p" * 3001,
        )


def test_modal_excessive_callback_id_raises_exception():
    with pytest.raises(ValidationError):
        Modal(
            title=PlainText(text="title"),
            blocks=[Section(text=MarkdownText(text="*markdown* text"))],
            callback_id="c" * 256,
        )


def test_modal_excessive_external_id_raises_exception():
    with pytest.raises(ValidationError):
        Modal(
            title=PlainText(text="title"),
            blocks=[Section(text=MarkdownText(text="*markdown* text"))],
            external_id="c" * 256,
        )


def test_builds_message():
    assert Message(
        text="message text",
        blocks=[
            Section(
                text="*markdown* text",
                accessory=Button(text=PlainText(text="button"), action_id="action_id"),
            ),
            RichText(
                elements=[RichTextSection(elements=[Text(text="test_rich_text")])]
            ),
        ],
    ).build() == {
        "text": "message text",
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*markdown* text"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "button"},
                    "action_id": "action_id",
                },
            },
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [{"type": "text", "text": "test_rich_text"}],
                    }
                ],
            },
        ],
    }


def test_empty_message_raises_exception():
    with pytest.raises(ValidationError):
        Message()


def test_message_empty_blocks_raise_exception():
    with pytest.raises(ValidationError):
        Message(blocks=[])


def test_message_excessive_blocks_raise_exception():
    with pytest.raises(ValidationError):
        Message(
            blocks=[
                Section(text=MarkdownText(text="*markdown* text")) for _ in range(51)
            ]
        )


def test_builds_workflow_step():
    assert WorkflowStep(
        blocks=[
            Section(
                text=MarkdownText(text="*markdown* text"),
                accessory=Button(text=PlainText(text="button"), action_id="action_id"),
            )
        ],
        private_metadata="private_metadata",
        callback_id="callback_id",
        submit_disabled=True,
    ).build() == {
        "type": "workflow_step",
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*markdown* text"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "button"},
                    "action_id": "action_id",
                },
            }
        ],
        "private_metadata": "private_metadata",
        "callback_id": "callback_id",
        "submit_disabled": True,
    }


def test_workflow_step_empty_blocks_raise_exception():
    with pytest.raises(ValidationError):
        WorkflowStep(blocks=[])


def test_workflow_step_excessive_blocks_raise_exception():
    with pytest.raises(ValidationError):
        WorkflowStep(
            blocks=[
                Section(text=MarkdownText(text="*markdown* text")) for _ in range(101)
            ]
        )


def test_workflow_step_excessive_callback_id_raises_exception():
    with pytest.raises(ValidationError):
        WorkflowStep(
            blocks=[Section(text=MarkdownText(text="*markdown* text"))],
            callback_id="c" * 256,
        )
