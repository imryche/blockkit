from .blocks import Block
from .components import Component
from .fields import StringField, ArrayField, BooleanField


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
