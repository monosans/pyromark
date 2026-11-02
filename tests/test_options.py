# ruff: noqa: E501
from __future__ import annotations

import functools
import io
import operator
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

import pyromark
import pytest
from pyromark._cli import main as pyromark_cli  # noqa: PLC2701

from tests.shared import ALL_OPTIONS, TABLE

FOOTNOTE = """\
[^1]: In new syntax, this is two footnote definitions.
[^2]: In old syntax, this is a single footnote definition with two lines.

[^3]:

    In new syntax, this is a footnote with two paragraphs.

    In old syntax, this is a footnote followed by a code block.

In new syntax, this undefined footnote definition renders as
literal text [^4]. In old syntax, it creates a dangling link.\
"""


STRIKETHROUGH = "~~Hi~~ Hello, ~there~ world!"


TASKLIST = """\
- [ ] foo
- [x] bar\
"""


SMART_PUNCTUATION = """\
'This here a real "quote"'

And -- if you're interested -- some em-dashes. Wait --- she actually said that?

Wow... Becky is so 'mean'!\
"""


HEADING_ATTRIBUTES = "# text { #id .class1 .class2 myattr, other_attr=myvalue }"


YAML_STYLE_METADATA_BLOCKS = """\
---
title: Metadata
---\
"""


PLUSES_DELIMITED_METADATA_BLOCKS = """\
+++
title: Metadata
+++\
"""


DEFINITION_LIST = """\
title 1
  : definition 1
title 2
  : definition 2\
"""


BAD_BITS = (1 << 0) | (1 << 16)


