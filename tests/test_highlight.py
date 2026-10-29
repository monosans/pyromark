from __future__ import annotations

import ast
import gc
import re
import weakref

import pyromark
import pytest

from tests.shared import (
    CODE_BLOCKS,
    CPYTHON_ONLY,
    RENDERS_PER_THREAD,
    THREADS,
    render_on_threads,
)

CODE_BLOCKS_COUNT = 3


CODE_BLOCKS_PLAIN = """<pre><code class="language-python">x = 1
</code></pre>
<pre><code>indented
</code></pre>
<pre><code class="language-unknown-language">y = 2
</code></pre>
"""


def test_highlight_disabled() -> None:
    assert (
        pyromark.html(CODE_BLOCKS, highlight=None)
        == pyromark.Markdown(highlight=None).html(CODE_BLOCKS)
        == pyromark.html(CODE_BLOCKS)
        == CODE_BLOCKS_PLAIN
    )


@pytest.mark.parametrize(
    "highlight",
    [pyromark.Theme.INSPIRED_GITHUB, pyromark.Theme.BASE16_OCEAN_DARK],
)
def test_highlight_syntect(highlight: pyromark.Theme) -> None:
    html = pyromark.html(CODE_BLOCKS, highlight=highlight)
    assert html == pyromark.Markdown(highlight=highlight).html(CODE_BLOCKS)
    assert html.count("<pre style=") == CODE_BLOCKS_COUNT
    assert "<code" not in html
    text = re.sub(r"<[^>]+>", "", html)
    assert "x = 1" in text
    assert "indented" in text
    assert "y = 2" in text
    assert pyromark.html("# Hi", highlight=highlight) == "<h1>Hi</h1>\n"


def test_highlight_theme_changes_output() -> None:
    light = pyromark.html(CODE_BLOCKS, highlight=pyromark.Theme.INSPIRED_GITHUB)
    dark = pyromark.html(
        CODE_BLOCKS, highlight=pyromark.Theme.BASE16_OCEAN_DARK
    )
    assert light != dark
    assert "background-color:#ffffff" in light
    assert "background-color:#2b303b" in dark


def test_highlight_unknown_theme() -> None:
    with pytest.raises(ValueError, match=r"unknown highlighting theme"):
        pyromark.html(CODE_BLOCKS, highlight="no-such-theme")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match=r"unknown highlighting theme"):
        pyromark.Markdown(highlight="no-such-theme")  # type: ignore[arg-type]


@pytest.mark.parametrize("highlight", [0, 1, 1.5, b"x", [], {}])
def test_highlight_invalid_type(highlight: object) -> None:
    with pytest.raises(TypeError, match=r"^highlight must be"):
        pyromark.html(CODE_BLOCKS, highlight=highlight)  # type: ignore[arg-type]


def test_highlight_callback() -> None:
    calls: list[tuple[str | None, str]] = []

    def callback(language: str | None, code: str) -> str:
        calls.append((language, code))
        return f"<div lang={language}>{code.strip()}</div>"

    expected = (
        "<div lang=python>x = 1</div>\n"
        "<div lang=None>indented</div>\n"
        "<div lang=unknown-language>y = 2</div>\n"
    )
    assert (
        pyromark.html(CODE_BLOCKS, highlight=callback)
        == pyromark.Markdown(highlight=callback).html(CODE_BLOCKS)
        == expected
    )
    assert (
        calls
        == [
            ("python", "x = 1\n"),
            (None, "indented\n"),
            ("unknown-language", "y = 2\n"),
        ]
        * 2
    )


def test_highlight_language_is_the_first_word_of_the_fence() -> None:
    markdown = '```python title="a.py"\nx = 1\n```'
    languages: list[str | None] = []

    pyromark.html(
        markdown, highlight=lambda language, _code: languages.append(language)
    )

    assert languages == ["python"]
    assert "color:#a71d5d" in pyromark.html(
        markdown, highlight=pyromark.Theme.INSPIRED_GITHUB
    )


@pytest.mark.parametrize(
    "markdown", ["```\nx = 1\n```", "```   \nx = 1\n```", "    x = 1"]
)
def test_highlight_language_is_none_when_the_block_names_none(
    markdown: str,
) -> None:
    languages: list[str | None] = []

    pyromark.html(
        markdown, highlight=lambda language, _code: languages.append(language)
    )

    assert languages == [None]


def test_highlight_callback_returning_none_falls_back() -> None:
    def callback(_language: str | None, _code: str) -> None:
        return None

    assert pyromark.html(CODE_BLOCKS, highlight=callback) == CODE_BLOCKS_PLAIN


def test_highlight_callback_partial_fallback() -> None:
    def callback(language: str | None, code: str) -> str | None:
        if language == "python":
            return f"<div>{code.strip()}</div>"
        return None

    html = pyromark.html(CODE_BLOCKS, highlight=callback)
    assert html.startswith("<div>x = 1</div>")
    assert "<pre><code>indented\n</code></pre>" in html
    assert '<pre><code class="language-unknown-language">' in html


def test_highlight_callback_error() -> None:
    calls: list[str | None] = []

    def callback(language: str | None, _code: str) -> str:
        calls.append(language)
        msg = "highlight failed"
        raise ValueError(msg)

    with pytest.raises(ValueError, match=r"^highlight failed$"):
        pyromark.html(CODE_BLOCKS, highlight=callback)
    assert calls == ["python"]


def test_highlight_callback_bad_return_type() -> None:
    def callback(_language: str | None, _code: str) -> str:
        return 42  # type: ignore[return-value]

    with pytest.raises(
        TypeError, match=r"^highlight callback must return the block's HTML"
    ) as exc:
        pyromark.html(CODE_BLOCKS, highlight=callback)

    assert type(exc.value.__cause__) is TypeError


