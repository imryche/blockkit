import json
from typing import TYPE_CHECKING, Any, List, Type, Union

from pydantic import BaseModel

if TYPE_CHECKING:
    from blockkit.objects import MarkdownText, PlainText


class Component(BaseModel):
    def __init__(self, *args, **kwargs):
        for name, field in self.__fields__.items():
            value = kwargs.get(field.alias)
            origin = getattr(field.type_, "__origin__", None)

            if (
                value
                and type(value) in (str, list)
                and origin is Union
                and self.__class__.__name__ != "Message"
            ):
                types = field.type_.__args__

                if type(value) is str:
                    value = self._expand_str(value, types)
                elif type(value) is list:
                    items = []
                    for v in value:
                        if type(v) is str:
                            v = self._expand_str(v, types)
                        items.append(v)
                    value = items

                kwargs[field.alias] = value

        super().__init__(*args, **kwargs)

    def _expand_str(
        self, value: str, types: List[Type[Any]]
    ) -> Union["PlainText", "MarkdownText", str]:
        literal_types = [t.__name__ for t in types]

        if "MarkdownText" in literal_types:
            idx = literal_types.index("MarkdownText")
            return types[idx](text=value)
        elif "PlainText" in literal_types:
            idx = literal_types.index("PlainText")
            return types[idx](text=value, emoji=True)

        return value

    def build(self) -> dict:
        return json.loads(self.json(by_alias=True, exclude_none=True))
