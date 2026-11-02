from __future__ import annotations

import gc
import io
import threading
import types
import typing
import weakref
from collections.abc import Callable, Iterator, Mapping
from typing import Literal, Union

import pyromark
import pytest
from pyromark.event import BrokenLink, Event, Range
from typing_extensions import is_typeddict

from tests.shared import (
    ALL_OPTIONS,
    CPYTHON_ONLY,
    EVENTS_TESTDATA,
    NON_ASCII_DOC,
)

UNKNOWN_LINK_TYPES = """\
[ref][lbl]

[lbl2][]

[lbl3]
"""


UNKNOWN_LINK_TYPES_EVENTS: tuple[Event, ...] = (
    {"Start": "Paragraph"},
    {
        "Start": {
            "Link": {
                "link_type": "ReferenceUnknown",
                "dest_url": "/u",
                "title": "t",
                "id": "lbl",
            }
        }
    },
    {"Text": "ref"},
    {"End": "Link"},
    {"End": "Paragraph"},
    {"Start": "Paragraph"},
    {
        "Start": {
            "Link": {
                "link_type": "CollapsedUnknown",
                "dest_url": "/u",
                "title": "t",
                "id": "lbl2",
            }
        }
    },
    {"Text": "lbl2"},
    {"End": "Link"},
    {"End": "Paragraph"},
    {"Start": "Paragraph"},
    {
        "Start": {
            "Link": {
                "link_type": "ShortcutUnknown",
                "dest_url": "/u",
                "title": "t",
                "id": "lbl3",
            }
        }
    },
    {"Text": "lbl3"},
    {"End": "Link"},
    {"End": "Paragraph"},
)


@pytest.mark.parametrize(
    ("markdown", "expected"),
    EVENTS_TESTDATA.values(),
    ids=EVENTS_TESTDATA.keys(),
)
def test_events(markdown: str, expected: tuple[Event, ...]) -> None:
    md = pyromark.Markdown(options=ALL_OPTIONS)
    assert (
        tuple(pyromark.events(markdown, options=ALL_OPTIONS))
        == tuple(md.events(markdown))
        == tuple(md.events(markdown))
        == expected
    )


@pytest.mark.parametrize(
    "markdown",
    [markdown for markdown, _events in EVENTS_TESTDATA.values()],
    ids=EVENTS_TESTDATA.keys(),
)
def test_events_with_range(markdown: str) -> None:
    md = pyromark.Markdown(options=ALL_OPTIONS)
    for merge_text in (False, True):
        events_with_range = tuple(
            pyromark.events_with_range(
                markdown, options=ALL_OPTIONS, merge_text=merge_text
            )
        )
        assert events_with_range == tuple(
            md.events_with_range(markdown, merge_text=merge_text)
        )
        assert tuple(event for event, _range in events_with_range) == tuple(
            pyromark.events(
                markdown, options=ALL_OPTIONS, merge_text=merge_text
            )
        )
        source_length = len(markdown.encode())
        for _event, range_ in events_with_range:
            assert 0 <= range_["start"] <= range_["end"] <= source_length


def test_events_unknown_link_types() -> None:
    def callback(_broken_link: BrokenLink) -> tuple[str, str]:
        return "/u", "t"

    assert (
        tuple(
            pyromark.events(UNKNOWN_LINK_TYPES, broken_link_callback=callback)
        )
        == tuple(
            pyromark.Markdown(broken_link_callback=callback).events(
                UNKNOWN_LINK_TYPES
            )
        )
        == UNKNOWN_LINK_TYPES_EVENTS
    )


def test_merge_text() -> None:
    markdown = r"a&amp;b\!c"
    merged: tuple[Event, ...] = (
        {"Start": "Paragraph"},
        {"Text": "a&b!c"},
        {"End": "Paragraph"},
    )
    unmerged: tuple[Event, ...] = (
        {"Start": "Paragraph"},
        {"Text": "a"},
        {"Text": "&"},
        {"Text": "b"},
        {"Text": "!c"},
        {"End": "Paragraph"},
    )
    md = pyromark.Markdown()
    assert (
        tuple(pyromark.events(markdown))
        == tuple(pyromark.events(markdown, merge_text=True))
        == tuple(md.events(markdown))
        == tuple(md.events(markdown, merge_text=True))
        == merged
    )
    assert (
        tuple(pyromark.events(markdown, merge_text=False))
        == tuple(md.events(markdown, merge_text=False))
        == unmerged
    )


