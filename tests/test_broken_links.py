from __future__ import annotations

import gc
import io
import itertools
import weakref
from collections import UserList
from collections.abc import Callable, Iterable, Iterator, Mapping
from typing import TypeAlias

import pyromark
import pytest
from pyromark.event import BrokenLink, BrokenLinkCallback, Event

from tests.shared import BROKEN_LINKS, CPYTHON_ONLY

_Runner: TypeAlias = Callable[[str, BrokenLinkCallback | None], object]


BROKEN_LINKS_RESULT = (
    '<p><a href="https://example.com/b" title="Example">a</a>'
    ' and <a href="https://example.com/c" title="Example">c</a>'
    ' and <a href="https://example.com/d" title="Example">d</a>'
    ' and <img src="https://example.com/e" alt="e" title="Example" /></p>\n'
)


BROKEN_LINKS_CALLS: list[BrokenLink] = [
    {"span": {"start": 0, "end": 6}, "link_type": "Reference", "reference": "b"},
    {"span": {"start": 11, "end": 14}, "link_type": "Collapsed", "reference": "c"},
    {"span": {"start": 21, "end": 24}, "link_type": "Shortcut", "reference": "d"},
    {"span": {"start": 29, "end": 33}, "link_type": "Shortcut", "reference": "e"},
]


def _write_html(markdown: str, callback: BrokenLinkCallback | None, /) -> bytes:
    file = io.BytesIO()
    pyromark.write_html(markdown, file, broken_link_callback=callback)
    return file.getvalue()


def _markdown_write_html(markdown: str, callback: BrokenLinkCallback | None, /) -> bytes:
    file = io.BytesIO()
    pyromark.Markdown(broken_link_callback=callback).write_html(markdown, file)
    return file.getvalue()


RUNNERS: Mapping[str, _Runner] = {
    "html": lambda markdown, callback: pyromark.html(markdown, broken_link_callback=callback),
    "events": lambda markdown, callback: tuple(
        pyromark.events(markdown, broken_link_callback=callback)
    ),
    "events_unmerged": lambda markdown, callback: tuple(
        pyromark.events(markdown, merge_text=False, broken_link_callback=callback)
    ),
    "events_with_range": lambda markdown, callback: tuple(
        pyromark.events_with_range(markdown, broken_link_callback=callback)
    ),
    "Markdown.html": lambda markdown, callback: pyromark.Markdown(
        broken_link_callback=callback
    ).html(markdown),
    "Markdown.events": lambda markdown, callback: tuple(
        pyromark.Markdown(broken_link_callback=callback).events(markdown)
    ),
    "Markdown.events_with_range": lambda markdown, callback: tuple(
        pyromark.Markdown(broken_link_callback=callback).events_with_range(markdown)
    ),
    "write_html": _write_html,
    "Markdown.write_html": _markdown_write_html,
}


def _resolving_callback(calls: list[BrokenLink]) -> Callable[[BrokenLink], tuple[str, str]]:
    def callback(broken_link: BrokenLink) -> tuple[str, str]:
        calls.append(broken_link)
        return f"https://example.com/{broken_link['reference']}", "Example"

    return callback


def test_broken_link_callback_html() -> None:
    calls: list[BrokenLink] = []
    assert (
        pyromark.html(BROKEN_LINKS, broken_link_callback=_resolving_callback(calls))
        == pyromark.Markdown(broken_link_callback=_resolving_callback(calls)).html(BROKEN_LINKS)
        == BROKEN_LINKS_RESULT
    )
    assert calls == BROKEN_LINKS_CALLS * 2


def test_broken_link_callback_events() -> None:
    calls: list[BrokenLink] = []
    expected_calls: list[BrokenLink] = [
        {"span": {"start": 0, "end": 5}, "link_type": "Shortcut", "reference": "foo"}
    ] * 3
    expected: tuple[Event, ...] = (
        {"Start": "Paragraph"},
        {
            "Start": {
                "Link": {
                    "link_type": "ShortcutUnknown",
                    "dest_url": "https://example.com/foo",
                    "title": "Example",
                    "id": "foo",
                }
            }
        },
        {"Text": "foo"},
        {"End": "Link"},
        {"End": "Paragraph"},
    )
    assert (
        tuple(pyromark.events("[foo]", broken_link_callback=_resolving_callback(calls)))
        == tuple(pyromark.Markdown(broken_link_callback=_resolving_callback(calls)).events("[foo]"))
        == expected
    )
    assert (
        tuple(
            event
            for event, _range in pyromark.events_with_range(
                "[foo]", broken_link_callback=_resolving_callback(calls)
            )
        )
        == expected
    )
    assert calls == expected_calls


@pytest.mark.parametrize("runner", RUNNERS.values(), ids=RUNNERS.keys())
def test_broken_link_callback_returning_none(runner: _Runner) -> None:
    calls: list[BrokenLink] = []

    def callback(broken_link: BrokenLink) -> None:
        calls.append(broken_link)

    assert runner(BROKEN_LINKS, callback) == runner(BROKEN_LINKS, None)
    assert calls == BROKEN_LINKS_CALLS


