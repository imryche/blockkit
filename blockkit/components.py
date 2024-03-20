import json
from typing import Any, List, Type

from pydantic import BaseModel, model_validator


try:
    from typing import get_origin, get_args
except ImportError:

    def get_origin(tp):
        return getattr(tp, "__origin__", None)

    def get_args(tp):
        return getattr(tp, "__args__", ())


class Component(BaseModel):
    @model_validator(mode="after")
    def expand_strings(self) -> Any:
        for field_name, field in self.model_fields.items():
            inner_types = self._get_inner_types(field.annotation)
            if not inner_types:
                continue

            value = getattr(self, field_name)
            type_names = [t.__name__ for t in inner_types]

            expandable = "MarkdownText" in type_names or "PlainText" in type_names
            if not expandable:
                continue

            if isinstance(value, str):
                value = self._expand_str(value, inner_types, type_names)
            if isinstance(value, list):
                value = [
                    self._expand_str(v, inner_types, type_names)
                    if isinstance(v, str)
                    else v
                    for v in value
                ]
            setattr(self, field_name, value)
        return self

    @classmethod
    def _expand_str(cls, value: str, types: List[Type[Any]], type_names: List[str]):
        if "MarkdownText" in type_names:
            return types[type_names.index("MarkdownText")](text=value)
        elif "PlainText" in type_names:
            return types[type_names.index("PlainText")](text=value, emoji=True)
        return value

    @classmethod
    def _get_inner_types(cls, types, parent_types=None):
        origin = get_origin(types)
        if not origin:
            return parent_types
        args = get_args(types)
        return cls._get_inner_types(args[0], parent_types=args)

    def build(self) -> dict:
        return json.loads(self.model_dump_json(by_alias=True, exclude_none=True))
