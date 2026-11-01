from __future__ import annotations

import io
from collections.abc import Callable
from pathlib import Path

import pyromark
import pytest
from pyromark.event import BrokenLink
from typing_extensions import Buffer, Protocol, override

from tests.shared import ALL_OPTIONS, BROKEN_LINKS, CODE_BLOCKS, EVENTS_TESTDATA, TABLE


@pytest.mark.parametrize(
    ("markdown", "options"),
    [(markdown, ALL_OPTIONS) for markdown, _ in EVENTS_TESTDATA.values()]
    + [(CODE_BLOCKS, pyromark.Options(0)), (TABLE, pyromark.Options(0))],
)
def test_write_html_matches_html(markdown: str, options: pyromark.Options) -> None:
    file = io.BytesIO()
    pyromark.write_html(markdown, file, options=options)
    assert file.getvalue().decode() == pyromark.html(markdown, options=options)


def test_write_html_passes_through_options() -> None:
    def broken_link_callback(_broken_link: BrokenLink) -> tuple[str, str]:
        return "/u", "t"

    def highlight(_language: str | None, code: str) -> str:
        return f"<x>{code.strip()}</x>"

    markdown = f"{CODE_BLOCKS}\n\n[missing]"
    file = io.BytesIO()
    pyromark.write_html(
        markdown, file, broken_link_callback=broken_link_callback, highlight=highlight
    )
    assert file.getvalue().decode() == pyromark.html(
        markdown, broken_link_callback=broken_link_callback, highlight=highlight
    )
    assert b"<x>x = 1</x>" in file.getvalue()
    assert b'<a href="/u" title="t">missing</a>' in file.getvalue()


def test_write_html_propagates_write_errors() -> None:
    calls: list[int] = []

    class Failing(io.BytesIO):
        @override
        def write(self, buffer: Buffer, /) -> int:
            calls.append(len(calls))
            msg = f"disk on fire #{len(calls)}"
            raise OSError(msg)

    with pytest.raises(OSError, match=r"^disk on fire #1$"):
        pyromark.write_html("# Hello world" * 5000, Failing())
    assert len(calls) == 1


def test_write_html_keeps_the_file_objects_exception_chain() -> None:
    class Chained(io.BytesIO):
        @override
        def write(self, buffer: Buffer, /) -> int:
            cause = KeyError("root cause")
            msg = "write blew up"
            raise ValueError(msg) from cause

    with pytest.raises(ValueError, match=r"^write blew up$") as exc:
        pyromark.write_html("# Hello world", Chained())

    assert isinstance(exc.value.__cause__, KeyError)


def test_write_html_keeps_the_file_objects_implicit_context() -> None:
    class Implicit(io.BytesIO):
        @override
        def write(self, buffer: Buffer, /) -> int:
            try:
                return int("not a number")
            except ValueError:
                msg = "disk full"
                raise OSError(msg)  # noqa: B904

    with pytest.raises(OSError, match=r"^disk full$") as exc:
        pyromark.write_html("# Hello world", Implicit())

    assert not exc.value.__suppress_context__
    assert isinstance(exc.value.__context__, ValueError)


class _Unwritable(io.BytesIO):
    @override
    def write(self, buffer: Buffer, /) -> int:
        pytest.fail("wrote after a callback raised")


def test_write_html_stops_at_a_broken_link_callback_error() -> None:
    def callback(_broken_link: BrokenLink) -> tuple[str, str]:
        msg = "callback failed"
        raise LookupError(msg)

    with pytest.raises(LookupError, match=r"^callback failed$"):
        pyromark.write_html(BROKEN_LINKS, _Unwritable(), broken_link_callback=callback)


def test_write_html_stops_at_a_highlight_error() -> None:
    def highlight(_language: str | None, _code: str) -> str:
        msg = "highlight failed"
        raise LookupError(msg)

    with pytest.raises(LookupError, match=r"^highlight failed$"):
        pyromark.write_html(CODE_BLOCKS, _Unwritable(), highlight=highlight)


