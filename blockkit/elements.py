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
from .validators import ValidationError


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


class SelectBase(Component):
    type = StringField()
    placeholder = TextField(plain=True, max_length=150)
    action_id = StringField(max_length=255)
    confirm = ConfirmField()


class MultiStaticSelect(SelectBase):
    initial_options = ArrayField([Option, OptionGroup], max_items=100)
    options = ArrayField([Option], max_items=100)
    option_groups = ArrayField([OptionGroup], max_items=100)
    max_selected_items = IntegerField()

    def __init__(
        self,
        placeholder,
        action_id,
        confirm=None,
        max_selected_items=None,
        initial_options=None,
        options=None,
        option_groups=None,
    ):
        if options and option_groups:
            raise ValidationError("You can specify either options or option_groups")

        super().__init__(
            "multi_static_select",
            placeholder,
            action_id,
            confirm,
            initial_options,
            options,
            option_groups,
            max_selected_items,
        )


class MultiExternalSelect(SelectBase):
    initial_options = ArrayField([Option, OptionGroup], max_items=100)
    min_query_length = IntegerField()
    max_selected_items = IntegerField()

    def __init__(
        self,
        placeholder,
        action_id,
        confirm=None,
        max_selected_items=None,
        initial_options=None,
        min_query_length=None,
    ):
        super().__init__(
            "multi_external_select",
            placeholder,
            action_id,
            confirm,
            initial_options,
            min_query_length,
            max_selected_items,
        )


class MultiUsersSelect(SelectBase):
    initial_users = ArrayField([str])
    max_selected_items = IntegerField()

    def __init__(
        self,
        placeholder,
        action_id,
        confirm=None,
        max_selected_items=None,
        initial_users=None,
    ):
        super().__init__(
            "multi_users_select",
            placeholder,
            action_id,
            confirm,
            initial_users,
            max_selected_items,
        )


class MultiConversationsSelect(SelectBase):
    initial_conversations = ArrayField([str])
    max_selected_items = IntegerField()

    def __init__(
        self,
        placeholder,
        action_id,
        confirm=None,
        max_selected_items=None,
        initial_conversations=None,
    ):
        super().__init__(
            "multi_conversations_select",
            placeholder,
            action_id,
            confirm,
            initial_conversations,
            max_selected_items,
        )


class MultiChannelsSelect(SelectBase):
    initial_channels = ArrayField([str])
    max_selected_items = IntegerField()

    def __init__(
        self,
        placeholder,
        action_id,
        confirm=None,
        initial_channels=None,
        max_selected_items=None,
    ):
        super().__init__(
            "multi_channels_select",
            placeholder,
            action_id,
            confirm,
            initial_channels,
            max_selected_items,
        )