def test_events_with_range_offsets() -> None:
    markdown = r"a&amp;b\!c"
    merged: tuple[tuple[Event, Range], ...] = (
        ({"Start": "Paragraph"}, {"start": 0, "end": 10}),
        ({"Text": "a&b!c"}, {"start": 0, "end": 10}),
        ({"End": "Paragraph"}, {"start": 0, "end": 10}),
    )
    unmerged: tuple[tuple[Event, Range], ...] = (
        ({"Start": "Paragraph"}, {"start": 0, "end": 10}),
        ({"Text": "a"}, {"start": 0, "end": 1}),
        ({"Text": "&"}, {"start": 1, "end": 6}),
        ({"Text": "b"}, {"start": 6, "end": 7}),
        ({"Text": "!c"}, {"start": 8, "end": 10}),
        ({"End": "Paragraph"}, {"start": 0, "end": 10}),
    )
    md = pyromark.Markdown()
    assert (
        tuple(pyromark.events_with_range(markdown))
        == tuple(pyromark.events_with_range(markdown, merge_text=False))
        == tuple(md.events_with_range(markdown))
        == unmerged
    )
    assert (
        tuple(pyromark.events_with_range(markdown, merge_text=True))
        == tuple(md.events_with_range(markdown, merge_text=True))
        == merged
    )


def test_events_is_an_iterator() -> None:
    events = pyromark.events("# Hello world")
    assert iter(events) is events
    assert next(events) == {
        "Start": {
            "Heading": {"level": "H1", "id": None, "classes": (), "attrs": ()}
        }
    }
    assert list(events) == [{"Text": "Hello world"}, {"End": {"Heading": "H1"}}]
    with pytest.raises(StopIteration):
        next(events)
    assert list(events) == []

    events_with_range = pyromark.events_with_range("# Hi")
    assert iter(events_with_range) is events_with_range
    assert len(list(events_with_range)) == len(tuple(pyromark.events("# Hi")))


def test_events_outlive_their_input() -> None:
    markdown = "".join(("# ", "Hello", " world"))  # noqa: FLY002
    events = pyromark.events(markdown)
    events_with_range = pyromark.events_with_range(markdown)
    del markdown
    gc.collect()
    assert tuple(events) == tuple(pyromark.events("# Hello world"))
    assert tuple(events_with_range) == tuple(
        pyromark.events_with_range("# Hello world")
    )


SOURCE_CYCLE_FACTORIES: Mapping[str, Callable[[str], Iterator[object]]] = {
    "events": pyromark.events,
    "events_with_range": pyromark.events_with_range,
    "Markdown.events": lambda markdown: pyromark.Markdown().events(markdown),
    "Markdown.events_with_range": lambda markdown: (
        pyromark.Markdown().events_with_range(markdown)
    ),
}


@CPYTHON_ONLY
@pytest.mark.parametrize(
    "factory",
    SOURCE_CYCLE_FACTORIES.values(),
    ids=SOURCE_CYCLE_FACTORIES.keys(),
)
def test_source_cycle_is_collectable(
    factory: Callable[[str], Iterator[object]],
) -> None:
    class Source(str):  # noqa: FURB189
        __slots__ = ("__weakref__", "iterator")
        iterator: Iterator[object]

    source = Source("[a]")
    source.iterator = factory(source)
    assert source in gc.get_referents(source.iterator)
    ref = weakref.ref(source)
    del source
    gc.collect()
    assert ref() is None


def test_iterator_outlives_the_markdown_that_made_it() -> None:
    def callback(_broken_link: BrokenLink) -> tuple[str, str]:
        return "/u", "t"

    md = pyromark.Markdown(broken_link_callback=callback)
    events = md.events("[a]")
    del md
    gc.collect()
    assert tuple(events) == tuple(
        pyromark.events("[a]", broken_link_callback=callback)
    )


def test_event_ranges_are_utf8_byte_offsets() -> None:
    source = NON_ASCII_DOC.encode()
    for event, range_ in pyromark.events_with_range(NON_ASCII_DOC):
        assert 0 <= range_["start"] <= range_["end"] <= len(source)
        if event == {"Text": "é日本\U0001f600 text"}:
            assert (
                source[range_["start"] : range_["end"]].decode()
                == "é日本\U0001f600 text"
            )
            assert (
                NON_ASCII_DOC[range_["start"] : range_["end"]]
                != "é日本\U0001f600 text"
            )
            break
    else:  # pragma: no cover
        pytest.fail("no Text event covering the non-ASCII run")


@pytest.mark.parametrize(
    "markdown",
    [
        "> " * 5_000 + "deep",
        "*" * 5_000 + "x" + "*" * 5_000,
        "[" * 5_000 + "x" + "]" * 5_000,
        "".join("  " * i + "- x\n" for i in range(500)),
        "<div>" * 5_000,
    ],
    ids=["blockquote", "emphasis", "brackets", "list", "html"],
)
def test_deeply_nested_input_does_not_overflow_the_stack(markdown: str) -> None:
    options = ALL_OPTIONS
    file = io.BytesIO()

    pyromark.write_html(markdown, file, options=options)

    assert file.getvalue().decode() == pyromark.html(markdown, options=options)
    assert sum(1 for _ in pyromark.events(markdown, options=options)) > 0


@pytest.mark.parametrize(
    "call",
    [
        pyromark.html,
        lambda markdown: pyromark.write_html(markdown, io.BytesIO()),
        lambda markdown: tuple(pyromark.events(markdown)),
        lambda markdown: tuple(pyromark.events_with_range(markdown)),
        pyromark.reference_definitions,
    ],
    ids=["html", "write_html", "events", "events_with_range", "refdefs"],
)
def test_lone_surrogate_is_rejected(call: Callable[[str], object]) -> None:
    with pytest.raises(UnicodeEncodeError):
        call("a\ud800b")


