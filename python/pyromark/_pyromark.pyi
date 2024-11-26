# ruff: noqa: E301, E302
from typing import Final

from typing_extensions import final

from pyromark._options import Options
from pyromark.event import Event

__version__: Final[str]

def events(
    markdown: str,
    /,
    *,
    options: Options = Options(0),  # noqa: B008, PYI011
    merge_text: bool = True,
) -> tuple[Event, ...]: ...
def html(markdown: str, /, *, options: Options = Options(0)) -> str: ...  # noqa: B008, PYI011
@final
class Markdown:
    def __init__(self, *, options: Options = Options(0)) -> None: ...  # noqa: B008, PYI011
    def events(
        self, markdown: str, /, *, merge_text: bool = True
    ) -> tuple[Event, ...]: ...
    def html(self, markdown: str, /) -> str: ...