TESTDATA = [
    (
        "$x^2$ and $$y$$",
        pyromark.Options.ENABLE_MATH,
        ("--enable-math",),
        "<p>$x^2$ and $$y$$</p>\n",
        '<p><span class="math math-inline">x^2</span> and <span class="math math-display">y</span></p>\n',
    ),
    (
        "> [!NOTE]\n> note text",
        pyromark.Options.ENABLE_GFM,
        ("--enable-gfm",),
        "<blockquote>\n<p>[!NOTE]\nnote text</p>\n</blockquote>\n",
        '<blockquote class="markdown-alert-note">\n<p>note text</p>\n</blockquote>\n',
    ),
    (
        "x ^sup^ y",
        pyromark.Options.ENABLE_SUPERSCRIPT,
        ("--enable-superscript",),
        "<p>x ^sup^ y</p>\n",
        "<p>x <sup>sup</sup> y</p>\n",
    ),
    (
        "x ~sub~ y",
        pyromark.Options.ENABLE_SUBSCRIPT,
        ("--enable-subscript",),
        "<p>x ~sub~ y</p>\n",
        "<p>x <sub>sub</sub> y</p>\n",
    ),
    (
        "[[foo|bar]] and [[baz]]",
        pyromark.Options.ENABLE_WIKILINKS,
        ("--enable-wikilinks",),
        "<p>[[foo|bar]] and [[baz]]</p>\n",
        '<p><a href="foo">bar</a> and <a href="baz">baz</a></p>\n',
    ),
    (
        TABLE,
        pyromark.Options.ENABLE_TABLES,
        ("--enable-tables",),
        """\
<p>| foo | bar |
| --- | --- |
| baz | bim |</p>
""",
        """\
<table><thead><tr><th>foo</th><th>bar</th></tr></thead><tbody>
<tr><td>baz</td><td>bim</td></tr>
</tbody></table>
""",
    ),
    (
        FOOTNOTE,
        pyromark.Options.ENABLE_FOOTNOTES,
        ("--enable-footnotes",),
        """\
<p>[^1]: In new syntax, this is two footnote definitions.
[^2]: In old syntax, this is a single footnote definition with two lines.</p>
<p>[^3]:</p>
<pre><code>In new syntax, this is a footnote with two paragraphs.

In old syntax, this is a footnote followed by a code block.
</code></pre>
<p>In new syntax, this undefined footnote definition renders as
literal text [^4]. In old syntax, it creates a dangling link.</p>
""",
        """\
<div class="footnote-definition" id="1"><sup class="footnote-definition-label">1</sup>
<p>In new syntax, this is two footnote definitions.</p>
</div>
<div class="footnote-definition" id="2"><sup class="footnote-definition-label">2</sup>
<p>In old syntax, this is a single footnote definition with two lines.</p>
</div>
<div class="footnote-definition" id="3"><sup class="footnote-definition-label">3</sup>
<p>In new syntax, this is a footnote with two paragraphs.</p>
<p>In old syntax, this is a footnote followed by a code block.</p>
</div>
<p>In new syntax, this undefined footnote definition renders as
literal text [^4]. In old syntax, it creates a dangling link.</p>
""",
    ),
    (
        STRIKETHROUGH,
        pyromark.Options.ENABLE_STRIKETHROUGH,
        ("--enable-strikethrough",),
        """\
<p>~~Hi~~ Hello, ~there~ world!</p>
""",
        """\
<p><del>Hi</del> Hello, <del>there</del> world!</p>
""",
    ),
    (
        TASKLIST,
        pyromark.Options.ENABLE_TASKLISTS,
        ("--enable-tasklists",),
        """\
<ul>
<li>[ ] foo</li>
<li>[x] bar</li>
</ul>
""",
        """\
<ul>
<li><input disabled="" type="checkbox"/>
foo</li>
<li><input disabled="" type="checkbox" checked=""/>
bar</li>
</ul>
""",
    ),
    (
        SMART_PUNCTUATION,
        pyromark.Options.ENABLE_SMART_PUNCTUATION,
        ("--enable-smart-punctuation",),
        """\
<p>'This here a real "quote"'</p>
<p>And -- if you're interested -- some em-dashes. Wait --- she actually said that?</p>
<p>Wow... Becky is so 'mean'!</p>
""",
        """\
<p>‘This here a real “quote”’</p>
<p>And – if you’re interested – some em-dashes. Wait — she actually said that?</p>
<p>Wow… Becky is so ‘mean’!</p>
""",
    ),
    (
        HEADING_ATTRIBUTES,
        pyromark.Options.ENABLE_HEADING_ATTRIBUTES,
        ("--enable-heading-attributes",),
        """\
<h1>text { #id .class1 .class2 myattr, other_attr=myvalue }</h1>
""",
        """<h1 id="id" class="class1 class2" myattr,="" other_attr="myvalue">text</h1>
""",
    ),
    (
        YAML_STYLE_METADATA_BLOCKS,
        pyromark.Options.ENABLE_YAML_STYLE_METADATA_BLOCKS,
        ("--enable-yaml-style-metadata-blocks",),
        """\
<hr />
<h2>title: Metadata</h2>
""",
        "",
    ),
    (
        PLUSES_DELIMITED_METADATA_BLOCKS,
        pyromark.Options.ENABLE_PLUSES_DELIMITED_METADATA_BLOCKS,
        ("--enable-pluses-delimited-metadata-blocks",),
        """\
<p>+++
title: Metadata
+++</p>
""",
        "",
    ),
    (
        FOOTNOTE,
        pyromark.Options.ENABLE_OLD_FOOTNOTES,
        ("--enable-old-footnotes",),
        """\
<p>[^1]: In new syntax, this is two footnote definitions.
[^2]: In old syntax, this is a single footnote definition with two lines.</p>
<p>[^3]:</p>
<pre><code>In new syntax, this is a footnote with two paragraphs.

In old syntax, this is a footnote followed by a code block.
</code></pre>
<p>In new syntax, this undefined footnote definition renders as
literal text [^4]. In old syntax, it creates a dangling link.</p>
""",
        """\
<div class="footnote-definition" id="1"><sup class="footnote-definition-label">1</sup>
<p>In new syntax, this is two footnote definitions.</p>
</div>
<div class="footnote-definition" id="2"><sup class="footnote-definition-label">2</sup>
<p>In old syntax, this is a single footnote definition with two lines.</p>
</div>
<div class="footnote-definition" id="3"><sup class="footnote-definition-label">3</sup></div>
<pre><code>In new syntax, this is a footnote with two paragraphs.

In old syntax, this is a footnote followed by a code block.
</code></pre>
<p>In new syntax, this undefined footnote definition renders as
literal text <sup class="footnote-reference"><a href="#4">4</a></sup>. In old syntax, it creates a dangling link.</p>
""",
    ),
    (
        DEFINITION_LIST,
        pyromark.Options.ENABLE_DEFINITION_LIST,
        ("--enable-definition-list",),
        """\
<p>title 1
: definition 1
title 2
: definition 2</p>
""",
        """\
<dl>
<dt>title 1</dt>
<dd>definition 1
title 2</dd>
<dd>definition 2</dd>
</dl>
""",
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
                YAML_STYLE_METADATA_BLOCKS,
                PLUSES_DELIMITED_METADATA_BLOCKS,
                DEFINITION_LIST,
            )
        ),
        functools.reduce(operator.or_, pyromark.Options.__members__.values()),
        tuple(
            "--" + option_name.lower().replace("_", "-")
            for option_name in pyromark.Options.__members__
        ),
        """\
<p>| foo | bar |
| --- | --- |
| baz | bim |</p>
<p>[^1]: In new syntax, this is two footnote definitions.
[^2]: In old syntax, this is a single footnote definition with two lines.</p>
<p>[^3]:</p>
<pre><code>In new syntax, this is a footnote with two paragraphs.

In old syntax, this is a footnote followed by a code block.
</code></pre>
<p>In new syntax, this undefined footnote definition renders as
literal text [^4]. In old syntax, it creates a dangling link.</p>
<p>~~Hi~~ Hello, ~there~ world!</p>
<ul>
<li>[ ] foo</li>
<li>[x] bar</li>
</ul>
<p>'This here a real "quote"'</p>
<p>And -- if you're interested -- some em-dashes. Wait --- she actually said that?</p>
<p>Wow... Becky is so 'mean'!</p>
<h1>text { #id .class1 .class2 myattr, other_attr=myvalue }</h1>
<hr />
<h2>title: Metadata</h2>
<p>+++
title: Metadata
+++</p>
<p>title 1
: definition 1
title 2
: definition 2</p>
""",
        """\
<table><thead><tr><th>foo</th><th>bar</th></tr></thead><tbody>
<tr><td>baz</td><td>bim</td></tr>
</tbody></table>
<div class="footnote-definition" id="1"><sup class="footnote-definition-label">1</sup>
<p>In new syntax, this is two footnote definitions.</p>
</div>
<div class="footnote-definition" id="2"><sup class="footnote-definition-label">2</sup>
<p>In old syntax, this is a single footnote definition with two lines.</p>
</div>
<div class="footnote-definition" id="3"><sup class="footnote-definition-label">3</sup></div>
<pre><code>In new syntax, this is a footnote with two paragraphs.

In old syntax, this is a footnote followed by a code block.
</code></pre>
<p>In new syntax, this undefined footnote definition renders as
literal text <sup class="footnote-reference"><a href="#4">4</a></sup>. In old syntax, it creates a dangling link.</p>
<p><del>Hi</del> Hello, <sub>there</sub> world!</p>
<ul>
<li><input disabled="" type="checkbox"/>
foo</li>
<li><input disabled="" type="checkbox" checked=""/>
bar</li>
</ul>
<p>‘This here a real “quote”’</p>
<p>And – if you’re interested – some em-dashes. Wait — she actually said that?</p>
<p>Wow… Becky is so ‘mean’!</p>
<h1 id="id" class="class1 class2" myattr,="" other_attr="myvalue">text</h1>
<dl>
<dt>title 1</dt>
<dd>definition 1
title 2</dd>
<dd>definition 2</dd>
</dl>
""",
    ),
]


