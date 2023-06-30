from typing_extensions import final

from ._extensions import Extensions

__version__: str

@final
class Markdown:
    def __init__(self, *, extensions: Extensions | None = None) -> None: ...
    def convert(self, text: str) -> str: ...

def markdown(text: str, *, extensions: Extensions | None = None) -> str: ...
