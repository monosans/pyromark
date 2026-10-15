from collections.abc import Iterator
from typing import Final, final

from _typeshed import SupportsWrite

from pyromark._options import Options
from pyromark.event import BrokenLinkCallback, Event, LinkDef, Range

__version__: Final[str]

def events(
    markdown: str,
    /,
    *,
    options: Options = Options(0),  # noqa: B008, PYI011
    merge_text: bool = True,
    broken_link_callback: BrokenLinkCallback | None = None,
) -> Iterator[Event]: ...
def events_with_range(
    markdown: str,
    /,
    *,
    options: Options = Options(0),  # noqa: B008, PYI011
    merge_text: bool = False,
    broken_link_callback: BrokenLinkCallback | None = None,
) -> Iterator[tuple[Event, Range]]: ...
def html(
    markdown: str,
    /,
    *,
    options: Options = Options(0),  # noqa: B008, PYI011
    broken_link_callback: BrokenLinkCallback | None = None,
) -> str: ...
def reference_definitions(
    markdown: str,
    /,
    *,
    options: Options = Options(0),  # noqa: B008, PYI011
) -> dict[str, LinkDef]: ...
def write_html(
    markdown: str,
    file: SupportsWrite[bytes],
    /,
    *,
    options: Options = Options(0),  # noqa: B008, PYI011
    broken_link_callback: BrokenLinkCallback | None = None,
) -> None: ...

@final
class Markdown:
    def __init__(
        self,
        *,
        options: Options = Options(0),  # noqa: B008, PYI011
        broken_link_callback: BrokenLinkCallback | None = None,
    ) -> None: ...
    def events(
        self, markdown: str, /, *, merge_text: bool = True
    ) -> Iterator[Event]: ...
    def events_with_range(
        self, markdown: str, /, *, merge_text: bool = False
    ) -> Iterator[tuple[Event, Range]]: ...
    def html(self, markdown: str, /) -> str: ...
    def reference_definitions(self, markdown: str, /) -> dict[str, LinkDef]: ...
    def write_html(
        self, markdown: str, file: SupportsWrite[bytes], /
    ) -> None: ...
