# ruff: noqa: PYI030
from __future__ import annotations

from typing import Optional, Union

from typing_extensions import Literal, TypeAlias, TypedDict

_HeadingLevel: TypeAlias = Literal["H1", "H2", "H3", "H4", "H5", "H6"]


class _HeadingData(TypedDict):
    level: _HeadingLevel
    id: Optional[str]
    classes: tuple[str, ...]
    attrs: tuple[tuple[str, Optional[str]], ...]


class _HeadingStart(TypedDict):
    Heading: _HeadingData


_BlockQuoteKind: TypeAlias = Literal[
    "Note", "Tip", "Important", "Warning", "Caution"
]


class _BlockQuote(TypedDict):
    BlockQuote: Optional[_BlockQuoteKind]


class _Fenced(TypedDict):
    Fenced: str


_CodeBlockKind: TypeAlias = Union[Literal["Indented"], _Fenced]


class _CodeBlock(TypedDict):
    CodeBlock: _CodeBlockKind


class _ListStart(TypedDict):
    List: Optional[int]


class _FootnoteDefinition(TypedDict):
    FootnoteDefinition: str


_Alignment: TypeAlias = Literal["None", "Left", "Center", "Right"]


class _Table(TypedDict):
    Table: tuple[_Alignment, ...]


class _WikiLink(TypedDict):
    has_pothole: bool


_LinkType: TypeAlias = Union[
    Literal["Inline"],
    Literal["Reference"],
    Literal["ReferenceUnknown"],
    Literal["Collapsed"],
    Literal["CollapsedUnknown"],
    Literal["Shortcut"],
    Literal["ShortcutUnknown"],
    Literal["Autolink"],
    Literal["Email"],
    _WikiLink,
]


class _LinkData(TypedDict):
    link_type: _LinkType
    dest_url: str
    title: str
    id: str


class _Link(TypedDict):
    Link: _LinkData


class _ImageData(TypedDict):
    link_type: _LinkType
    dest_url: str
    title: str
    id: str


class _Image(TypedDict):
    Image: _ImageData


_MetadataBlockKind: TypeAlias = Literal["YamlStyle", "PlusesStyle"]


class _MetadataBlock(TypedDict):
    MetadataBlock: _MetadataBlockKind


_Tag: TypeAlias = Union[
    Literal["Paragraph"],
    _HeadingStart,
    _BlockQuote,
    _CodeBlock,
    Literal["HtmlBlock"],
    _ListStart,
    Literal["Item"],
    _FootnoteDefinition,
    Literal["DefinitionList"],
    Literal["DefinitionListTitle"],
    Literal["DefinitionListDefinition"],
    _Table,
    Literal["TableHead"],
    Literal["TableRow"],
    Literal["TableCell"],
    Literal["Emphasis"],
    Literal["Strong"],
    Literal["Strikethrough"],
    Literal["Superscript"],
    Literal["Subscript"],
    _Link,
    _Image,
    _MetadataBlock,
]


class _HeadingEnd(TypedDict):
    Heading: _HeadingLevel


class _ListEnd(TypedDict):
    List: bool


_TagEnd: TypeAlias = Union[
    Literal["Paragraph"],
    _HeadingEnd,
    _BlockQuote,
    Literal["CodeBlock"],
    Literal["HtmlBlock"],
    _ListEnd,
    Literal["Item"],
    Literal["FootnoteDefinition"],
    Literal["DefinitionList"],
    Literal["DefinitionListTitle"],
    Literal["DefinitionListDefinition"],
    Literal["Table"],
    Literal["TableHead"],
    Literal["TableRow"],
    Literal["TableCell"],
    Literal["Emphasis"],
    Literal["Strong"],
    Literal["Strikethrough"],
    Literal["Superscript"],
    Literal["Subscript"],
    Literal["Link"],
    Literal["Image"],
    _MetadataBlock,
]


class _Start(TypedDict):
    Start: _Tag


class _End(TypedDict):
    End: _TagEnd


class _Text(TypedDict):
    Text: str


class _Code(TypedDict):
    Code: str


class _InlineMath(TypedDict):
    InlineMath: str


class _DisplayMath(TypedDict):
    DisplayMath: str


class _Html(TypedDict):
    Html: str


class _InlineHtml(TypedDict):
    Html: str


class _FootnoteReference(TypedDict):
    FootnoteReference: str


class _TaskListMarker(TypedDict):
    FootnoteReference: str


Event: TypeAlias = Union[
    _Start,
    _End,
    _Text,
    _Code,
    _InlineMath,
    _DisplayMath,
    _Html,
    _InlineHtml,
    _FootnoteReference,
    Literal["SoftBreak"],
    Literal["HardBreak"],
    Literal["Rule"],
    _TaskListMarker,
]


class Range(TypedDict):
    start: int
    end: int


__all__ = ("Event", "Range")
