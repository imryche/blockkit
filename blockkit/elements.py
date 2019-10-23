from .components import Component
from .validators import validate_url


class Image(Component):
    def __init__(self, image_url, alt_text):
        self._add_field('type', 'image')
        self._add_field('image_url', image_url, [validate_url])
        self._add_field('alt_text', alt_text)
