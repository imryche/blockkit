from .components import Component
from .fields import (
    ArrayField,
    BooleanField,
    StringField,
    TextField,
    UrlField,
    ValidationError,
)


class Text(Component):
    markdown = "mrkdwn"
    plain = "plain_text"

    text = StringField()
    type = StringField(options=[markdown, plain])
    emoji = BooleanField()
    verbatim = BooleanField()

    def __init__(self, text, type_, emoji=None, verbatim=None):
        super().__init__(text, type_, emoji, verbatim)

        if type_ == self.markdown and emoji:
            raise ValidationError(
                f"'emoji' field isn't allowed when type is \"{self.plain}\"."
            )

        if type_ == self.plain and verbatim:
            raise ValidationError(
                f"'verbatim' field isn't allowd when type is \"{self.markdown}\"."
            )


class MarkdownText(Text):
    def __init__(self, text, verbatim=None):
        super().__init__(text, self.markdown, None, verbatim)


class PlainText(Text):
    def __init__(self, text, emoji=None):
        super().__init__(text, self.plain, emoji, None)


class Confirm(Component):
    title = TextField(max_length=100, plain=True)
    text = TextField(max_length=300)
    confirm = TextField(max_length=30, plain=True)
    deny = TextField(max_length=30, plain=True)

    def __init__(self, title, text, confirm, deny):
        super().__init__(title, text, confirm, deny)


class Option(Component):
    text = TextField(max_length=75, plain=True)
    value = StringField(max_length=75)
    url = UrlField(max_length=3000)

    def __init__(self, text, value, url=None):
        super().__init__(text, value, url)


class OptionGroup(Component):
    label = TextField(max_length=75, plain=True)
    options = ArrayField(Option, max_items=100)

    def __init__(self, label, options):
        super().__init__(label, options)


class Filter(Component):
    include_options = ("im", "mpim", "private", "public")

    include = ArrayField(str)
    exclude_external_shared_channels = BooleanField()
    exclude_bot_users = BooleanField()

    def __init__(
        self,
        include=None,
        exclude_external_shared_channels=None,
        exclude_bot_users=False,
    ):
        if not any((include, exclude_external_shared_channels, exclude_bot_users)):
            raise ValidationError("You should provide at least one argument.")

        if set(include) - set(self.include_options):
            raise ValidationError("Incorrect include options.")

        super().__init__(include, exclude_external_shared_channels, exclude_bot_users)
