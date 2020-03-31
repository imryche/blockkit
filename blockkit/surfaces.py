from .blocks import Block, Input
from .components import Component
from .fields import ArrayField, BooleanField, StringField, TextField, ValidationError


class Message(Component):
    text = StringField()
    blocks = ArrayField(Block)
    attachments = ArrayField()
    thread_ts = StringField()
    mrkdwn = BooleanField()

    def __init__(
        self, text=None, blocks=None, attachments=None, thread_ts=None, mrkdwn=None
    ):
        super().__init__(text, blocks, attachments, thread_ts, mrkdwn)


class Modal(Component):
    type = StringField()
    title = TextField(max_length=24, plain=True)
    blocks = ArrayField(Block)
    close = TextField(max_length=24, plain=True)
    submit = TextField(max_length=24, plain=True)
    private_metadata = StringField(max_length=3000)
    callback_id = StringField(max_length=255)
    clear_on_close = BooleanField()
    notify_on_close = BooleanField()
    external_id = StringField()

    def __init__(
        self,
        title,
        blocks,
        close=None,
        submit=None,
        private_metadata=None,
        callback_id=None,
        clear_on_close=None,
        notify_on_close=None,
        external_id=None,
    ):
        if not submit and any(isinstance(b, Input) for b in blocks):
            raise ValidationError("You have to provide submit.")

        super().__init__(
            "modal",
            title,
            blocks,
            close,
            submit,
            private_metadata,
            callback_id,
            clear_on_close,
            notify_on_close,
            external_id,
        )


class Home(Component):
    type = StringField()
    blocks = ArrayField(Block)
    private_metadata = StringField(max_length=3000)
    callback_id = StringField(max_length=255)
    external_id = StringField()

    def __init__(
        self, blocks, private_metadata=None, callback_id=None, external_id=None,
    ):
        super().__init__(
            "home", blocks, private_metadata, callback_id, external_id,
        )
