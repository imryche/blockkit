from . import Text
from .components import Component
from .elements import Element
from .fields import ArrayField, ObjectField, StringField, TextField


class Block(Component):
    type = StringField()
    block_id = StringField(max_length=255)


class Section(Block):
    text = TextField(max_length=3000)
    fields = ArrayField(Text, max_items=10)
    accessory = ObjectField(Element)

    def __init__(self, text, block_id=None, fields=None, accessory=None):
        super().__init__("section", block_id, text, fields, accessory)


class Divider(Block):
    def __init__(self, block_id=None):
        super().__init__("divider", block_id)
