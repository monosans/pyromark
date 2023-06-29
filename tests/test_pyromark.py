from __future__ import annotations

import pyromark
import pytest

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

BAD_BITS = 2 << 1

TESTDATA = [
    (
        TABLE,
        pyromark.Extensions.ENABLE_TABLES,
        "<p>| a   | b   |\n| --- | --- |\n| c   | d   |</p>\n",
        "<table><thead><tr><th>a</th><th>b</th></tr></thead><tbody>\n<tr><td>c</td><td>d</td></tr>\n</tbody></table>\n",
    ),
    (
        FOOTNOTE,
        pyromark.Extensions.ENABLE_FOOTNOTES,
        (
            "<p>Here's a sentence with a footnote. [^1]</p>\n<p>[^1]: This"
            " is the footnote.</p>\n"
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
        pyromark.Extensions.ENABLE_STRIKETHROUGH,
        "<p>~~The world is flat.~~</p>\n",
        "<p><del>The world is flat.</del></p>\n",
    ),
    (
        TASKLIST,
        pyromark.Extensions.ENABLE_TASKLISTS,
        (
            "<ul>\n<li>[x] Write the press release</li>\n<li>[ ] Update the"
            " website</li>\n<li>[ ] Contact the media</li>\n</ul>\n"
        ),
        (
            '<ul>\n<li><input disabled="" type="checkbox"'
            ' checked=""/>\nWrite the press release</li>\n<li><input'
            ' disabled="" type="checkbox"/>\nUpdate the'
            ' website</li>\n<li><input disabled=""'
            ' type="checkbox"/>\nContact the media</li>\n</ul>\n'
        ),
    ),
    (
        SMART_PUNCTUATION,
        pyromark.Extensions.ENABLE_SMART_PUNCTUATION,
        (
            "<p>'This here a real &quot;quote&quot;'</p>\n<p>And -- if"
            " you're interested -- some em-dashes. Wait --- she actually"
            " said that?</p>\n<p>Wow... Becky is so 'mean'!</p>\n"
        ),
        (
            "<p>‘This here a real “quote”’</p>\n<p>And – if you’re"
            " interested – some em-dashes. Wait — she actually said"
            " that?</p>\n<p>Wow… Becky is so ‘mean’!</p>\n"
        ),
    ),
    (
        HEADING_ATTRIBUTES,
        pyromark.Extensions.ENABLE_HEADING_ATTRIBUTES,
        "<h1>text { #id .class1 .class2 }</h1>\n",
        '<h1 id="id" class="class1 class2">text</h1>\n',
    ),
    (
        "\n\n".join(  # noqa: FLY002
            (
                TABLE,
                FOOTNOTE,
                STRIKETHROUGH,
                TASKLIST,
                SMART_PUNCTUATION,
                HEADING_ATTRIBUTES,
            )
        ),
        (
            pyromark.Extensions.ENABLE_TABLES
            | pyromark.Extensions.ENABLE_FOOTNOTES
            | pyromark.Extensions.ENABLE_STRIKETHROUGH
            | pyromark.Extensions.ENABLE_TASKLISTS
            | pyromark.Extensions.ENABLE_SMART_PUNCTUATION
            | pyromark.Extensions.ENABLE_HEADING_ATTRIBUTES
        ),
        (
            "<p>| a   | b   |\n| --- | --- |\n| c   | d   |</p>\n<p>Here's"
            " a sentence with a footnote. [^1]</p>\n<p>[^1]: This is the"
            " footnote.</p>\n<p>~~The world is flat.~~</p>\n<ul>\n<li>[x]"
            " Write the press release</li>\n<li>[ ] Update the"
            " website</li>\n<li>[ ] Contact the media</li>\n</ul>\n<p>'This"
            " here a real &quot;quote&quot;'</p>\n<p>And -- if you're"
            " interested -- some em-dashes. Wait --- she actually said"
            " that?</p>\n<p>Wow... Becky is so 'mean'!</p>\n<h1>text { #id"
            " .class1 .class2 }</h1>\n"
        ),
        (
            "<table><thead><tr><th>a</th><th>b</th></tr></thead><tbody>\n<tr><td>c</td><td>d</td></tr>\n</tbody></table>\n<p>Here’s"
            ' a sentence with a footnote. <sup class="footnote-reference"><a'
            ' href="#1">1</a></sup></p>\n<div class="footnote-definition"'
            ' id="1"><sup class="footnote-definition-label">1</sup>\n<p>This is'
            " the footnote.</p>\n</div>\n<p><del>The world is"
            ' flat.</del></p>\n<ul>\n<li><input disabled="" type="checkbox"'
            ' checked=""/>\nWrite the press release</li>\n<li><input'
            ' disabled="" type="checkbox"/>\nUpdate the'
            ' website</li>\n<li><input disabled="" type="checkbox"/>\nContact'
            " the media</li>\n</ul>\n<p>‘This here a real “quote”’</p>\n<p>And"
            " – if you’re interested – some em-dashes. Wait — she actually said"
            ' that?</p>\n<p>Wow… Becky is so ‘mean’!</p>\n<h1 id="id"'
            ' class="class1 class2">text</h1>\n'
        ),
    ),
]


@pytest.mark.parametrize(
    ("text", "extensions", "res_without_ext", "res_with_ext"), TESTDATA
)
def test_extensions(
    text: str,
    extensions: pyromark.Extensions,
    res_without_ext: str,
    res_with_ext: str,
) -> None:
    assert (
        pyromark.markdown(text)
        == pyromark.markdown(text, extensions=pyromark.Extensions(0))
        == pyromark.Markdown().convert(text)
        == pyromark.Markdown(extensions=pyromark.Extensions(0)).convert(text)
        == res_without_ext
    )
    extensions |= BAD_BITS
    assert (
        pyromark.markdown(text, extensions=extensions)
        == pyromark.Markdown(extensions=extensions).convert(text)
        == res_with_ext
    )
