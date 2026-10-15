from collections.abc import Iterator
from typing import Final, final

from _typeshed import SupportsWrite

from pyromark._options import Options
from pyromark._theme import Theme
from pyromark.event import (
    BrokenLinkCallback,
    Event,
    HighlightCallback,
    LinkDef,
    Range,
)

__version__: Final[str]

def events(
    markdown: str,
    /,
    *,
    options: Options = Options(0),  # noqa: B008, PYI011
    merge_text: bool = True,
    broken_link_callback: BrokenLinkCallback | None = None,
) -> Iterator[Event]:
    """Iterate over the document's events.

    Returns a lazy iterator: wrap it in `tuple()` if you need a sequence.
    Adjacent text events are merged unless `merge_text=False`.

    Examples:
        ```python
        for event in pyromark.events("# Hello world"):
            match event:
                case {"Start": {"Heading": {"level": level}}}:
                    print(f"{level} heading started")
                case {"Text": text}:
                    print(f"Got {text!r}")
                case {"End": {"Heading": level}}:
                    print(f"{level} heading ended")
        ```
    """

def events_with_range(
    markdown: str,
    /,
    *,
    options: Options = Options(0),  # noqa: B008, PYI011
    merge_text: bool = False,
    broken_link_callback: BrokenLinkCallback | None = None,
) -> Iterator[tuple[Event, Range]]:
    """Like `events`, but yields `(event, range)` pairs.

    Ranges are UTF-8 byte offsets: slice `markdown.encode()`, not
    `markdown`. Text is not merged by default, because each piece has its
    own range.

    Examples:
        ```python
        markdown = "# Hello world"
        for event, range_ in pyromark.events_with_range(markdown):
            source = markdown.encode()[range_["start"] : range_["end"]]
            print(event, source.decode())
        ```
    """

def html(
    markdown: str,
    /,
    *,
    options: Options = Options(0),  # noqa: B008, PYI011
    broken_link_callback: BrokenLinkCallback | None = None,
    highlight: Theme | HighlightCallback | None = None,
) -> str:
    r"""Render Markdown to HTML.

    The output is not sanitized: raw HTML passes through, as `CommonMark`
    requires.

    Examples:
        ```python
        html = pyromark.html("# Hello world")
        assert html == "<h1>Hello world</h1>\n"
        ```

        Resolve references the document does not define:

        ```python
        html = pyromark.html(
            "[Hello]",
            broken_link_callback=lambda link: (f"/{link['reference']}", ""),
        )
        assert html == '<p><a href="/Hello">Hello</a></p>\n'
        ```

        Highlight code blocks:

        ```python
        html = pyromark.html(
            "~~~python\nx = 1\n~~~", highlight=pyromark.Theme.INSPIRED_GITHUB
        )
        ```
    """

def reference_definitions(
    markdown: str,
    /,
    *,
    options: Options = Options(0),  # noqa: B008, PYI011
) -> dict[str, LinkDef]:
    """Return the document's link reference definitions, keyed by label.

    They come in document order. Labels match case-insensitively, and the
    first definition wins. Only the block level pass runs, so this is cheaper
    than `events`.

    Examples:
        ```python
        definitions = pyromark.reference_definitions("[foo]: /a 'A'")
        assert definitions == {
            "foo": {"dest": "/a", "title": "A", "span": {"start": 0, "end": 13}}
        }
        ```
    """

def write_html(
    markdown: str,
    file: SupportsWrite[bytes],
    /,
    *,
    options: Options = Options(0),  # noqa: B008, PYI011
    broken_link_callback: BrokenLinkCallback | None = None,
    highlight: Theme | HighlightCallback | None = None,
) -> None:
    r"""Like `html`, but writes UTF-8 into a binary file.

    The output goes to `file.write()` in 64 KiB chunks instead of being
    returned as one `str`.

    Examples:
        ```python
        import io

        file = io.BytesIO()
        pyromark.write_html("# Hello world", file)
        assert file.getvalue() == b"<h1>Hello world</h1>\n"
        ```
    """

@final
class Markdown:
    r"""Parser settings, given once and reused for every call.

    Takes the same keyword arguments as `html`; `highlight` only affects
    `html` and `write_html`. Instances are immutable, so one can be shared
    between threads.

    Examples:
        ```python
        md = pyromark.Markdown(options=pyromark.Options.ENABLE_TABLES)
        assert md.html("# Hello world") == "<h1>Hello world</h1>\n"
        ```
    """
    def __init__(
        self,
        *,
        options: Options = Options(0),  # noqa: B008, PYI011
        broken_link_callback: BrokenLinkCallback | None = None,
        highlight: Theme | HighlightCallback | None = None,
    ) -> None: ...
    def events(
        self, markdown: str, /, *, merge_text: bool = True
    ) -> Iterator[Event]:
        """Same as [`pyromark.events`][], with these settings."""
    def events_with_range(
        self, markdown: str, /, *, merge_text: bool = False
    ) -> Iterator[tuple[Event, Range]]:
        """Same as [`pyromark.events_with_range`][], with these settings."""
    def html(self, markdown: str, /) -> str:
        """Same as [`pyromark.html`][], with these settings."""
    def reference_definitions(self, markdown: str, /) -> dict[str, LinkDef]:
        """Same as [`pyromark.reference_definitions`][], with these settings."""
    def write_html(self, markdown: str, file: SupportsWrite[bytes], /) -> None:
        """Same as [`pyromark.write_html`][], with these settings."""
