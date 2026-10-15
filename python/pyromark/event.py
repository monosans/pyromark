"""Types describing the events the parser yields.

Every event is either a single-key dict, such as `{"Text": "hi"}` or
`{"Start": {"Heading": {"level": "H1", ...}}}`, or one of the bare
strings `"SoftBreak"`, `"HardBreak"` and `"Rule"`. The key names and
the nesting mirror pulldown-cmark's own enums.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Final, Literal, TypeAlias, final

from typing_extensions import TypedDict

_HeadingLevel: TypeAlias = Literal["H1", "H2", "H3", "H4", "H5", "H6"]


@final
class _HeadingData(TypedDict):
    level: _HeadingLevel
    id: str | None
    classes: tuple[str, ...]
    attrs: tuple[tuple[str, str | None], ...]


@final
class _HeadingStart(TypedDict):
    Heading: _HeadingData


_BlockQuoteKind: TypeAlias = Literal[
    "Note", "Tip", "Important", "Warning", "Caution"
]


@final
class _BlockQuote(TypedDict):
    BlockQuote: _BlockQuoteKind | None


@final
class _Fenced(TypedDict):
    Fenced: str


_CodeBlockKind: TypeAlias = Literal["Indented"] | _Fenced


@final
class _CodeBlock(TypedDict):
    CodeBlock: _CodeBlockKind


@final
class _ListStart(TypedDict):
    List: int | None


@final
class _FootnoteDefinition(TypedDict):
    FootnoteDefinition: str


_Alignment: TypeAlias = Literal["None", "Left", "Center", "Right"]


@final
class _Table(TypedDict):
    Table: tuple[_Alignment, ...]


@final
class _WikiLinkData(TypedDict):
    has_pothole: bool


@final
class _WikiLink(TypedDict):
    WikiLink: _WikiLinkData


_LinkType: TypeAlias = (
    Literal[
        "Inline",
        "Reference",
        "ReferenceUnknown",
        "Collapsed",
        "CollapsedUnknown",
        "Shortcut",
        "ShortcutUnknown",
        "Autolink",
        "Email",
    ]
    | _WikiLink
)


@final
class _LinkData(TypedDict):
    link_type: _LinkType
    dest_url: str
    title: str
    id: str


@final
class _Link(TypedDict):
    Link: _LinkData


@final
class _Image(TypedDict):
    Image: _LinkData


_MetadataBlockKind: TypeAlias = Literal["YamlStyle", "PlusesStyle"]


@final
class _MetadataBlock(TypedDict):
    MetadataBlock: _MetadataBlockKind


_Tag: TypeAlias = (
    Literal[
        "Paragraph",
        "HtmlBlock",
        "Item",
        "DefinitionList",
        "DefinitionListTitle",
        "DefinitionListDefinition",
        "TableHead",
        "TableRow",
        "TableCell",
        "Emphasis",
        "Strong",
        "Strikethrough",
        "Superscript",
        "Subscript",
    ]
    | _HeadingStart
    | _BlockQuote
    | _CodeBlock
    | _ListStart
    | _FootnoteDefinition
    | _Table
    | _Link
    | _Image
    | _MetadataBlock
)


@final
class _HeadingEnd(TypedDict):
    Heading: _HeadingLevel


@final
class _ListEnd(TypedDict):
    List: bool


_TagEnd: TypeAlias = (
    Literal[
        "Paragraph",
        "CodeBlock",
        "HtmlBlock",
        "Item",
        "FootnoteDefinition",
        "DefinitionList",
        "DefinitionListTitle",
        "DefinitionListDefinition",
        "Table",
        "TableHead",
        "TableRow",
        "TableCell",
        "Emphasis",
        "Strong",
        "Strikethrough",
        "Superscript",
        "Subscript",
        "Link",
        "Image",
    ]
    | _HeadingEnd
    | _BlockQuote
    | _ListEnd
    | _MetadataBlock
)


@final
class _Start(TypedDict):
    Start: _Tag


@final
class _End(TypedDict):
    End: _TagEnd


@final
class _Text(TypedDict):
    Text: str


@final
class _Code(TypedDict):
    Code: str


@final
class _InlineMath(TypedDict):
    InlineMath: str


@final
class _DisplayMath(TypedDict):
    DisplayMath: str


@final
class _Html(TypedDict):
    Html: str


@final
class _InlineHtml(TypedDict):
    InlineHtml: str


@final
class _FootnoteReference(TypedDict):
    FootnoteReference: str


@final
class _TaskListMarker(TypedDict):
    TaskListMarker: bool


Event: TypeAlias = (
    Literal["SoftBreak", "HardBreak", "Rule"]
    | _Start
    | _End
    | _Text
    | _Code
    | _InlineMath
    | _DisplayMath
    | _Html
    | _InlineHtml
    | _FootnoteReference
    | _TaskListMarker
)
"""One element of the document.

Match on it to pick out the elements you care about; see the
[`events`][pyromark.events] example.
"""


@final
class Range(TypedDict):
    """A region of the source, as UTF-8 byte offsets.

    Slice `markdown.encode()` with it, not `markdown`, or non-ASCII text
    shifts the result.
    """

    start: int
    end: int


@final
class BrokenLink(TypedDict):
    """A link reference the document does not define."""

    span: Range
    link_type: _LinkType
    reference: str


BrokenLinkCallback: TypeAlias = Callable[[BrokenLink], tuple[str, str] | None]
"""Resolves a link reference that has no definition.

Returns `(destination_url, title)`, or `None` to leave the reference as
text. If it raises, the call it was passed to stops and raises it.
"""

__all__: Final = ("BrokenLink", "BrokenLinkCallback", "Event", "Range")
