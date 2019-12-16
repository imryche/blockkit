from collections import OrderedDict

from .fields import Field


class ComponentMeta(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        new_class = super().__new__(cls, name, bases, attrs, **kwargs)
        fields = OrderedDict(
            (key, attrs[key])
            for key in attrs
            if issubclass(attrs[key].__class__, Field)
        )
        new_class._fields = fields

        return new_class


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

    def build(self):
        result = {}

        for name, field in self._fields.items():
            value = getattr(self, name, None)
            if value is None:
                continue

            if isinstance(value, list):
                value = [a.build() for a in value]
            else:
                if issubclass(type(value), Component):
                    value = value.build()

            result[name] = value

        return result
