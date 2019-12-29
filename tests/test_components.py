import pytest

from blockkit import MarkdownText, PlainText
from blockkit.components import Component
from blockkit.fields import StringField, TextField, ArrayField


def test_component_detects_all_fields():
    class NotField:
        pass

    class FakeComponent(Component):
        title = StringField()
        text = StringField()
        not_field = NotField()

    component = FakeComponent()
    assert list(component._fields.keys()) == ["title", "text"]


def test_component_with_exeeding_args_raises_exception():
    class FakeComponent(Component):
        title = StringField()

    with pytest.raises(IndexError):
        FakeComponent("test", "test", "test")


def test_component_builds_fields(values):
    class ParentFakeComponent(Component):
        title = StringField()
        text = TextField()

    class FakeComponent(ParentFakeComponent):
        elements = ArrayField(PlainText)
        users = ArrayField(str)

    users = ["U123456", "U654321"]
    component = FakeComponent(
        values.title,
        MarkdownText(values.text),
        [PlainText(values.text) for _ in range(2)],
        users,
    )

    assert component.build() == {
        "title": values.title,
        "text": {"type": "mrkdwn", "text": values.text},
        "elements": [
            {"type": "plain_text", "text": values.text},
            {"type": "plain_text", "text": values.text},
        ],
        "users": users,
    }
