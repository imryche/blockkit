from blockkit.fields import (
    ArrayField,
    ObjectField,
    DateField,
    IntegerField,
    StringField,
    TextField,
    UrlField,
)

from . import Option, OptionGroup, Confirm
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
    confirm = ObjectField(Confirm)

    def __init__(self, text, action_id, url=None, value=None, style=None, confirm=None):
        super().__init__("button", text, action_id, url, value, style, confirm)


class DatePicker(Component):
    type = StringField()
    action_id = StringField(max_length=255)
    placeholder = TextField(plain=True, max_length=150)
    initial_date = DateField()
    confirm = ObjectField(Confirm)

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
    confirm = ObjectField(Confirm)


class StaticSelectBase(SelectBase):
    options = ArrayField(Option, max_items=100)
    option_groups = ArrayField(OptionGroup, max_items=100)


class StaticSelect(StaticSelectBase):
    initial_option = ObjectField(Option, OptionGroup)

    def __init__(
        self,
        placeholder,
        action_id,
        options=None,
        option_groups=None,
        initial_option=None,
        confirm=None,
        max_selected_items=None,
    ):
        if options and option_groups:
            raise ValidationError("You can specify either options or option_groups")

        super().__init__(
            "static_select",
            placeholder,
            action_id,
            confirm,
            options,
            option_groups,
            initial_option,
        )


class MultiStaticSelect(StaticSelectBase):
    initial_options = ArrayField(Option, OptionGroup, max_items=100)
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
        if options and option_groups:
            raise ValidationError("You can specify either options or option_groups")

        super().__init__(
            "multi_static_select",
            placeholder,
            action_id,
            confirm,
            options,
            option_groups,
            initial_options,
            max_selected_items,
        )


class ExternalSelectBase(SelectBase):
    min_query_length = IntegerField()


class ExternalSelect(ExternalSelectBase):
    initial_option = ObjectField(Option, OptionGroup)

    def __init__(
        self,
        placeholder,
        action_id,
        initial_option=None,
        min_query_length=None,
        confirm=None,
    ):
        super().__init__(
            "external_select",
            placeholder,
            action_id,
            confirm,
            min_query_length,
            initial_option,
        )


class MultiExternalSelect(ExternalSelectBase):
    initial_options = ArrayField(Option, OptionGroup, max_items=100)
    max_selected_items = IntegerField()

    def __init__(
        self,
        placeholder,
        action_id,
        min_query_length=None,
        initial_options=None,
        confirm=None,
        max_selected_items=None,
    ):
        super().__init__(
            "multi_external_select",
            placeholder,
            action_id,
            confirm,
            min_query_length,
            initial_options,
            max_selected_items,
        )


class UsersSelect(SelectBase):
    initial_user = StringField()

    def __init__(
        self, placeholder, action_id, initial_user=None, confirm=None,
    ):
        super().__init__(
            "users_select", placeholder, action_id, confirm, initial_user,
        )


class MultiUsersSelect(SelectBase):
    initial_users = ArrayField(str)
    max_selected_items = IntegerField()

    def __init__(
        self,
        placeholder,
        action_id,
        initial_users=None,
        confirm=None,
        max_selected_items=None,
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
    initial_conversations = ArrayField(str)
    max_selected_items = IntegerField()

    def __init__(
        self,
        placeholder,
        action_id,
        initial_conversations=None,
        confirm=None,
        max_selected_items=None,
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
    initial_channels = ArrayField(str)
    max_selected_items = IntegerField()

    def __init__(
        self,
        placeholder,
        action_id,
        initial_channels=None,
        confirm=None,
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