@CPYTHON_ONLY
def test_markdown_highlight_callback_is_collectable() -> None:
    class Holder:
        def __init__(self) -> None:
            self.tag = "x"
            self.md = pyromark.Markdown(highlight=self.callback)

        def callback(self, _language: str | None, code: str) -> str:
            return f"<{self.tag}>{code.strip()}</{self.tag}>"

    holder = Holder()
    assert holder.md.html("```\na\n```") == "<x>a</x>\n"
    ref = weakref.ref(holder)
    del holder
    gc.collect()
    assert ref() is None


def test_theme_members_all_work() -> None:
    for theme in pyromark.Theme:
        html = pyromark.html(CODE_BLOCKS, highlight=theme)
        assert html.startswith('<pre style="background-color:#')
        assert pyromark.Markdown(highlight=theme).html(CODE_BLOCKS) == html


def test_theme_covers_every_bundled_theme() -> None:
    with pytest.raises(ValueError, match=r"^unknown highlighting theme") as exc:
        pyromark.html("", highlight="no-such-theme")  # type: ignore[arg-type]
    bundled = ast.literal_eval(str(exc.value).partition("expected one of ")[2])

    assert sorted(bundled) == sorted(theme.value for theme in pyromark.Theme)


def test_theme_from_configuration_value() -> None:
    assert pyromark.Theme("Solarized (dark)") is pyromark.Theme.SOLARIZED_DARK
    with pytest.raises(ValueError, match=r"no-such-theme"):
        pyromark.Theme("no-such-theme")


@pytest.mark.parametrize("value", [True, False])
def test_highlight_rejects_bool(value: bool) -> None:
    with pytest.raises(TypeError, match=r"pyromark.Theme"):
        pyromark.html(CODE_BLOCKS, highlight=value)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match=r"pyromark.Theme"):
        pyromark.Markdown(highlight=value)  # type: ignore[arg-type]


def test_a_theme_is_safe_to_share_between_threads() -> None:
    md = pyromark.Markdown(highlight=pyromark.Theme.BASE16_OCEAN_DARK)
    markdown = f"{CODE_BLOCKS}\n" * 5
    expected = md.html(markdown)

    results, errors = render_on_threads(md, markdown)

    assert not errors
    assert results == [expected] * (THREADS * RENDERS_PER_THREAD)


INDENTED_BLOCK = "    a = 1\n    b = 2\n    c = 3\n"

CROSS_LINE_STATE = '```python\nx = """\nstill a string\n"""\ny = 1\n```'


def test_highlight_joins_a_block_split_across_text_events() -> None:
    parts = [
        event["Text"]
        for event in pyromark.events(INDENTED_BLOCK, merge_text=False)
        if isinstance(event, dict) and "Text" in event
    ]
    assert len(parts) > 1

    seen: list[str] = []

    def highlight(_language: str | None, code: str) -> str:
        seen.append(code)
        return "<x/>"

    pyromark.html(INDENTED_BLOCK, highlight=highlight)

    assert seen == ["".join(parts)]


def test_an_unhighlighted_split_block_keeps_every_line() -> None:
    def highlight(_language: str | None, _code: str) -> None:
        return None

    assert pyromark.html(INDENTED_BLOCK, highlight=highlight) == pyromark.html(
        INDENTED_BLOCK
    )


def test_a_theme_carries_state_across_lines() -> None:
    html = pyromark.html(
        CROSS_LINE_STATE, highlight=pyromark.Theme.INSPIRED_GITHUB
    )

    assert "still a string" in html
    string_colour = re.findall(r'color:(#[0-9a-f]{6});">still a string', html)
    assert string_colour
    assert re.search(
        r"color:" + string_colour[0] + r';">&quot;&quot;&quot;', html
    )


def test_highlight_callback_output_ends_its_line() -> None:
    html = pyromark.html(
        "~~~\nx\n~~~\n\nafter", highlight=lambda _language, _code: "<pre/>"
    )
    assert html == "<pre/>\n<p>after</p>\n"


@pytest.mark.parametrize(
    ("language", "code"),
    [
        ("typescript", "let x: number = 1"),
        ("tsx", "const a = <A />"),
        ("toml", "a = 1"),
        ("dockerfile", "FROM alpine"),
        ("kotlin", "val x = 1"),
        ("swift", "let x = 1"),
        ("zig", "const x = 1;"),
    ],
)
def test_highlight_knows_more_than_the_syntect_defaults(
    language: str, code: str
) -> None:
    def render(fence: str) -> str:
        return pyromark.html(
            f"~~~{fence}\n{code}\n~~~", highlight=pyromark.Theme.INSPIRED_GITHUB
        )

    assert render(language) != render("no-such-language")


@pytest.mark.parametrize(
    ("alias", "language", "code"),
    [
        ("batch", "bat", "echo %x%"),
        ("csharp", "cs", "var x = 1;"),
        ("docker", "dockerfile", "FROM alpine"),
        ("fsharp", "f#", "let x = 1"),
        ("jsonc", "json", '{"a": 1}'),
        ("objc", "objective-c", "@interface A @end"),
        ("pwsh", "ps1", "$x = 1"),
        ("python3", "py", "x = 1"),
        ("Shell", "bash", "echo $HOME"),
    ],
)
def test_highlight_understands_common_aliases(
    alias: str, language: str, code: str
) -> None:
    def render(fence: str) -> str:
        return pyromark.html(
            f"~~~{fence}\n{code}\n~~~", highlight=pyromark.Theme.INSPIRED_GITHUB
        )

    assert render(alias) == render(language) != render("no-such-language")
