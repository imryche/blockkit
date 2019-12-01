class Field:
    def validate(self, value):
        print('validated')
        return value


class MetaComponent(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        new_class = super().__new__(cls, name, bases, attrs, **kwargs)
        fields = {
            k: v
            for k, v in attrs.items() if issubclass(v.__class__, Field)
        }
        new_class._fields = fields
        return new_class


class Component(metaclass=MetaComponent):
    def __init__(self, *args, **kwargs):
        iter_fields = iter(self._fields)

        for arg in args:
            name = next(iter_fields)
            field = self._fields[name]
            setattr(self, name, field.validate(arg))

        for name in iter_fields:
            value = kwargs.get(name, None)
            if not value:
                continue

            field = self._fields[name]
            setattr(self, name, field.validate(value))


class Section(Component):
    title = Field()
    text = Field()
    accessory = Field()
    type = Field()


s = Section('foo', accessory='bar', text='test')
print(s.title, s.text, s.accessory, s.type)
