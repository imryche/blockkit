from .components import Component
from .objects import Text, validate_plain
from .validators import validate_url, validate_type, validate_choices


class Element(Component):
    def __init__(self, action_id=None):
        self._add_field('action_id', action_id)


class Image(Element):
    TYPE = 'image'

    def __init__(self, image_url, alt_text):
        self._add_field('type', self.TYPE)
        self._add_field('image_url', image_url, [validate_url])
        self._add_field('alt_text', alt_text)


class Button(Element):
    TYPE = 'button'
    PRIMARY = 'primary'
    DANGER = 'danger'

    def __init__(self, text, value=None, url=None, style=None, action_id=None):
        super().__init__(action_id)
        self._add_field('type', self.TYPE)
        # TODO: can only be of type: plain_text
        self._add_field('text', text, [validate_type(Text), validate_plain])
        self._add_field('value', value)
        self._add_field('url', url, [validate_url])
        self._add_field('style', style,
                        [validate_choices([self.PRIMARY, self.DANGER])])
        # TODO: add confirm field
