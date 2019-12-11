from blockkit.fields import (
    ArrayField,
    ConfirmField,
    DateField,
    IntegerField,
    StringField,
    TextField,
    UrlField,
)

from . import Option, OptionGroup
from .components import Component


class Button(Component):
    primary = "primary"
    danger = "danger"

    type = StringField()
    text = TextField(plain=True, max_length=75)
    action_id = StringField(max_length=255)
    url = UrlField(max_length=3000)
    value = StringField(max_length=2000)
    style = StringField(options=[primary, danger])
    confirm = ConfirmField()

    def __init__(self, text, action_id, url=None, value=None, style=None, confirm=None):
        super().__init__("button", text, action_id, url, value, style, confirm)


class DatePicker(Component):
    type = StringField()
    action_id = StringField(max_length=255)
    placeholder = TextField(plain=True, max_length=150)
    initial_date = DateField()
    confirm = ConfirmField()

    def __init__(self, action_id, placeholder=None, initial_date=None, confirm=None):
        super().__init__("datepicker", action_id, placeholder, initial_date, confirm)


class Image(Component):
    type = StringField()
    image_url = UrlField()
    alt_text = StringField()

    def __init__(self, image_url, alt_text):
        super().__init__("image", image_url, alt_text)


class MultiSelect(Component):
    type = StringField()
    placeholder = TextField(plain=True, max_length=150)
    action_id = StringField(max_length=255)
    options = ArrayField([Option], max_items=100)
    option_groups = ArrayField([OptionGroup], max_items=100)
    initial_options = ArrayField([Option, OptionGroup], max_items=100)
    confirm = ConfirmField()
    max_selected_items = IntegerField()

    def __init__(
        self,
        placeholder,
        action_id,
        options=None,
        option_groups=None,
        initial_options=None,
        confirm=None,
        max_selected_items=None,
    ):
        super().__init__(
            "multi_static_select",
            placeholder,
            action_id,
            options,
            option_groups,
            initial_options,
            confirm,
            max_selected_items,
        )
