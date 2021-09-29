from pydantic import validator as pydantic_validator


def validator(field, func, **kwargs):
    return pydantic_validator(field, allow_reuse=True)(lambda v: func(v, **kwargs))


def validators(field, *validator_funcs):
    def validate(v):
        for func, kwargs in validator_funcs:
            func(v, **kwargs)
        return v

    return pydantic_validator(field, allow_reuse=True)(lambda v: validate(v))


def validate_int_range(v, *, min_value, max_value):
    if v is not None and not min_value <= v <= max_value:
        raise ValueError(f"Should be between {min_value} and {max_value}")
    return v


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


def validate_string_length(v, *, max_len):
    if v is not None and len(v) > max_len:
        raise ValueError(f"Maximum length is {max_len} characters")
    return v


def validate_choices(v, *, choices):
    if v is not None and v not in choices:
        raise ValueError(f"Allowed values are {choices}")
    return v


def validate_list_choices(v, *, choices):
    if v is not None and len(v) == 0 or set(v) - set(choices):
        raise ValueError(f"Allowed values are {choices}")
    return v


def validate_list_size(v, *, min_len, max_len):
    if v is not None:
        if len(v) < min_len:
            raise ValueError(
                f"Must contain at least {min_len} item" + ("s" if min_len > 1 else "")
            )
        if len(v) > max_len:
            raise ValueError(
                f"Must contain a maximum of {max_len} item" + ("s" if max_len > 1 else "")
            )
    return v


def validate_date(v):
    if v is not None:
        return v.isoformat()
    return v


def validate_time(v):
    if v is not None:
        return v.strftime("%H:%M")
    return v
