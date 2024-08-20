# ruff: noqa: E501
from __future__ import annotations

import functools
import operator
import platform
import sys
from pathlib import Path
from typing import Sequence

import pyromark
import pytest
from pyromark.__main__ import main as pyromark_cli  # noqa: PLC2701

TABLE = """\
| foo | bar |
| --- | --- |
| baz | bim |\
"""

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

BAD_BITS = 2 << 1

TESTDATA = [
    (
        TABLE,
        pyromark.Extensions.ENABLE_TABLES,
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
        pyromark.Extensions.ENABLE_FOOTNOTES,
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
        pyromark.Extensions.ENABLE_STRIKETHROUGH,
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
        pyromark.Extensions.ENABLE_TASKLISTS,
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
        pyromark.Extensions.ENABLE_SMART_PUNCTUATION,
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
        pyromark.Extensions.ENABLE_HEADING_ATTRIBUTES,
        ("--enable-heading-attributes",),
        """\
<h1>text { #id .class1 .class2 myattr, other_attr=myvalue }</h1>
""",
        """<h1 id="id" class="class1 class2" myattr,="" other_attr="myvalue">text</h1>
""",
    ),
    (
        YAML_STYLE_METADATA_BLOCKS,
        pyromark.Extensions.ENABLE_YAML_STYLE_METADATA_BLOCKS,
        ("--enable-yaml-style-metadata-blocks",),
        """\
<hr />
<h2>title: Metadata</h2>
""",
        "",
    ),
    (
        PLUSES_DELIMITED_METADATA_BLOCKS,
        pyromark.Extensions.ENABLE_PLUSES_DELIMITED_METADATA_BLOCKS,
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
        pyromark.Extensions.ENABLE_OLD_FOOTNOTES,
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
<p>In new syntax, this is two footnote definitions.
<sup class="footnote-reference"><a href="#2">2</a></sup>: In old syntax, this is a single footnote definition with two lines.</p>
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
            )
        ),
        functools.reduce(
            operator.or_, pyromark.Extensions.__members__.values()
        ),
        tuple(
            "--" + ext_name.lower().replace("_", "-")
            for ext_name in pyromark.Extensions.__members__
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
""",
        """\
<table><thead><tr><th>foo</th><th>bar</th></tr></thead><tbody>
<tr><td>baz</td><td>bim</td></tr>
</tbody></table>
<div class="footnote-definition" id="1"><sup class="footnote-definition-label">1</sup>
<p>In new syntax, this is two footnote definitions.
<sup class="footnote-reference"><a href="#2">2</a></sup>: In old syntax, this is a single footnote definition with two lines.</p>
</div>
<div class="footnote-definition" id="3"><sup class="footnote-definition-label">3</sup></div>
<pre><code>In new syntax, this is a footnote with two paragraphs.

In old syntax, this is a footnote followed by a code block.
</code></pre>
<p>In new syntax, this undefined footnote definition renders as
literal text <sup class="footnote-reference"><a href="#4">4</a></sup>. In old syntax, it creates a dangling link.</p>
<p><del>Hi</del> Hello, <del>there</del> world!</p>
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
""",
    ),
]


@pytest.mark.skipif(
    sys.version_info == (3, 13, 0, "candidate", 1)
    and platform.system() == "Windows"
    and platform.architecture()[0] == "64bit",
    reason="",
)
@pytest.mark.parametrize(
    ("text", "extensions", "cli_extensions", "res_without_ext", "res_with_ext"),
    TESTDATA,
)
def test_pyromark(
    text: str,
    extensions: pyromark.Extensions,
    cli_extensions: Sequence[str],
    res_without_ext: str,
    res_with_ext: str,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    file = tmp_path / "tmp.md"
    file.write_text(text)

    pyromark_cli((str(file),))
    capture = capsys.readouterr()
    assert not capture.err
    assert (
        pyromark.markdown(text)
        == pyromark.markdown(text, extensions=pyromark.Extensions(0))
        == pyromark.Markdown().convert(text)
        == pyromark.Markdown(extensions=pyromark.Extensions(0)).convert(text)
        == capture.out
        == res_without_ext
    )

    extensions |= BAD_BITS
    pyromark_cli((*cli_extensions, str(file)))
    capture = capsys.readouterr()
    assert not capture.err
    assert (
        pyromark.markdown(text, extensions=extensions)
        == pyromark.Markdown(extensions=extensions).convert(text)
        == capture.out
        == res_with_ext
    )


def test_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit, match=""):
        pyromark_cli(("--version",))
    capture = capsys.readouterr()
    assert not capture.err
    assert capture.out == f"{pyromark.__version__}\n"
