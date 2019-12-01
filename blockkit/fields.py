from .validators import (
    validate_attr,
    validate_len,
    validate_options,
    validate_type,
    validate_types,
    validate_url,
)


class Field:
    def validate(self, value):
        return value


class StringField(Field):
    def __init__(self, max_length=None, options=None):
        self.max_length = max_length
        self.options = options or []

    def validate(self, value):
        validate_type(str)(value)

        if self.max_length:
            validate_len(value, self.max_length)

        if self.options:
            validate_options(value, self.options)

        return value


class BooleanField(Field):
    def validate(self, value):
        validate_type(bool)(value)

        return value


class TextField(Field):
    def __init__(self, max_length=None, plain=False):
        self.max_length = max_length
        self.plain = plain

    def validate(self, value):
        from .objects import Text

        validate_type(Text)(value)

        if self.max_length:
            validate_len(value.text, self.max_length)

        if self.plain:
            validate_attr("type", Text.PLAIN)(value)

        return value


class ArrayField(Field):
    def __init__(self, field_types=None, max_items=None):
        self.field_types = field_types
        self.max_items = max_items

    def validate(self, value):
        if self.field_types:
            validate_types(self.field_types)(value)

        if self.max_items:
            validate_len(value, self.max_items)

        return value


class UrlField(Field):
    def __init__(self, max_length=None):
        self.max_length = max_length

    def validate(self, value):
        validate_url(value)

        if self.max_length:
            validate_len(value, self.max_length)

        return value


class ConfirmField(Field):
    def validate(self, value):
        from . import Confirm
        validate_type(Confirm)(value)

        return value
