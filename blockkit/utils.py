import re


def is_md(text):
    patterns = [
        # Bold, italic, strikethrough, inline code: *text*, _text_, ~text~, `text`
        r"(?:^|\W)([*_~`])([^\1]+)\1(?:$|\W)",
        # Code block: line starting with ```
        r"^```",
        # Quote: line starting with >
        r"^>",
        # Links and mentions: <http...>, <@USERID>, <#CHANNELID|channel>
        r"<[^>]+>",
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.MULTILINE):
            return True
    return False
