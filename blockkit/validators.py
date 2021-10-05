from pydantic import AnyUrl
from pydantic import validator as pydantic_validator


def validator(field, func, **kwargs):
    return pydantic_validator(field, allow_reuse=True)(lambda v: func(v, **kwargs))


def validate_text_length(v, *, max_len):
    if v is not None and len(v.text) > max_len:
        raise ValueError(f"Maximum length is {max_len} characters")
    return v


def validate_list_text_length(v, *, max_len):
    if v is None:
        return
    for item in v:
        validate_text_length(item, max_len=max_len)
    return v


def validate_date(v):
    if v is not None:
        return v.isoformat()
    return v


def validate_time(v):
    if v is not None:
        return v.strftime("%H:%M")
    return v


class SlackUrl(AnyUrl):
    max_length = 3000