def test_racing_one_iterator_loses_nothing() -> None:
    markdown = "# H\n\ntext *a* [missing] `c`\n\n> q\n\n" * 40
    total = sum(1 for _ in pyromark.events(markdown))
    shared = pyromark.events(markdown)
    workers = 8
    consumed = [0] * workers
    raised: list[str] = []
    barrier = threading.Barrier(workers)
    lock = threading.Lock()

    def drain(slot: int) -> None:
        seen = 0
        barrier.wait()
        try:
            for _ in shared:
                seen += 1
        except Exception as exc:
            with lock:
                raised.append(type(exc).__name__)
        finally:
            consumed[slot] = seen

    threads = [
        threading.Thread(target=drain, args=(index,))
        for index in range(workers)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert set(raised) <= {"RuntimeError"}
    assert sum(consumed) + sum(1 for _ in shared) == total


_EVERY_VARIANT = (
    "# h1\n## h2 {#i .a .b x=y}\n### h3\n#### h4\n##### h5\n###### h6\n",
    "para *e* **s** ~~d~~ `c` <b>x</b>\n\n<div>b</div>\n\n---\n",
    "~~~python\nx = 1\n~~~\n\n    indented\n",
    "> [!NOTE]\n> n\n\n> [!TIP]\n> t\n\n> [!IMPORTANT]\n> i\n",
    "> [!WARNING]\n> w\n\n> [!CAUTION]\n> c\n\n> plain\n",
    "- a\n- [ ] b\n- [x] c\n\n1. one\n2. two\n",
    "| a | b | c | d |\n|:--|:-:|--:|---|\n| 1 | 2 | 3 | 4 |\n",
    "x[^1]\n\n[^1]: note\n\n$inline$ and $$display$$\n",
    "---\nyaml: 1\n---\n",
    "+++\ntoml = 1\n+++\n",
    "term\n\n: definition\n\nsoft\nbreak\n\nhard  \nbreak\n",
    "[[w|t]] [[p]] <https://auto.link> <me@example.com>\n",
    "[k] [k][] [k][k] [x](/i 't') ![i](/i 'T')\n\n[k]: /k\n",
    "~sub~ and ^sup^\n",
)


_UNRESOLVED = "[gone] [gone][] [gone][absent]\n"


def _declared_names(annotation: object) -> set[str]:
    """Every Literal member and TypedDict key reachable from a type."""
    if typing.get_origin(annotation) is Literal:
        return {str(arg) for arg in typing.get_args(annotation)}
    if is_typeddict(annotation):
        hints = typing.get_type_hints(annotation, globalns=vars(pyromark.event))
        return set(hints) | {
            name for hint in hints.values() for name in _declared_names(hint)
        }
    return {
        name
        for arg in typing.get_args(annotation)
        for name in _declared_names(arg)
    }


def _matches(value: object, annotation: object) -> bool:
    """Whether a value has the shape an annotation describes."""
    origin = typing.get_origin(annotation)
    if origin is Literal:
        return value in typing.get_args(annotation)
    if origin in {Union, types.UnionType}:
        return any(_matches(value, a) for a in typing.get_args(annotation))
    if origin is tuple:
        args = typing.get_args(annotation)
        if not isinstance(value, tuple):
            return False
        if args[-1] is Ellipsis:
            return all(_matches(v, args[0]) for v in value)
        return len(args) == len(value) and all(map(_matches, value, args))
    if is_typeddict(annotation):
        hints = typing.get_type_hints(annotation, globalns=vars(pyromark.event))
        return (
            isinstance(value, dict)
            and set(value) == set(hints)
            and all(_matches(value[k], h) for k, h in hints.items())
        )
    if annotation is type(None):
        return value is None
    if annotation is bool:
        return isinstance(value, bool)
    if annotation is int:
        return isinstance(value, int) and not isinstance(value, bool)
    if annotation is str:
        return isinstance(value, str)
    msg = f"unhandled annotation {annotation!r}"
    raise AssertionError(msg)


def _observed_names(event: object) -> set[str]:
    if isinstance(event, str):
        return {event}
    if isinstance(event, dict):
        return set(event) | {
            n for v in event.values() for n in _observed_names(v)
        }
    if isinstance(event, tuple):
        return {n for v in event for n in _observed_names(v)}
    return {"None"} if event is None else set()


def test_event_types_declare_exactly_what_is_emitted() -> None:
    options = ALL_OPTIONS
    observed: set[str] = set()
    for markdown in (*_EVERY_VARIANT, _UNRESOLVED):
        events = pyromark.events(
            markdown,
            options=options,
            merge_text=False,
            broken_link_callback=lambda _broken_link: ("/resolved", "t"),
        )
        for event in events:
            observed |= _observed_names(event)
            assert _matches(event, pyromark.event.Event), event

    assert _declared_names(pyromark.event.Event) - observed == set()
