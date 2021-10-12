from datetime import date, time
from typing import TYPE_CHECKING, Callable, Optional, Union

from pydantic import AnyUrl
from pydantic import validator as pydantic_validator

if TYPE_CHECKING:
    from blockkit.objects import MarkdownText, PlainText


def validator(
    field: str, func: Callable, each_item: bool = False, **kwargs
) -> classmethod:
    return pydantic_validator(field, allow_reuse=True, each_item=each_item)(
        lambda v: func(v, **kwargs)
    )


def validate_text_length(
    v: Union["PlainText", "MarkdownText", str], *, max_length: int
) -> Union["PlainText", "MarkdownText", str]:
    if v is not None:
        e = ValueError(f"Maximum length is {max_length} characters")
        if type(v) == str and len(v) > max_length:
            raise e
        elif type(v) != str and len(getattr(v, "text")) > max_length:
            raise e
    return v


def validate_date(v: date) -> Optional[str]:
    if v is not None:
        return v.isoformat()
    return v


def validate_time(v: time) -> Optional[str]:
    if v is not None:
        return v.strftime("%H:%M")
    return v


class SlackUrl(AnyUrl):
    max_length = 3000