def test_write_html_rejects_text_file(tmp_path: Path) -> None:
    with (
        (tmp_path / "out.html").open("w", encoding="utf-8") as file,
        pytest.raises(TypeError, match=r"."),
    ):
        pyromark.write_html("# Hi", file)  # type: ignore[arg-type]


def test_write_html_accepts_bare_write_only_object() -> None:
    class Sink:
        def __init__(self) -> None:
            self.data = bytearray()

        def write(self, buffer: Buffer, /) -> int:
            chunk = bytes(buffer)
            self.data += chunk
            return len(chunk)

    sink = Sink()

    pyromark.write_html("# Hello world", sink)

    assert bytes(sink.data) == b"<h1>Hello world</h1>\n"


class _PartialWriter(io.RawIOBase):
    """Accepts half of each chunk, which a file object is allowed to do."""

    def __init__(self) -> None:
        self.data = bytearray()

    @override
    def writable(self) -> bool:
        return True

    @override
    def write(self, buffer: Buffer, /) -> int:
        chunk = bytes(buffer)
        half = max(1, len(chunk) // 2)
        self.data += chunk[:half]
        return half


class _SilentWriter(io.RawIOBase):
    """Reports nothing, like plenty of file-like objects in the wild."""

    def __init__(self) -> None:
        self.data = bytearray()

    @override
    def writable(self) -> bool:
        return True

    @override
    def write(self, buffer: Buffer, /) -> None:
        self.data += bytes(buffer)


class _OverReportingWriter(io.RawIOBase):
    """Claims to have taken more than it was given."""

    def __init__(self) -> None:
        self.data = bytearray()

    @override
    def writable(self) -> bool:
        return True

    @override
    def write(self, buffer: Buffer, /) -> int:
        chunk = bytes(buffer)
        self.data += chunk
        return len(chunk) * 10


class _RecordingWriter(Protocol):
    data: bytearray

    def write(self, buffer: Buffer, /) -> int | None: ...


@pytest.mark.parametrize(
    "writer_type",
    [_PartialWriter, _SilentWriter, _OverReportingWriter],
    ids=["partial", "silent", "over-reporting"],
)
def test_write_html_honours_reported_length(writer_type: Callable[[], _RecordingWriter]) -> None:
    markdown = "# Hello world\n\n" * 5000
    writer = writer_type()
    pyromark.write_html(markdown, writer)
    assert bytes(writer.data) == pyromark.html(markdown).encode()


def test_write_html_rejects_non_integer_length() -> None:
    class Nonsense(io.RawIOBase):
        @override
        def writable(self) -> bool:
            return True

        @override
        def write(self, buffer: Buffer, /) -> int:
            return "not a length"  # type: ignore[return-value]

    with pytest.raises(TypeError, match=r"."):
        pyromark.write_html("# Hello world" * 5000, Nonsense())


def test_markdown_write_html_matches_function() -> None:
    def highlight(_language: str | None, code: str) -> str:
        return f"<x>{code.strip()}</x>"

    markdown = f"{CODE_BLOCKS}\n\n{TABLE}"
    options = pyromark.Options.ENABLE_TABLES
    md = pyromark.Markdown(options=options, highlight=highlight)

    file = io.BytesIO()
    md.write_html(markdown, file)

    assert file.getvalue().decode() == md.html(markdown)
    assert file.getvalue().decode() == pyromark.html(markdown, options=options, highlight=highlight)
    assert b"<x>x = 1</x>" in file.getvalue()
    assert b"<table>" in file.getvalue()


def test_write_html_rejects_a_write_that_takes_nothing() -> None:
    class Stuck(io.RawIOBase):
        @override
        def writable(self) -> bool:
            return True

        @override
        def write(self, buffer: Buffer, /) -> int:
            return 0

    with pytest.raises(OSError, match=r"^file\.write\(\) wrote nothing$"):
        pyromark.write_html("# Hello world", Stuck())
