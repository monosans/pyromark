from collections.abc import Iterator
from typing import Final, final

from pyromark._options import Options
from pyromark.event import BrokenLinkCallback, Event, Range

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
