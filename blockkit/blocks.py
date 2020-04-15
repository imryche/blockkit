from . import Text
from .components import Component
from .elements import (
    Button,
    Checkboxes,
    DatePicker,
    Element,
    Image,
    Overflow,
    PlainTextInput,
    Select,
)
from .fields import (
    ArrayField,
    BooleanField,
    ObjectField,
    StringField,
    TextField,
    UrlField,
    ValidationError,
)


class Block(Component):
    type = StringField()
    block_id = StringField(max_length=255)


class Section(Block):
    text = TextField(max_length=3000)
    fields = ArrayField(Text, max_items=10)
    accessory = ObjectField(Element)

    def __init__(self, text=None, block_id=None, fields=None, accessory=None):
        if not any((text, fields)):
            raise ValidationError("Provide either text or fields.")

        super().__init__("section", block_id, text, fields, accessory)


class Divider(Block):
    def __init__(self, block_id=None):
        super().__init__("divider", block_id)


class ImageBlock(Block):
    image_url = UrlField(max_length=3000)
    alt_text = StringField(max_length=2000)
    title = TextField(plain=True, max_length=2000)

    def __init__(self, image_url, alt_text, title=None, block_id=None):
        super().__init__("image", block_id, image_url, alt_text, title)


class Actions(Block):
    elements = ArrayField(Select, Button, Overflow, DatePicker, max_items=5)

    def __init__(self, elements, block_id=None):
        super().__init__("actions", block_id, elements)


class Context(Block):
    elements = ArrayField(Text, Image, max_items=10)

    def __init__(self, elements, block_id=None):
        super().__init__("context", block_id, elements)


class Input(Block):
    label = TextField(plain=True, max_length=2000)
    element = ObjectField(PlainTextInput, Select, DatePicker, Checkboxes)
    hint = TextField(plain=True, max_length=2000)
    optional = BooleanField()

    def __init__(self, label, element, block_id=None, hint=None, optional=None):
        super().__init__("input", block_id, label, element, hint, optional)


class File(Block):
    external_id = StringField()
    source = StringField()

    def __init__(self, external_id, source="remote", block_id=None):
        super().__init__("file", block_id, external_id, source)