@pytest.mark.parametrize("runner", RUNNERS.values(), ids=RUNNERS.keys())
def test_broken_link_callback_error(runner: _Runner) -> None:
    calls: list[BrokenLink] = []

    def callback(broken_link: BrokenLink) -> tuple[str, str]:
        calls.append(broken_link)
        msg = "callback failed"
        raise ValueError(msg)

    with pytest.raises(ValueError, match=r"^callback failed$"):
        runner(BROKEN_LINKS, callback)
    assert calls == BROKEN_LINKS_CALLS[:1]


ITERATOR_RUNNERS = {name: runner for name, runner in RUNNERS.items() if "events" in name}


@pytest.mark.parametrize("runner", ITERATOR_RUNNERS.values(), ids=ITERATOR_RUNNERS.keys())
def test_broken_link_callback_running_out_of_answers_is_not_silent(runner: _Runner) -> None:
    destinations = iter(["/only-one"])

    def callback(_broken_link: BrokenLink) -> tuple[str, str]:
        return next(destinations), ""

    with pytest.raises(RuntimeError, match=r"^callback raised StopIteration$"):
        runner(BROKEN_LINKS, callback)


@pytest.mark.parametrize(
    ("returned", "expected"),
    [
        (42, TypeError),
        (("x",), ValueError),
        (("a", "b", "c"), ValueError),
        ((1, 2), TypeError),
        ("https://example.com", TypeError),
        (["a", "b"], TypeError),
    ],
    ids=["not-a-tuple", "too-short", "too-long", "not-strings", "a-bare-str", "a-list"],
)
def test_broken_link_callback_bad_return_type(returned: object, expected: type[Exception]) -> None:
    def callback(_broken_link: BrokenLink) -> tuple[str, str]:
        return returned  # type: ignore[return-value]

    with pytest.raises(expected, match=r"^broken link callback must return a ") as exc:
        pyromark.html(BROKEN_LINKS, broken_link_callback=callback)

    assert type(exc.value.__cause__) is expected


@pytest.mark.parametrize("value", [42, "callback", object()])
def test_broken_link_callback_must_be_callable(value: object) -> None:
    calls: tuple[Callable[[], object], ...] = (
        lambda: pyromark.html("# Hi", broken_link_callback=value),  # type: ignore[arg-type]
        lambda: pyromark.write_html(
            "# Hi",
            io.BytesIO(),
            broken_link_callback=value,  # type: ignore[arg-type]
        ),
        lambda: pyromark.events("# Hi", broken_link_callback=value),  # type: ignore[arg-type]
        lambda: pyromark.events_with_range(
            "# Hi",
            broken_link_callback=value,  # type: ignore[arg-type]
        ),
        lambda: pyromark.Markdown(broken_link_callback=value),  # type: ignore[arg-type]
    )
    for call in calls:
        with pytest.raises(TypeError, match=r"^broken_link_callback must be callable$"):
            call()


@CPYTHON_ONLY
def test_markdown_broken_link_callback_is_collectable() -> None:
    class Holder:
        def __init__(self) -> None:
            self.dest_url = "https://example.com"
            self.md = pyromark.Markdown(broken_link_callback=self.callback)

        def callback(self, _broken_link: BrokenLink) -> tuple[str, str]:
            return self.dest_url, ""

    holder = Holder()
    assert holder.md.html("[a]") == ('<p><a href="https://example.com">a</a></p>\n')
    ref = weakref.ref(holder)
    del holder
    gc.collect()
    assert ref() is None


@pytest.mark.parametrize(
    "func", [pyromark.events, pyromark.events_with_range], ids=["events", "events_with_range"]
)
def test_broken_link_callback_error_mid_iteration(func: Callable[..., Iterable[object]]) -> None:
    calls: list[BrokenLink] = []

    def callback(broken_link: BrokenLink) -> tuple[str, str]:
        calls.append(broken_link)
        msg = "callback failed"
        raise ValueError(msg)

    events = func(BROKEN_LINKS, broken_link_callback=callback)
    with pytest.raises(ValueError, match=r"^callback failed$"):
        list(events)
    assert calls == BROKEN_LINKS_CALLS[:1]


@pytest.mark.parametrize(
    "func", [pyromark.events, pyromark.events_with_range], ids=["events", "events_with_range"]
)
def test_broken_link_callback_error_ends_the_iteration(
    func: Callable[..., Iterator[object]],
) -> None:
    def callback(_broken_link: BrokenLink) -> tuple[str, str]:
        msg = "callback failed"
        raise ValueError(msg)

    events = func(BROKEN_LINKS, broken_link_callback=callback)
    with pytest.raises(ValueError, match=r"^callback failed$"):
        list(events)

    assert list(events) == []
    assert gc.get_referents(events) == [type(events)]


@pytest.mark.parametrize(
    "func", [pyromark.events, pyromark.events_with_range], ids=["events", "events_with_range"]
)
def test_broken_link_callback_error_reaches_a_caller_that_stops_early(
    func: Callable[..., Iterator[object]],
) -> None:
    calls: list[str] = []

    def callback(broken_link: BrokenLink) -> tuple[str, str]:
        calls.append(broken_link["reference"])
        msg = "callback failed"
        raise ValueError(msg)

    events = func(BROKEN_LINKS, broken_link_callback=callback)

    # takewhile ends quietly, so no error is raised, if an event is yielded
    # once the callback has failed.
    with pytest.raises(ValueError, match=r"^callback failed$"):
        tuple(itertools.takewhile(lambda _event: not calls, events))
    assert calls


