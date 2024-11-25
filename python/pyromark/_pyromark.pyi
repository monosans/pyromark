# ruff: noqa: E301, E302
from typing import Final

from typing_extensions import final

from pyromark._options import Options
from pyromark.event import Event

__version__: Final[str]

def events(
    markdown: str, /, *, options: Options | None = None, merge_text: bool = True
) -> list[Event]: ...
def html(markdown: str, /, *, options: Options | None = None) -> str: ...
@final
class Markdown:
    def __init__(self, *, options: Options | None = None) -> None: ...
    def events(
        self, markdown: str, /, *, merge_text: bool = True
    ) -> list[Event]: ...
    def html(self, markdown: str, /) -> str: ...
