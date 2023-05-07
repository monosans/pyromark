from __future__ import annotations

from typing import TYPE_CHECKING, Any, Type

import pyromark
import pytest

if TYPE_CHECKING:
    from pyromark import _Extension

TABLE = """\
| a   | b   |
| --- | --- |
| c   | d   |\
"""

FOOTNOTE = """\
Here's a sentence with a footnote. [^1]

[^1]: This is the footnote.\
"""

STRIKETHROUGH = "~~The world is flat.~~"

TASKLIST = """\
- [x] Write the press release
- [ ] Update the website
- [ ] Contact the media\
"""

SMART_PUNCTUATION = """\
'This here a real "quote"'

And -- if you're interested -- some em-dashes. Wait --- she actually said that?

Wow... Becky is so 'mean'!\
"""

HEADING_ATTRIBUTES = "# text { #id .class1 .class2 }"


@pytest.mark.parametrize(
    ("extensions", "exc", "exc_str"),
    [
        (("asdf",), ValueError, "unknown extension: 'asdf'"),
        (
            set(),
            TypeError,
            "argument 'extensions': 'set' object cannot be converted to 'Sequence'",
        ),
        ("", TypeError, "argument 'extensions': Can't extract `str` to `Vec`"),
    ],
)
def test_wrong_extensions(
    extensions: Any, exc: Type[BaseException], exc_str: str
) -> None:
    with pytest.raises(exc, match=exc_str):
        pyromark.Markdown(extensions=extensions)


@pytest.mark.parametrize(
    ("text", "extension", "res_without_ext", "res_with_ext"),
    [
        (
            TABLE,
            "tables",
            "<p>| a   | b   |\n| --- | --- |\n| c   | d   |</p>\n",
            "<table><thead><tr><th>a</th><th>b</th></tr></thead><tbody>\n<tr><td>c</td><td>d</td></tr>\n</tbody></table>\n",
        ),
        (
            FOOTNOTE,
            "footnotes",
            (
                "<p>Here's a sentence with a footnote. [^1]</p>\n<p>[^1]: This is the"
                " footnote.</p>\n"
            ),
            (
                "<p>Here's a sentence with a footnote. <sup"
                ' class="footnote-reference"><a href="#1">1</a></sup></p>\n<div'
                ' class="footnote-definition" id="1"><sup'
                ' class="footnote-definition-label">1</sup>\n<p>This is the'
                " footnote.</p>\n</div>\n"
            ),
        ),
        (
            STRIKETHROUGH,
            "strikethrough",
            "<p>~~The world is flat.~~</p>\n",
            "<p><del>The world is flat.</del></p>\n",
        ),
        (
            TASKLIST,
            "tasklists",
            (
                "<ul>\n<li>[x] Write the press release</li>\n<li>[ ] Update the"
                " website</li>\n<li>[ ] Contact the media</li>\n</ul>\n"
            ),
            (
                '<ul>\n<li><input disabled="" type="checkbox" checked=""/>\nWrite the'
                ' press release</li>\n<li><input disabled="" type="checkbox"/>\nUpdate'
                ' the website</li>\n<li><input disabled="" type="checkbox"/>\nContact'
                " the media</li>\n</ul>\n"
            ),
        ),
        (
            SMART_PUNCTUATION,
            "smart_punctuation",
            (
                "<p>'This here a real &quot;quote&quot;'</p>\n<p>And -- if you're"
                " interested -- some em-dashes. Wait --- she actually said"
                " that?</p>\n<p>Wow... Becky is so 'mean'!</p>\n"
            ),
            (
                "<p>‘This here a real “quote”’</p>\n<p>And – if you’re interested –"
                " some em-dashes. Wait — she actually said that?</p>\n<p>Wow… Becky is"
                " so ‘mean’!</p>\n"
            ),
        ),
        (
            HEADING_ATTRIBUTES,
            "heading_attributes",
            "<h1>text { #id .class1 .class2 }</h1>\n",
            '<h1 id="id" class="class1 class2">text</h1>\n',
        ),
    ],
)
def test_extensions(
    text: str, extension: _Extension, res_without_ext: str, res_with_ext: str
) -> None:
    assert (
        pyromark.markdown(text) == pyromark.Markdown().convert(text) == res_without_ext
    )
    assert (
        pyromark.markdown(text, extensions=(extension,))
        == pyromark.Markdown(extensions=(extension,)).convert(text)
        == res_with_ext
    )
