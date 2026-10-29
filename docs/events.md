# Events

[`events`][pyromark.events] walks the document as a flat stream: a `Start` and an `End` around every element, with text and other leaves in between.

```python
import pyromark

assert list(pyromark.events("Hello *world*")) == [
    {"Start": "Paragraph"},
    {"Text": "Hello "},
    {"Start": "Emphasis"},
    {"Text": "world"},
    {"End": "Emphasis"},
    {"End": "Paragraph"},
]
```

Use `match` to pick out what you need. Pass `options=` to get events of extensions, as with [`html`][pyromark.html].

## Build a table of contents

```python
import pyromark

markdown = "# Intro\n\n## Install with `uv`\n\n## Usage\n"
toc = []
title = ""
for event in pyromark.events(markdown):
    match event:
        case {"Start": {"Heading": _}}:
            title = ""
        case {"Text": text} | {"Code": text}:
            title += text
        case {"End": {"Heading": level}}:
            toc.append((level, title))

assert toc == [("H1", "Intro"), ("H2", "Install with uv"), ("H2", "Usage")]
```

## Collect links

```python
import pyromark

markdown = "[Docs](https://example.com) and ![logo](/logo.png)"
links = []
for event in pyromark.events(markdown):
    match event:
        case {"Start": {"Link": link} | {"Image": link}}:
            links.append(link["dest_url"])

assert links == ["https://example.com", "/logo.png"]
```

## Extract plain text

```python
import pyromark

text = ""
for event in pyromark.events("# Title\n\nSome *styled*\ntext."):
    match event:
        case {"Text": chunk} | {"Code": chunk}:
            text += chunk
        case "SoftBreak" | "HardBreak":
            text += " "
        case {"End": "Paragraph" | {"Heading": _}}:
            text += "\n"

assert text == "Title\nSome styled text.\n"
```

## Find where an element is in the source

[`events_with_range`][pyromark.events_with_range] pairs every event with its [`Range`][pyromark.event.Range] in UTF-8 bytes, so slice `markdown.encode()`, not `markdown`:

```python
import pyromark

markdown = "Café\n\n# Привет *мир*\n"
source = markdown.encode()
for event, span in pyromark.events_with_range(markdown):
    match event:
        case {"Start": {"Heading": _}}:
            heading = source[span["start"] : span["end"]].decode()

assert heading == "# Привет *мир*\n"
```

## All events

Leaves:

| Event                        | Meaning                            |
| ---------------------------- | ---------------------------------- |
| `{"Text": "..."}`            | text                               |
| `{"Code": "..."}`            | `` `inline code` ``                |
| `{"Html": "..."}`            | a line of an HTML block            |
| `{"InlineHtml": "<b>"}`      | an inline HTML tag                 |
| `{"InlineMath": "..."}`      | `$math$`                           |
| `{"DisplayMath": "..."}`     | `$$math$$`                         |
| `{"FootnoteReference": "1"}` | `[^1]`                             |
| `{"TaskListMarker": True}`   | `[x]`, or `[ ]` when `False`       |
| `"SoftBreak"`                | a line break inside a paragraph    |
| `"HardBreak"`                | a line ending in two spaces or `\` |
| `"Rule"`                     | `---`                              |

Elements, as `{"Start": ...}` and `{"End": ...}`:

| Element         | `Start`                                                                               | `End`                        |
| --------------- | ------------------------------------------------------------------------------------- | ---------------------------- |
| Paragraph       | `"Paragraph"`                                                                         | `"Paragraph"`                |
| Heading         | `{"Heading": {"level": "H1", "id": None, "classes": (), "attrs": ()}}`                | `{"Heading": "H1"}`          |
| Block quote     | `{"BlockQuote": None}`, or `"Note"`, `"Tip"`, `"Important"`, `"Warning"`, `"Caution"` | same as `Start`              |
| Code block      | `{"CodeBlock": {"Fenced": "python"}}` or `{"CodeBlock": "Indented"}`                  | `"CodeBlock"`                |
| HTML block      | `"HtmlBlock"`                                                                         | `"HtmlBlock"`                |
| List            | `{"List": None}` for bullets, `{"List": 1}` for numbers starting at 1                 | `{"List": True}` if numbered |
| List item       | `"Item"`                                                                              | `"Item"`                     |
| Footnote        | `{"FootnoteDefinition": "1"}`                                                         | `"FootnoteDefinition"`       |
| Definition list | `"DefinitionList"`, `"DefinitionListTitle"`, `"DefinitionListDefinition"`             | same as `Start`              |
| Table           | `{"Table": ("None", "Left", "Center", "Right")}`, the column alignments               | `"Table"`                    |
| Table parts     | `"TableHead"`, `"TableRow"`, `"TableCell"`                                            | same as `Start`              |
| Inline styles   | `"Emphasis"`, `"Strong"`, `"Strikethrough"`, `"Superscript"`, `"Subscript"`           | same as `Start`              |
| Link            | `{"Link": {"link_type": "Inline", "dest_url": "/", "title": "", "id": ""}}`           | `"Link"`                     |
| Image           | `{"Image": {...}}`, same fields as `Link`                                             | `"Image"`                    |
| Front matter    | `{"MetadataBlock": "YamlStyle"}` or `"PlusesStyle"`                                   | same as `Start`              |

A heading's `id`, `classes` and `attrs` come from `{ #id .class key=value }` with `ENABLE_HEADING_ATTRIBUTES`. A link's `link_type` is one of `"Inline"`, `"Reference"`, `"ReferenceUnknown"`, `"Collapsed"`, `"CollapsedUnknown"`, `"Shortcut"`, `"ShortcutUnknown"`, `"Autolink"`, `"Email"` or `{"WikiLink": {"has_pothole": True}}`; `id` is the reference label.
