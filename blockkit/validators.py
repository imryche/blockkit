from collections.abc import Sequence

import validators.url


def validate_type(types):
    def validate(value):
        value_types = types
        if not isinstance(types, Sequence):
            value_types = [types]

        for value_type in value_types:
            if not isinstance(value, value_type):
                raise ValueError(f'{value} should be an instance '
                                 f'of {value_type}')

    return validate


def validate_types(types):
    def validate(values):
        for value in values:
            if type(value) not in types:
                raise ValueError(f'{value} should be an instance of {types}')

    return validate


def validate_non_empty(value):
    if len(value) < 1:
        raise ValueError('This field can\'t be empty')
    return value


def validate_choices(choices):
    def validate(value):
        for c in choices:
            if value not in choices:
                raise ValueError(f'{c} should be either {choices}')

    return validate


def validate_url(url):
    if not validators.url(url):
        raise ValueError(f'{url} is not correct url')
    return url
