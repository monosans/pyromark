from __future__ import annotations

import io
from collections.abc import Callable, Mapping

import pyromark
import pytest
from pyromark.event import BrokenLink

from tests.shared import CODE_BLOCKS, RENDERS_PER_THREAD, TABLE, THREADS, render_on_threads


def test_markdown_options_and_broken_link_callback() -> None:
    def callback(_broken_link: BrokenLink) -> tuple[str, str]:
        return "/u", "t"

    markdown = f"{TABLE}\n\n[a]"
    options = pyromark.Options.ENABLE_TABLES
    html = pyromark.Markdown(options=options, broken_link_callback=callback).html(markdown)
    assert html == pyromark.html(markdown, options=options, broken_link_callback=callback)
    assert "<table>" in html
    assert '<a href="/u" title="t">a</a>' in html


CONFIG_DOC = """\
---
[meta]: /m
---

~~~python
x = 1
~~~

[undefined]

[defined]: /d
"""


CONFIG_SETTINGS: Mapping[str, Callable[[], pyromark.Markdown]] = {
    "options": lambda: pyromark.Markdown(
        options=pyromark.Options.ENABLE_YAML_STYLE_METADATA_BLOCKS
    ),
    "broken_link_callback": lambda: pyromark.Markdown(
        broken_link_callback=lambda _broken_link: ("/u", "t")
    ),
    "highlight": lambda: pyromark.Markdown(highlight=pyromark.Theme.INSPIRED_GITHUB),
}


CONFIG_SCOPE: Mapping[str, set[str]] = {
    "events": {"options", "broken_link_callback"},
    "events_with_range": {"options", "broken_link_callback"},
    "html": {"options", "broken_link_callback", "highlight"},
    "write_html": {"options", "broken_link_callback", "highlight"},
    "reference_definitions": {"options"},
}


def _call(md: pyromark.Markdown, method: str) -> object:
    if method == "events":
        return tuple(md.events(CONFIG_DOC))
    if method == "events_with_range":
        return tuple(md.events_with_range(CONFIG_DOC))
    if method == "html":
        return md.html(CONFIG_DOC)
    if method == "write_html":
        file = io.BytesIO()
        md.write_html(CONFIG_DOC, file)
        return file.getvalue()
    return md.reference_definitions(CONFIG_DOC)


@pytest.mark.parametrize("method", CONFIG_SCOPE)
@pytest.mark.parametrize("setting", CONFIG_SETTINGS)
def test_markdown_setting_scope(setting: str, method: str) -> None:
    default = _call(pyromark.Markdown(), method)
    configured = _call(CONFIG_SETTINGS[setting](), method)
    if setting in CONFIG_SCOPE[method]:
        assert configured != default, f"{setting} should reach {method}"
    else:
        assert configured == default, f"{setting} should not reach {method}"


def test_markdown_settings_are_reusable() -> None:
    md = pyromark.Markdown(
        options=pyromark.Options.ENABLE_TABLES, highlight=pyromark.Theme.INSPIRED_GITHUB
    )
    once = md.html(CONFIG_DOC)
    events = tuple(md.events(CONFIG_DOC))

    assert md.html(CONFIG_DOC) == once
    assert tuple(md.events(CONFIG_DOC)) == events
    assert once == pyromark.html(
        CONFIG_DOC, options=pyromark.Options.ENABLE_TABLES, highlight=pyromark.Theme.INSPIRED_GITHUB
    )
    assert events == tuple(pyromark.events(CONFIG_DOC, options=pyromark.Options.ENABLE_TABLES))


def test_markdown_is_safe_to_share_between_threads() -> None:
    def broken(_broken_link: BrokenLink) -> tuple[str, str]:
        return "/u", "t"

    def highlight(_language: str | None, code: str) -> str:
        return f"<x>{code.strip()}</x>"

    md = pyromark.Markdown(
        options=pyromark.Options.ENABLE_TABLES, broken_link_callback=broken, highlight=highlight
    )
    markdown = f"{CODE_BLOCKS}\n\n{TABLE}\n\n[missing]\n" * 5
    expected = md.html(markdown)

    results, errors = render_on_threads(md, markdown)

    assert not errors
    assert results == [expected] * (THREADS * RENDERS_PER_THREAD)
