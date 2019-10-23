import json
from urllib.parse import quote

from .components import Component
from .elements import Image
from .objects import Text
from .validators import validate_non_empty, validate_type, validate_types


class Block(Component):
    def __init__(self, block_id=None):
        self._add_field('block_id', block_id)

    def builder_url(self):
        blocks = self.build()
        quoted_blocks = quote(json.dumps(blocks))

        return (f'https://api.slack.com/tools/block-kit-builder'
                f'?blocks=[{quoted_blocks}]&mode=message')


class Section(Block):
    def __init__(self, text, fields=None, accessory=None, block_id=None):
        super().__init__(block_id)
        self._add_field('type', 'section')
        self._add_field('text', text, [validate_type(Text)])
        self._add_field(
            'fields', fields,
            [validate_non_empty, validate_types([Text])])
        self._add_field('accessory', accessory, [validate_type(Image)])


"""
section = Section(
    Text('This is title'),
    fields=[
        Text('This is first field'),
        Text('This is second field'),
    ],
    accessory=Image('http://placekitten.com/200/200', 'Kittens'),
    block_id='kittens block'
)
section.builder_url()
"""
