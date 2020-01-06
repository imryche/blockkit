from abc import ABC, abstractmethod

from .validators import (
    validate_attr,
    validate_max_len,
    validate_options,
    validate_type,
    validate_types,
    validate_url,
    validate_date,
    validate_min_len,
    ValidationError,
)


class Field(ABC):
    @abstractmethod
    def validate(self, value):
        pass


class StringField(Field):
    def __init__(self, max_length=None, options=None):
        self.max_length = max_length
        self.options = options or []

    def validate(self, value):
        validate_type(str)(value)

        if self.max_length:
            validate_max_len(value, self.max_length)

        if self.options:
            validate_options(value, self.options)

        return value


class IntegerField(Field):
    def __init__(self, max_value=None):
        self.max_value = max_value

    def validate(self, value):
        validate_type(int)(value)

        if self.max_value and value > self.max_value:
            raise ValidationError(f"{value} exeeds max value of {self.max_value}")

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
        from . import Text

        validate_type(Text)(value)

        if self.max_length:
            validate_max_len(value.text, self.max_length)

        if self.plain:
            validate_attr("type", Text.plain)(value)

        return value


class ArrayField(Field):
    def __init__(self, *field_types, min_items=None, max_items=None):
        self.field_types = field_types
        self.max_items = max_items
        self.min_items = min_items

    def validate(self, values):
        if self.field_types:
            validate_types(self.field_types)(values)

        if self.min_items:
            validate_min_len(values, self.min_items)

        if self.max_items:
            validate_max_len(values, self.max_items)

        return values


class UrlField(Field):
    def __init__(self, max_length=None):
        self.max_length = max_length

    def validate(self, value):
        validate_url(value)

        if self.max_length:
            validate_max_len(value, self.max_length)

        return value


class ObjectField(Field):
    def __init__(self, *field_types):
        self.field_types = field_types

    def validate(self, value):
        validate_types(self.field_types)((value,))

        return value


class DateField(Field):
    def validate(self, value):
        validate_date(value)

        return value
