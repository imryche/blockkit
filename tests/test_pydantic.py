import json
from typing import Optional, Union

from pydantic import BaseModel, StrictBool, StrictStr


class MarkdownText(BaseModel):
    type: str = "mrkdwn"
    text: StrictStr
    verbatim: StrictBool = None

    def __init__(self, *, text: str, verbatim: bool = None) -> None:
        super().__init__(text=text, verbatim=verbatim)


class PlainText(BaseModel):
    type: str = "plain_text"
    text: StrictStr
    emoji: StrictBool = None

    def __init__(self, *, text: str, verbatim: bool = None) -> None:
        super().__init__(text=text, verbatim=verbatim)


class Section(BaseModel):
    type: str = "section"
    text: Optional[Union[MarkdownText, str]] = None

    def __init__(
        self, *, text: Optional[Union[MarkdownText, PlainText]] = None
    ) -> None:
        super().__init__(text=text)


def test_builds_markdown_text():
    payload = MarkdownText(text="123", verbatim=True).dict()
    print(payload)


def test_builds_section():
    payload = Section(text=MarkdownText(text="foo bar")).dict(exclude_none=True)
    print(json.dumps(payload, indent=4))
