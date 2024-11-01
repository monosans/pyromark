from __future__ import annotations

from typing import Optional, Union

from typing_extensions import Literal, TypeAlias, TypedDict

HeadingLevel: TypeAlias = Literal["H1", "H2", "H3", "H4", "H5", "H6"]


class Heading(TypedDict):
    level: HeadingLevel
    id: Optional[str]
    classes: tuple[str, ...]
    attrs: tuple[tuple[str, Optional[str]], ...]


BlockQuoteKind: TypeAlias = Literal[
    "Note", "Tip", "Important", "Warning", "Caution"
]

CodeBlockKind: TypeAlias = Union[
    Literal["Indented"], tuple[Literal["Fenced"], str]
]

Alignment: TypeAlias = Literal["None", "Left", "Center", "Right"]

LinkType: TypeAlias = Literal[
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


class Link(TypedDict):
    link_type: LinkType
    dest_url: str
    title: str
    id: str


class Image(TypedDict):
    link_type: LinkType
    dest_url: str
    title: str
    id: str


MetadataBlockKind: TypeAlias = Literal["YamlStyle", "PlusesStyle"]

Tag: TypeAlias = Union[
    Literal[
        "Paragraph",
        "HtmlBlock",
        "DefinitionList",
        "DefinitionListTitle",
        "DefinitionListDefinition",
        "TableHead",
        "TableRow",
        "TableCell",
        "Emphasis",
        "Strong",
        "Strikethrough",
    ],
    tuple[Literal["Heading"], Heading],
    tuple[Literal["BlockQuote"], Optional[BlockQuoteKind]],
    tuple[Literal["CodeBlock"], CodeBlockKind],
    tuple[Literal["List"], Optional[int]],
    tuple[Literal["FootnoteDefinition"], str],
    tuple[Literal["Table"], tuple[Alignment, ...]],
    tuple[Literal["Link"], Link],
    tuple[Literal["Image"], Image],
    tuple[Literal["MetadataBlock"], MetadataBlockKind],
]

TagEnd: TypeAlias = Union[
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
    ],
    tuple[Heading, HeadingLevel],
    tuple[Literal["BlockQuote"], Optional[BlockQuoteKind]],
    tuple[Literal["List"], bool],
]

Event: TypeAlias = Union[
    Literal[
        "SoftBreak",
        "HardBreak",
        "Rule",
        "Emphasis",
        "Strong",
        "Strikethrough",
        "Link",
        "Image",
    ],
    tuple[Literal["Start"], Tag],
    tuple[Literal["End"], TagEnd],
    tuple[Literal["Text"], str],
    tuple[Literal["Code"], str],
    tuple[Literal["InlineMath"], str],
    tuple[Literal["DisplayMath"], str],
    tuple[Literal["Html"], str],
    tuple[Literal["InlineHtml"], str],
    tuple[Literal["FootnoteReference"], str],
    tuple[Literal["TaskListMarker"], bool],
    tuple[Literal["MetadataBlock"], MetadataBlockKind],
]
