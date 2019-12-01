import pytest

from blockkit.components import Component
from blockkit.objects import Text
from blockkit.fields import StringField, TextField, ArrayField

from .conftest import TITLE, TEXT


def test_component_detects_all_fields():
    class NotField:
        pass

    class FakeComponent(Component):
        title = StringField()
        text = StringField()
        not_field = NotField()

    component = FakeComponent()
    assert list(component._fields.keys()) == ['title', 'text']


def test_component_with_exeeding_args_raises_exception():
    class FakeComponent(Component):
        title = StringField()

    with pytest.raises(IndexError):
        FakeComponent('test', 'test', 'test')


def test_component_with_custom_validation_raises_exception():
    class FakeComponent(Component):
        title = StringField()

        def validate_title(self, value):
            raise ValueError

    with pytest.raises(ValueError):
        FakeComponent(TITLE)


def test_component_builds_fields():
    class FakeComponent(Component):
        title = StringField()
        text = TextField()
        elements = ArrayField([Text])

    component = FakeComponent(
        TITLE,
        Text(TEXT, type=Text.MARKDOWN),
        [Text(TEXT, type=Text.PLAIN) for _ in range(2)]
    )

    assert component.build() == {
        'title': TITLE,
        'text': {
            'type': 'mrkdwn',
            'text': TEXT
        },
        'elements': [
            {
                'type': 'plain_text',
                'text': TEXT
            },
            {
                'type': 'plain_text',
                'text': TEXT
            }
        ]
    }
