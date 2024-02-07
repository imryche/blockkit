from typing import List, Optional, Union

from pydantic import Field, model_validator

from blockkit.blocks import (
    Actions,
    Context,
    Divider,
    Header,
    ImageBlock,
    Input,
    RichText,
    Section,
)
from blockkit.components import Component
from blockkit.objects import PlainText
from blockkit.validators import validate_text_length, validator

__all__ = ["Home", "Message", "Modal", "WorkflowStep"]

Block = Union[Actions, Context, Divider, Header, ImageBlock, Input, RichText, Section]


class View(Component):
    blocks: List[Block] = Field(..., min_length=1, max_length=100)
    private_metadata: Optional[str] = Field(None, min_length=1, max_length=3000)
    callback_id: Optional[str] = Field(None, min_length=1, max_length=255)


class Home(View):
    type: str = "home"
    external_id: Optional[str] = Field(None, min_length=1, max_length=255)

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


class Modal(View):
    type: str = "modal"
    title: Union[PlainText, str]
    close: Union[PlainText, str, None] = None
    submit: Union[PlainText, str, None] = None
    clear_on_close: Optional[bool] = None
    notify_on_close: Optional[bool] = None
    external_id: Optional[str] = Field(None, min_length=1, max_length=255)
    submit_disabled: Optional[bool] = None

    def __init__(
        self,
        *,
        title: Union[PlainText, str],
        blocks: List[Block],
        close: Union[PlainText, str, None] = None,
        submit: Union[PlainText, str, None] = None,
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

    _validate_title = validator("title", validate_text_length, max_length=24)
    _validate_close = validator("close", validate_text_length, max_length=24)
    _validate_submit = validator("submit", validate_text_length, max_length=24)

    @model_validator(mode="after")
    def _validate_values(self) -> "Modal":
        if self.blocks and not self.submit and Input in (type(b) for b in self.blocks):
            raise ValueError("submit is required when an Input is within blocks")
        return self


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
    text: Optional[str] = Field(None, min_length=1, max_length=3000)
    blocks: Optional[List[Block]] = Field(None, min_length=1, max_length=50)

    def __init__(
        self, *, text: Optional[str] = None, blocks: Optional[List[Block]] = None
    ):
        super().__init__(text=text, blocks=blocks)

    @model_validator(mode="after")
    def _validate_values(self) -> "Message":
        if not self.text and not self.blocks:
            raise ValueError("You must provide either text or blocks")
        return self
