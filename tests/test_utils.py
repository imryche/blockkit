import pytest

from blockkit.utils import is_md


@pytest.mark.parametrize(
    "text, is_markdown",
    [
        ("_italic_", True),
        ("*bold*", True),
        ("~strike~", True),
        ("_*~italic bold strike~*_", True),
        (">block quote", True),
        (
            "unquoted text\n>quoted text\n>quoted text\nunquoted text",
            True,
        ),
        ("text with `inline *code*` in it", True),
        ("```multiline\ncode block```", True),
        ("text with a url <http://example.com>", True),
        ("text with a <http://example.com|url>", True),
        ("text with an email <mailto:alice@wonderland.com|link>", True),
        ("please, join <#C02BBR2CGCE>", True),
        ("hello, <@U049QQHEZC7>", True),
        ("hey, <!here>", True),
        # plain text
        ("basic text", False),
        ("not*bold*yet", False),
        ("- item 1\n- item 2\n- item 3", False),
        (":white_check_mark: *You're in*. We'll remind you 10 minutes before", True),
    ],
)
def test_is_md(text, is_markdown):
    assert is_md(text) == is_markdown