@pytest.mark.parametrize(
    "func", [pyromark.events, pyromark.events_with_range], ids=["events", "events_with_range"]
)
def test_abandoned_iterator_retains_nothing_after_a_callback_error(
    func: Callable[..., Iterator[object]],
) -> None:
    def callback(_broken_link: BrokenLink) -> tuple[str, str]:
        msg = "callback failed"
        raise ValueError(msg)

    iterator_type = type(func(""))

    def live() -> int:
        gc.collect()
        return sum(1 for obj in gc.get_objects() if isinstance(obj, iterator_type))

    before = live()
    for _ in range(20):
        events = func(BROKEN_LINKS, broken_link_callback=callback)
        with pytest.raises(ValueError, match=r"^callback failed$"):
            tuple(events)
        del events

    assert live() == before


def _resolve_a(parser: Iterator[object] | pyromark.Markdown, /) -> object:
    """Has the parser of "[a]" call its callback, without finishing an iterator."""
    if isinstance(parser, pyromark.Markdown):
        parser.html("[a]")
    else:
        next(parser)  # Start(Paragraph)
        next(parser)  # Start(Link), resolved by the callback
    return parser


CYCLE_FACTORIES: Mapping[str, Callable[[BrokenLinkCallback], object]] = {
    "events": lambda callback: _resolve_a(pyromark.events("[a]", broken_link_callback=callback)),
    "events_with_range": lambda callback: _resolve_a(
        pyromark.events_with_range("[a]", broken_link_callback=callback)
    ),
    "Markdown": lambda callback: _resolve_a(pyromark.Markdown(broken_link_callback=callback)),
}


@CPYTHON_ONLY
@pytest.mark.parametrize("factory", CYCLE_FACTORIES.values(), ids=CYCLE_FACTORIES.keys())
def test_callback_cycle_is_collectable(factory: Callable[[BrokenLinkCallback], object]) -> None:
    class Holder:
        def __init__(self) -> None:
            self.resolved: list[str] = []
            self.parser = factory(self.callback)

        def callback(self, broken_link: BrokenLink) -> tuple[str, str]:
            self.resolved.append(broken_link["reference"])
            return "/u", "t"

    holder = Holder()
    assert holder.resolved == ["a"]
    assert gc.is_tracked(holder.parser)
    ref = weakref.ref(holder)
    del holder
    gc.collect()
    assert ref() is None


@pytest.mark.parametrize("reenter", [iter, next], ids=["iter", "next"])
@pytest.mark.parametrize(
    "func", [pyromark.events, pyromark.events_with_range], ids=["events", "events_with_range"]
)
def test_callback_cannot_reenter_its_iterator(
    func: Callable[..., Iterator[object]], reenter: Callable[[Iterator[object]], object]
) -> None:
    def callback(_broken_link: BrokenLink) -> None:
        reenter(events)

    events = func("[a]", broken_link_callback=callback)

    with pytest.raises(RuntimeError, match=r"^Already (?:mutably )?borrowed$"):
        tuple(events)
    assert tuple(events) == ()


@CPYTHON_ONLY
@pytest.mark.parametrize(
    "func", [pyromark.events, pyromark.events_with_range], ids=["events", "events_with_range"]
)
def test_gc_can_break_a_callback_cycle_at_the_iterator(
    func: Callable[..., Iterator[object]],
) -> None:
    box: UserList[object] = UserList()
    ref = weakref.ref(box)
    # The collector clears a cycle oldest object first. Freezing sets the
    # box aside until the iterator has aged, and unfreezing puts it back
    # behind the iterator, so clearing the iterator has to break the cycle.
    gc.freeze()
    try:
        events = func("[a]", broken_link_callback=box.append)
        gc.collect()
    finally:
        gc.unfreeze()
    box.append(events)
    del box, events
    gc.collect()
    assert ref() is None


def test_broken_link_spans_are_utf8_byte_offsets() -> None:
    seen: list[BrokenLink] = []

    def callback(broken_link: BrokenLink) -> None:
        seen.append(broken_link)

    markdown = "é日本\U0001f600 [missing]"
    pyromark.html(markdown, broken_link_callback=callback)

    span = seen[0]["span"]
    source = markdown.encode()
    assert source[span["start"] : span["end"]].decode() == "[missing]"


@pytest.mark.parametrize("runner", RUNNERS.values(), ids=RUNNERS.keys())
def test_every_entry_point_wraps_a_stop_iteration(runner: _Runner) -> None:
    def callback(_broken_link: BrokenLink) -> tuple[str, str]:
        raise StopIteration

    with pytest.raises(RuntimeError, match=r"^callback raised StopIteration$") as exc:
        runner(BROKEN_LINKS, callback)

    assert isinstance(exc.value.__cause__, StopIteration)
