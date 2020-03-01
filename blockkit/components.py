from collections import OrderedDict

from .fields import Field


class ComponentMeta(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        class_ = super().__new__(cls, name, bases, attrs, **kwargs)

        fields = OrderedDict(
            (key, attrs[key])
            for key in attrs
            if issubclass(attrs[key].__class__, Field)
        )

        parent_fields = getattr(class_, "_fields", None)
        if parent_fields:
            class_._fields = {**parent_fields, **fields}
        else:
            class_._fields = fields

        return class_


class Component(metaclass=ComponentMeta):
    def __init__(self, *args):
        if len(args) > len(self._fields):
            raise IndexError("Number of args exceeds number of fields")

        fields_iter = iter(self._fields)

        for value in args:
            field_name = next(fields_iter)
            field = self._fields[field_name]

            if value is not None:
                value = field.validate(value)

            setattr(self, field_name, value)

    def __repr__(self):
        values = ", ".join(str(getattr(self, f)) for f in self._fields)
        return f"{self.__class__.__name__}({values})"

    def __eq__(self, other):
        return all(getattr(self, attr) == getattr(other, attr) for attr in self._fields)

    def build(self):
        result = {}

        for name, field in self._fields.items():
            value = getattr(self, name, None)
            if value is None:
                continue

            if isinstance(value, list):
                value = [
                    el.build() if isinstance(el, Component) else el for el in value
                ]
            else:
                if issubclass(type(value), Component):
                    value = value.build()

            result[name] = value

        return result
