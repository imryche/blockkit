from collections.abc import Sequence
from datetime import datetime

import validators.url


class ValidationError(Exception):
    pass


def validate_type(types):
    def validate(value):
        value_types = types
        if not isinstance(types, Sequence):
            value_types = [types]

        for value_type in value_types:
            if not isinstance(value, value_type):
                raise ValidationError(f'{value} should be an instance '
                                      f'of {value_type}')

    return validate


def validate_types(types):
    def validate(values):
        for value in values:
            if type(value) not in types:
                raise ValidationError(
                    f'{value} should be an instance of {types}')

    return validate


def validate_non_empty(value):
    if len(value) < 1:
        raise ValidationError('This field can\'t be empty')
    return value


def validate_choices(choices):
    def validate(value):
        for c in choices:
            if value not in choices:
                raise ValidationError(f'{c} should be either {choices}')

    return validate


def validate_options(value, options):
    if value not in options:
        raise ValidationError(f'{value} shouel be one of the {options}')


def validate_url(url):
    if not validators.url(url):
        raise ValidationError(f'{url} is not correct url')
    return url


def validate_attr(attr, attr_value):
    def validate(value):
        if getattr(value, attr) != attr_value:
            raise ValidationError(
                f'{value}.{attr} has incorrect value of {attr_value}')

    return validate


def validate_len(value, length):
    if len(value) > length:
        raise ValidationError(f'{value} length is more than {length}')


def validate_min_len(value, length):
    if len(value) < length:
        raise ValidationError(f'{value} length is less than {length}')

    return value


def validate_date(value):
    try:
        datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        raise ValidationError(f'{value} has incorrect date format')

    return value
