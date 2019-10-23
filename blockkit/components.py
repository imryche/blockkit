class Component:
    def _add_field(self, name, value, validators=None):
        if value is None:
            return

        for validator in validators or []:
            validator(value)

        validator = getattr(self, f'_validate_{name}', None)
        if validator:
            validator(value)

        if not hasattr(self, '_fields'):
            self._fields = []

        self._fields.append(name)

        setattr(self, name, value)

    def build(self):
        result = {}

        for field in self._fields:
            value = getattr(self, field)

            if isinstance(value, list):
                value = [a.build() for a in value]
            else:
                if issubclass(type(value), Component):
                    value = value.build()

            result[field] = value

        return result
