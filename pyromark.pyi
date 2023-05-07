from typing import Sequence

from typing_extensions import Literal, TypeAlias

__version__: str
_Extension: TypeAlias = Literal[
    "tables",
    "footnotes",
    "strikethrough",
    "tasklists",
    "smart_punctuation",
    "heading_attributes",
]

class Markdown:
    def __init__(self, *, extensions: Sequence[_Extension] | None = None) -> None: ...
    def convert(self, text: str) -> str: ...

def markdown(text: str, *, extensions: Sequence[_Extension] | None = None) -> str: ...
