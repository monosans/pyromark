from typing import Final
from collections.abc import Callable

from typing_extensions import final

from pyromark._options import Options
from pyromark.event import Event, Range

__version__: Final[str]

# Type alias for broken link callback
# Takes a dict with 'reference' and 'span' keys
# Returns either None or a tuple of (url, title)
BrokenLinkCallback = Callable[[dict[str, str | tuple[int, int]]], tuple[str, str] | None]

def events(
    markdown: str,
    /,
    *,
    options: Options = Options(0),  # noqa: B008, PYI011
    merge_text: bool = True,
    broken_link_callback: BrokenLinkCallback | None = None,
) -> tuple[Event, ...]: ...
def events_with_range(
    markdown: str,
    /,
    *,
    options: Options = Options(0),  # noqa: B008, PYI011
    broken_link_callback: BrokenLinkCallback | None = None,
) -> tuple[tuple[Event, Range], ...]: ...
def html(
    markdown: str,
    /,
    *,
    options: Options = Options(0),  # noqa: B008, PYI011
    broken_link_callback: BrokenLinkCallback | None = None,
) -> str: ...

@final
class Markdown:
    def __init__(self, *, options: Options = Options(0)) -> None: ...  # noqa: B008, PYI011
    def events(
        self,
        markdown: str,
        /,
        *,
        merge_text: bool = True,
        broken_link_callback: BrokenLinkCallback | None = None,
    ) -> tuple[Event, ...]: ...
    def events_with_range(
        self,
        markdown: str,
        /,
        *,
        broken_link_callback: BrokenLinkCallback | None = None,
    ) -> tuple[tuple[Event, Range], ...]: ...
    def html(
        self,
        markdown: str,
        /,
        *,
        broken_link_callback: BrokenLinkCallback | None = None,
    ) -> str: ...
