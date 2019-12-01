from .components import Component
from .fields import ArrayField, BooleanField, StringField, TextField, UrlField
from .validators import ValidationError


class Text(Component):
    MARKDOWN = "mrkdwn"
    PLAIN = "plain_text"

    text = StringField()
    type = StringField(options=[MARKDOWN, PLAIN])
    emoji = BooleanField()
    verbatim = BooleanField()

    def __init__(self, text, type=MARKDOWN, emoji=None, verbatim=None):
        super().__init__(text, type, emoji, verbatim)

    def validate_emoji(self, emoji):
        if self.type == self.MARKDOWN and emoji:
            raise ValidationError(
                f"'emoji' field is usable only when type is {self.PLAIN}"
            )

    def validate_verbatim(self, verbatim):
        if self.type == self.PLAIN and verbatim:
            raise ValidationError(
                f"'verbatim' field is usable only when type is {self.MARKDOWN}"
            )


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
    options = ArrayField([Option], max_items=100)

    def __init__(self, label, options):
        super().__init__(label, options)
