from typing import Union

from pydantic import BaseModel


class Component(BaseModel):
    def __init__(self, *args, **kwargs):
        for name, field in self.__fields__.items():
            value = kwargs.get(field.alias)
            origin = getattr(field.type_, "__origin__", None)

            if value and type(value) is str and origin is Union:
                types = field.type_.__args__
                literal_types = [t.__name__ for t in types]

                if "MarkdownText" in literal_types:
                    idx = literal_types.index("MarkdownText")
                    value = types[idx](text=value)
                elif "PlainText" in literal_types:
                    idx = literal_types.index("PlainText")
                    value = types[idx](text=value, emoji=True)

                kwargs[name] = value

        super().__init__(*args, **kwargs)

    def build(self) -> dict:
        return self.dict(by_alias=True, exclude_none=True)