@pytest.mark.parametrize(
    ("markdown", "options", "cli_options", "result_without_options", "result_with_options"),
    TESTDATA,
)
def test_pyromark(
    markdown: str,
    options: pyromark.Options,
    cli_options: Sequence[str],
    result_without_options: str,
    result_with_options: str,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    file = tmp_path / "tmp.md"
    file.write_text(markdown, encoding="utf-8")

    pyromark_cli((str(file),))
    capture = capsys.readouterr()
    assert not capture.err
    assert (
        pyromark.html(markdown)
        == pyromark.html(markdown, options=pyromark.Options(0))
        == pyromark.Markdown().html(markdown)
        == pyromark.Markdown(options=pyromark.Options(0)).html(markdown)
        == capture.out
        == result_without_options
    )

    pyromark_cli((*cli_options, str(file)))
    capture = capsys.readouterr()
    assert not capture.err
    assert (
        pyromark.html(markdown, options=options)
        == pyromark.Markdown(options=options).html(markdown)
        == capture.out
        == result_with_options
    )


@pytest.mark.parametrize("value", [1 << 32, 1 << 40, 2**64], ids=str)
def test_options_wider_than_32_bits_are_rejected(value: int) -> None:
    wide = pyromark.Options(value)
    with pytest.raises(OverflowError):
        pyromark.html(TABLE, options=wide)
    with pytest.raises(OverflowError):
        pyromark.Markdown(options=wide)


UNKNOWN_BIT_ENTRY_POINTS: Mapping[str, Callable[[pyromark.Options], object]] = {
    "html": lambda options: pyromark.html(TABLE, options=options),
    "events": lambda options: pyromark.events(TABLE, options=options),
    "events_with_range": lambda options: pyromark.events_with_range(TABLE, options=options),
    "write_html": lambda options: pyromark.write_html(TABLE, io.BytesIO(), options=options),
    "reference_definitions": lambda options: pyromark.reference_definitions(TABLE, options=options),
    "Markdown": lambda options: pyromark.Markdown(options=options),
}


@pytest.mark.parametrize("call", UNKNOWN_BIT_ENTRY_POINTS.values(), ids=UNKNOWN_BIT_ENTRY_POINTS)
@pytest.mark.parametrize(
    "options",
    [pyromark.Options(BAD_BITS), pyromark.Options(BAD_BITS) | ALL_OPTIONS],
    ids=["alone", "with-valid-bits"],
)
def test_options_unknown_bits_are_rejected(
    call: Callable[[pyromark.Options], object], options: pyromark.Options
) -> None:
    with pytest.raises(
        ValueError, match=r"^options has bits pulldown-cmark does not define: 0x10001$"
    ):
        call(options)


def test_options_old_footnotes_is_composite() -> None:
    old = pyromark.Options.ENABLE_OLD_FOOTNOTES
    assert pyromark.Options.ENABLE_FOOTNOTES in old
    assert int(old) == (1 << 9) | (1 << 2)
