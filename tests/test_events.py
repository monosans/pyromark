from __future__ import annotations

import gc
import threading
import weakref
from collections.abc import Callable, Iterator, Mapping

import pyromark
import pytest
from pyromark.event import Event, Range

from tests.shared import ALL_OPTIONS, EVENTS_TESTDATA, NON_ASCII_DOC


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
    assert pyromark.html(markdown, options=options)
    assert sum(1 for _ in pyromark.events(markdown, options=options)) > 0


@pytest.mark.parametrize(
    "call",
    [
        pyromark.html,
        lambda markdown: tuple(pyromark.events(markdown)),
        lambda markdown: tuple(pyromark.events_with_range(markdown)),
    ],
    ids=["html", "events", "events_with_range"],
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
