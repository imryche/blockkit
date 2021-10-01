from typing import List, Optional, Union

from pydantic import root_validator

from blockkit.blocks import (
    Actions,
    Context,
    Divider,
    Header,
    ImageBlock,
    Input,
    Section,
)
from blockkit.components import Component
from blockkit.objects import PlainText
from blockkit.validators import (
    validate_list_size,
    validate_string_length,
    validate_text_length,
    validator,
)

__all__ = ["Home", "Message", "Modal", "WorkflowStep"]

Block = Union[Actions, Context, Divider, Header, ImageBlock, Input, Section]


class View(Component):
    blocks: List[Block]
    private_metadata: Optional[str] = None
    callback_id: Optional[str] = None

    _validate_blocks = validator("blocks", validate_list_size, min_len=1, max_len=100)
    _validate_private_metadata = validator(
        "private_metadata", validate_string_length, max_len=3000
    )
    _validate_callback_id = validator(
        "callback_id", validate_string_length, max_len=255
    )


class Home(View):
    type: str = "home"
    external_id: Optional[str] = None

    def __init__(
        self,
        *,
        blocks: List[Block],
        private_metadata: Optional[str] = None,
        callback_id: Optional[str] = None,
        external_id: Optional[str] = None,
    ):
        super().__init__(
            blocks=blocks,
            private_metadata=private_metadata,
            callback_id=callback_id,
            external_id=external_id,
        )

    _validate_external_id = validator(
        "external_id", validate_string_length, max_len=255
    )


class Modal(View):
    type: str = "modal"
    title: PlainText
    close: Optional[PlainText] = None
    submit: Optional[PlainText] = None
    clear_on_close: Optional[bool] = None
    notify_on_close: Optional[bool] = None
    external_id: Optional[str] = None
    submit_disabled: Optional[bool] = None

    def __init__(
        self,
        *,
        title: PlainText,
        blocks: List[Block],
        close: Optional[PlainText] = None,
        submit: Optional[PlainText] = None,
        private_metadata: Optional[str] = None,
        callback_id: Optional[str] = None,
        clear_on_close: Optional[bool] = None,
        notify_on_close: Optional[bool] = None,
        external_id: Optional[str] = None,
        submit_disabled: Optional[bool] = None,
    ):
        super(View, self).__init__(
            title=title,
            blocks=blocks,
            close=close,
            submit=submit,
            private_metadata=private_metadata,
            callback_id=callback_id,
            clear_on_close=clear_on_close,
            notify_on_close=notify_on_close,
            external_id=external_id,
            submit_disabled=submit_disabled,
        )

    _validate_title = validator("title", validate_text_length, max_len=24)
    _validate_close = validator("close", validate_text_length, max_len=24)
    _validate_submit = validator("submit", validate_text_length, max_len=24)
    _validate_external_id = validator(
        "external_id", validate_string_length, max_len=255
    )

    @root_validator
    def _validate_values(cls, values):
        blocks = values.get("blocks")
        submit = values.get("submit")

        if blocks and not submit and Input in (
            type(b) for b in values["blocks"]
        ):
            raise ValueError("submit is required when an Input is within blocks")
        return values


class WorkflowStep(View):
    type: str = "workflow_step"
    submit_disabled: Optional[bool] = None

    def __init__(
        self,
        *,
        blocks: List[Block],
        private_metadata: Optional[str] = None,
        callback_id: Optional[str] = None,
        submit_disabled: Optional[bool] = None,
    ):
        super(View, self).__init__(
            blocks=blocks,
            private_metadata=private_metadata,
            callback_id=callback_id,
            submit_disabled=submit_disabled,
        )


class Message(Component):
    blocks: List[Block]

    def __init__(self, *, blocks: List[Block]):
        super().__init__(blocks=blocks)

    _validate_blocks = validator("blocks", validate_list_size, min_len=1, max_len=50)
