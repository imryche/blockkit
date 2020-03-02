import re
from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime

import validators.url


class ValidationError(Exception):
    pass


def validate_type(values, *types):
    pretty_types = [t.__name__ for t in types]
    if not isinstance(values, Iterable):
        values = [values]

    for value in values:
        if not any(isinstance(value, t) for t in types):
            raise ValidationError(
                f"{value} should be an instance one of either {pretty_types}."
            )

    return values


def validate_non_empty(value):
    if len(value) < 1:
        raise ValidationError("Can't be empty.")

    return value


def validate_options(value, options):
    if value not in options:
        raise ValidationError(f"{value} should be one of the {options}.")

    return value


def validate_url(value):
    has_deep_link = re.match(r"^slack://[a-zA-Z0-9?&=-]+$", value)
    if not has_deep_link and not validators.url(value):
        raise ValidationError(f"{value} is not correct url.")

    return value


def validate_attr(value, attr, attr_value):
    if getattr(value, attr) != attr_value:
        raise ValidationError(f"{value}.{attr} has incorrect value of {attr_value}.")

    return value


def validate_max_len(value, length):
    if len(value) > length:
        raise ValidationError(f"{value} length is more than {length}.")

    return value


def validate_min_len(value, length):
    if len(value) < length:
        raise ValidationError(f"{value} length is less than {length}.")

    return value


def validate_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(f"{value} has incorrect date format.")

    return value


class Field(ABC):
    @abstractmethod
    def validate(self, value):
        pass


class StringField(Field):
    def __init__(self, max_length=None, options=None):
        self.max_length = max_length
        self.options = options or []

    def validate(self, value):
        validate_type(value, str)

        if self.max_length:
            validate_max_len(value, self.max_length)

        if self.options:
            validate_options(value, self.options)

        return value


class IntegerField(Field):
    def __init__(self, max_value=None):
        self.max_value = max_value

    def validate(self, value):
        validate_type(value, int)

        if self.max_value and value > self.max_value:
            raise ValidationError(f"{value} exeeds max value of {self.max_value}.")

        return value


class BooleanField(Field):
    def validate(self, value):
        validate_type(value, bool)

        return value


class TextField(Field):
    def __init__(self, max_length=None, plain=False):
        self.max_length = max_length
        self.plain = plain

    def validate(self, value):
        from . import Text, PlainText

        if type(value) == str:
            value = PlainText(value, emoji=True)

        if self.plain:
            validate_attr(value, "type", Text.plain)

        validate_type(value, Text)

        if self.max_length:
            validate_max_len(value.text, self.max_length)

        return value


class ArrayField(Field):
    def __init__(self, *field_types, min_items=None, max_items=None):
        self.field_types = field_types
        self.max_items = max_items
        self.min_items = min_items

    def validate(self, values):
        from . import PlainText

        if str not in self.field_types:
            values = [PlainText(v, emoji=True) if type(v) == str else v for v in values]

        if self.field_types:
            for value in values:
                validate_type(value, *self.field_types)

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
        validate_type(value, *self.field_types)

        return value


class DateField(Field):
    def validate(self, value):
        validate_date(value)

        return value
