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


class Element(Component):
    type = StringField()
    action_id = StringField(max_length=255)


class Button(Element):
    primary = "primary"
    danger = "danger"

    text = TextField(plain=True, max_length=75)
    url = UrlField(max_length=3000)
    value = StringField(max_length=2000)
    style = StringField(options=[primary, danger])
    confirm = ObjectField(Confirm)

    def __init__(self, text, action_id, url=None, value=None, style=None, confirm=None):
        super().__init__("button", action_id, text, url, value, style, confirm)


class DatePicker(Element):
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


class SelectBase(Element):
    placeholder = TextField(plain=True, max_length=150)
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
            action_id,
            placeholder,
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
            action_id,
            placeholder,
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
            action_id,
            placeholder,
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
            action_id,
            placeholder,
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
            "users_select", action_id, placeholder, confirm, initial_user,
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
            action_id,
            placeholder,
            confirm,
            initial_users,
            max_selected_items,
        )


class ConversationsSelect(SelectBase):
    initial_conversation = StringField()

    def __init__(
        self, placeholder, action_id, initial_conversation=None, confirm=None,
    ):
        super().__init__(
            "conversations_select",
            action_id,
            placeholder,
            confirm,
            initial_conversation,
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
            action_id,
            placeholder,
            confirm,
            initial_conversations,
            max_selected_items,
        )


class ChannelsSelect(SelectBase):
    initial_channel = StringField()

    def __init__(
        self, placeholder, action_id, initial_channel=None, confirm=None,
    ):
        super().__init__(
            "channels_select", action_id, placeholder, confirm, initial_channel,
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
            action_id,
            placeholder,
            confirm,
            initial_channels,
            max_selected_items,
        )


class Overflow(Element):
    options = ArrayField(Option, min_items=2, max_items=5)
    confirm = ObjectField(Confirm)

    def __init__(self, action_id, options, confirm=None):
        super().__init__("overflow", action_id, options, confirm)
