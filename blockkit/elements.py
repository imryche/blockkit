from blockkit.fields import (
    ArrayField,
    ObjectField,
    DateField,
    IntegerField,
    StringField,
    TextField,
    UrlField,
    BooleanField,
    ValidationError,
)

from . import Option, OptionGroup, Confirm, Filter
from .components import Component


class Element(Component):
    type = StringField()


class ActionableElement(Element):
    action_id = StringField(max_length=255)


class Button(ActionableElement):
    primary = "primary"
    danger = "danger"

    text = TextField(plain=True, max_length=75)
    url = UrlField(max_length=3000)
    value = StringField(max_length=2000)
    style = StringField(options=[primary, danger])
    confirm = ObjectField(Confirm)

    def __init__(
        self, text, action_id=None, url=None, value=None, style=None, confirm=None
    ):
        if not any((action_id, url)):
            raise ValidationError("You should provide either action_id or url")

        super().__init__("button", action_id, text, url, value, style, confirm)


class DatePicker(ActionableElement):
    placeholder = TextField(plain=True, max_length=150)
    initial_date = DateField()
    confirm = ObjectField(Confirm)

    def __init__(self, action_id, placeholder=None, initial_date=None, confirm=None):
        super().__init__("datepicker", action_id, placeholder, initial_date, confirm)


class Image(Element):
    type = StringField()
    image_url = UrlField()
    alt_text = StringField()

    def __init__(self, image_url, alt_text):
        super().__init__("image", image_url, alt_text)


class Select(ActionableElement):
    placeholder = TextField(plain=True, max_length=150)
    confirm = ObjectField(Confirm)


class StaticSelectBase(Select):
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
            raise ValidationError("You can specify either options or option_groups.")

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
            raise ValidationError("You can specify either options or option_groups.")

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


class ExternalSelectBase(Select):
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


class UsersSelect(Select):
    initial_user = StringField()

    def __init__(
        self, placeholder, action_id, initial_user=None, confirm=None,
    ):
        super().__init__(
            "users_select", action_id, placeholder, confirm, initial_user,
        )


class MultiUsersSelect(Select):
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


class ConversationsSelect(Select):
    initial_conversation = StringField()
    filter = ObjectField(Filter)

    def __init__(
        self,
        placeholder,
        action_id,
        initial_conversation=None,
        confirm=None,
        filter=None,
    ):
        super().__init__(
            "conversations_select",
            action_id,
            placeholder,
            confirm,
            initial_conversation,
            filter,
        )


class MultiConversationsSelect(Select):
    initial_conversations = ArrayField(str)
    max_selected_items = IntegerField()
    filter = ObjectField(Filter)

    def __init__(
        self,
        placeholder,
        action_id,
        initial_conversations=None,
        confirm=None,
        max_selected_items=None,
        filter=None,
    ):
        super().__init__(
            "multi_conversations_select",
            action_id,
            placeholder,
            confirm,
            initial_conversations,
            max_selected_items,
            filter,
        )


class ChannelsSelect(Select):
    initial_channel = StringField()

    def __init__(
        self, placeholder, action_id, initial_channel=None, confirm=None,
    ):
        super().__init__(
            "channels_select", action_id, placeholder, confirm, initial_channel,
        )


class MultiChannelsSelect(Select):
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


class Overflow(ActionableElement):
    options = ArrayField(Option, min_items=1, max_items=5)
    confirm = ObjectField(Confirm)

    def __init__(self, action_id, options, confirm=None):
        super().__init__("overflow", action_id, options, confirm)


class PlainTextInput(ActionableElement):
    placeholder = TextField(plain=True, max_length=150)
    initial_value = StringField()
    multiline = BooleanField()
    min_length = IntegerField(max_value=3000)
    max_length = IntegerField()

    def __init__(
        self,
        action_id,
        placeholder=None,
        initial_value=None,
        multiline=None,
        min_length=None,
        max_length=None,
    ):
        super().__init__(
            "plain_text_input",
            action_id,
            placeholder,
            initial_value,
            multiline,
            min_length,
            max_length,
        )


class RadioButtons(ActionableElement):
    options = ArrayField(Option)
    initial_option = ObjectField(Option)
    confirm = ObjectField(Confirm)

    def __init__(self, action_id, options, initial_option=None, confirm=None):
        super().__init__("radio_buttons", action_id, options, initial_option, confirm)


class Checkboxes(ActionableElement):
    options = ArrayField(Option)
    initial_options = ArrayField(Option)
    confirm = ObjectField(Confirm)

    def __init__(self, action_id, options, initial_options=None, confirm=None):
        super().__init__("checkboxes", action_id, options, initial_options, confirm)
