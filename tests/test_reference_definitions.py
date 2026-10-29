from __future__ import annotations

import pyromark
from pyromark.event import LinkDef

from tests.shared import NON_ASCII_DOC

REFERENCE_DEFINITIONS_DOC = """[foo]: /a 'A'
[bar]: /b

Text referring to [foo] and [bar] and [missing].

[BAZ]: /c "C"
[baz]: /ignored
"""


def test_reference_definitions() -> None:
    expected: dict[str, LinkDef] = {
        "foo": {"dest": "/a", "title": "A", "span": {"start": 0, "end": 13}},
        "bar": {"dest": "/b", "title": None, "span": {"start": 14, "end": 23}},
        "BAZ": {"dest": "/c", "title": "C", "span": {"start": 75, "end": 88}},
    }
    definitions = pyromark.reference_definitions(REFERENCE_DEFINITIONS_DOC)
    assert definitions == expected
    assert list(definitions) == ["foo", "bar", "BAZ"]
    for label, definition in definitions.items():
        span = definition["span"]
        source = REFERENCE_DEFINITIONS_DOC[span["start"] : span["end"]]
        assert source.startswith(f"[{label}]:")


def test_reference_definitions_empty() -> None:
    assert pyromark.reference_definitions("no definitions here") == {}
    assert pyromark.reference_definitions("") == {}


def test_reference_definitions_options() -> None:
    markdown = "---\n[foo]: /a\n---\n"
    expected: dict[str, LinkDef] = {
        "foo": {"dest": "/a", "title": None, "span": {"start": 4, "end": 13}}
    }
    assert pyromark.reference_definitions(markdown) == expected
    assert (
        pyromark.reference_definitions(
            markdown, options=pyromark.Options.ENABLE_YAML_STYLE_METADATA_BLOCKS
        )
        == {}
    )


def test_markdown_reference_definitions_matches_function() -> None:
    options = pyromark.Options.ENABLE_YAML_STYLE_METADATA_BLOCKS
    md = pyromark.Markdown(options=options)
    assert md.reference_definitions(
        REFERENCE_DEFINITIONS_DOC
    ) == pyromark.reference_definitions(
        REFERENCE_DEFINITIONS_DOC, options=options
    )
    metadata = "---\n[foo]: /a\n---\n"
    assert md.reference_definitions(metadata) == {}
    assert pyromark.Markdown().reference_definitions(metadata) != {}


def test_reference_definition_spans_are_utf8_byte_offsets() -> None:
    source = NON_ASCII_DOC.encode()
    definitions = pyromark.reference_definitions(NON_ASCII_DOC)
    span = definitions["foo"]["span"]
    assert source[span["start"] : span["end"]].decode() == "[foo]: /url"
    assert NON_ASCII_DOC[span["start"] : span["end"]] != "[foo]: /url"
