# ruff: noqa: E301, E302
from typing_extensions import final

from ._extensions import Extensions
from .event import Event

__version__: str

def events(
    text: str,
    /,
    *,
    extensions: Extensions | None = None,
    merge_text: bool = True,
) -> tuple[Event, ...]: ...
def markdown(text: str, *, extensions: Extensions | None = None) -> str: ...
@final
class Markdown:
    def __init__(self, *, extensions: Extensions | None = None) -> None: ...
    def events(
        self, text: str, /, *, merge_text: bool = True
    ) -> tuple[Event, ...]: ...
    def convert(self, text: str) -> str: ...
