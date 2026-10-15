# ruff: noqa: E501
from __future__ import annotations

import functools
import operator
from collections.abc import Mapping

import pyromark
from pyromark.event import Event

TABLE = """\
| foo | bar |
| --- | --- |
| baz | bim |\
"""


BROKEN_LINKS = "[a][b] and [c][] and [d] and ![e]"


ALL_OPTIONS = functools.reduce(
    operator.or_, pyromark.Options.__members__.values()
)


EVENTS_TESTDATA: Mapping[str, tuple[str, tuple[Event, ...]]] = {
    "yaml_metadata": (
        "---\ntitle: Meta\n---\n",
        (
            {"Start": {"MetadataBlock": "YamlStyle"}},
            {"Text": "title: Meta\n"},
            {"End": {"MetadataBlock": "YamlStyle"}},
        ),
    ),
    "pluses_metadata": (
        "+++\ntitle: Meta\n+++\n",
        (
            {"Start": {"MetadataBlock": "PlusesStyle"}},
            {"Text": "title: Meta\n"},
            {"End": {"MetadataBlock": "PlusesStyle"}},
        ),
    ),
    "headings": (
        "# h1 { #the-id .c1 .c2 attr1 attr2=v2 }\n\n## h2\n\n### h3\n\n#### h4\n\n##### h5\n\n###### h6\n",
        (
            {
                "Start": {
                    "Heading": {
                        "level": "H1",
                        "id": "the-id",
                        "classes": ("c1", "c2"),
                        "attrs": (("attr1", None), ("attr2", "v2")),
                    }
                }
            },
            {"Text": "h1"},
            {"End": {"Heading": "H1"}},
            {
                "Start": {
                    "Heading": {
                        "level": "H2",
                        "id": None,
                        "classes": (),
                        "attrs": (),
                    }
                }
            },
            {"Text": "h2"},
            {"End": {"Heading": "H2"}},
            {
                "Start": {
                    "Heading": {
                        "level": "H3",
                        "id": None,
                        "classes": (),
                        "attrs": (),
                    }
                }
            },
            {"Text": "h3"},
            {"End": {"Heading": "H3"}},
            {
                "Start": {
                    "Heading": {
                        "level": "H4",
                        "id": None,
                        "classes": (),
                        "attrs": (),
                    }
                }
            },
            {"Text": "h4"},
            {"End": {"Heading": "H4"}},
            {
                "Start": {
                    "Heading": {
                        "level": "H5",
                        "id": None,
                        "classes": (),
                        "attrs": (),
                    }
                }
            },
            {"Text": "h5"},
            {"End": {"Heading": "H5"}},
            {
                "Start": {
                    "Heading": {
                        "level": "H6",
                        "id": None,
                        "classes": (),
                        "attrs": (),
                    }
                }
            },
            {"Text": "h6"},
            {"End": {"Heading": "H6"}},
        ),
    ),
    "block_quotes": (
        "> plain\n\n> [!NOTE]\n> n\n\n> [!TIP]\n> t\n\n> [!IMPORTANT]\n> i\n\n> [!WARNING]\n> w\n\n> [!CAUTION]\n> c\n",
        (
            {"Start": {"BlockQuote": None}},
            {"Start": "Paragraph"},
            {"Text": "plain"},
            {"End": "Paragraph"},
            {"End": {"BlockQuote": None}},
            {"Start": {"BlockQuote": "Note"}},
            {"Start": "Paragraph"},
            {"Text": "n"},
            {"End": "Paragraph"},
            {"End": {"BlockQuote": "Note"}},
            {"Start": {"BlockQuote": "Tip"}},
            {"Start": "Paragraph"},
            {"Text": "t"},
            {"End": "Paragraph"},
            {"End": {"BlockQuote": "Tip"}},
            {"Start": {"BlockQuote": "Important"}},
            {"Start": "Paragraph"},
            {"Text": "i"},
            {"End": "Paragraph"},
            {"End": {"BlockQuote": "Important"}},
            {"Start": {"BlockQuote": "Warning"}},
            {"Start": "Paragraph"},
            {"Text": "w"},
            {"End": "Paragraph"},
            {"End": {"BlockQuote": "Warning"}},
            {"Start": {"BlockQuote": "Caution"}},
            {"Start": "Paragraph"},
            {"Text": "c"},
            {"End": "Paragraph"},
            {"End": {"BlockQuote": "Caution"}},
        ),
    ),
    "code": (
        "    indented\n\n```rust\nfenced\n```\n\n`inline`\n",
        (
            {"Start": {"CodeBlock": "Indented"}},
            {"Text": "indented\n"},
            {"End": "CodeBlock"},
            {"Start": {"CodeBlock": {"Fenced": "rust"}}},
            {"Text": "fenced\n"},
            {"End": "CodeBlock"},
            {"Start": "Paragraph"},
            {"Code": "inline"},
            {"End": "Paragraph"},
        ),
    ),
    "html": (
        "<div>\nblock\n</div>\n\ntext <span>inline</span>\n",
        (
            {"Start": "HtmlBlock"},
            {"Html": "<div>\n"},
            {"Html": "block\n"},
            {"Html": "</div>\n"},
            {"End": "HtmlBlock"},
            {"Start": "Paragraph"},
            {"Text": "text "},
            {"InlineHtml": "<span>"},
            {"Text": "inline"},
            {"InlineHtml": "</span>"},
            {"End": "Paragraph"},
        ),
    ),
    "lists": (
        "- a\n\n3. b\n\n- [ ] todo\n- [x] done\n",
        (
            {"Start": {"List": None}},
            {"Start": "Item"},
            {"Text": "a"},
            {"End": "Item"},
            {"End": {"List": False}},
            {"Start": {"List": 3}},
            {"Start": "Item"},
            {"Text": "b"},
            {"End": "Item"},
            {"End": {"List": True}},
            {"Start": {"List": None}},
            {"Start": "Item"},
            {"TaskListMarker": False},
            {"Text": "todo"},
            {"End": "Item"},
            {"Start": "Item"},
            {"TaskListMarker": True},
            {"Text": "done"},
            {"End": "Item"},
            {"End": {"List": False}},
        ),
    ),
    "footnotes": (
        "ref[^1]\n\n[^1]: def\n",
        (
            {"Start": "Paragraph"},
            {"Text": "ref"},
            {"FootnoteReference": "1"},
            {"End": "Paragraph"},
            {"Start": {"FootnoteDefinition": "1"}},
            {"Start": "Paragraph"},
            {"Text": "def"},
            {"End": "Paragraph"},
            {"End": "FootnoteDefinition"},
        ),
    ),
    "definition_list": (
        "title\n  : definition\n",
        (
            {"Start": "DefinitionList"},
            {"Start": "DefinitionListTitle"},
            {"Text": "title"},
            {"End": "DefinitionListTitle"},
            {"Start": "DefinitionListDefinition"},
            {"Text": "definition"},
            {"End": "DefinitionListDefinition"},
            {"End": "DefinitionList"},
        ),
    ),
    "table": (
        "| a | b | c | d |\n|---|:--|:-:|--:|\n| 1 | 2 | 3 | 4 |\n",
        (
            {"Start": {"Table": ("None", "Left", "Center", "Right")}},
            {"Start": "TableHead"},
            {"Start": "TableCell"},
            {"Text": "a"},
            {"End": "TableCell"},
            {"Start": "TableCell"},
            {"Text": "b"},
            {"End": "TableCell"},
            {"Start": "TableCell"},
            {"Text": "c"},
            {"End": "TableCell"},
            {"Start": "TableCell"},
            {"Text": "d"},
            {"End": "TableCell"},
            {"End": "TableHead"},
            {"Start": "TableRow"},
            {"Start": "TableCell"},
            {"Text": "1"},
            {"End": "TableCell"},
            {"Start": "TableCell"},
            {"Text": "2"},
            {"End": "TableCell"},
            {"Start": "TableCell"},
            {"Text": "3"},
            {"End": "TableCell"},
            {"Start": "TableCell"},
            {"Text": "4"},
            {"End": "TableCell"},
            {"End": "TableRow"},
            {"End": "Table"},
        ),
    ),
    "inline_styles": (
        "*em* **strong** ~sub~ ~~strike~~ ^sup^\n",
        (
            {"Start": "Paragraph"},
            {"Start": "Emphasis"},
            {"Text": "em"},
            {"End": "Emphasis"},
            {"Text": " "},
            {"Start": "Strong"},
            {"Text": "strong"},
            {"End": "Strong"},
            {"Text": " "},
            {"Start": "Subscript"},
            {"Text": "sub"},
            {"End": "Subscript"},
            {"Text": " "},
            {"Start": "Strikethrough"},
            {"Text": "strike"},
            {"End": "Strikethrough"},
            {"Text": " "},
            {"Start": "Superscript"},
            {"Text": "sup"},
            {"End": "Superscript"},
            {"End": "Paragraph"},
        ),
    ),
    "breaks": (
        "soft\nbreak\n\nhard  \nbreak\n\n---\n",
        (
            {"Start": "Paragraph"},
            {"Text": "soft"},
            "SoftBreak",
            {"Text": "break"},
            {"End": "Paragraph"},
            {"Start": "Paragraph"},
            {"Text": "hard"},
            "HardBreak",
            {"Text": "break"},
            {"End": "Paragraph"},
            "Rule",
        ),
    ),
    "math": (
        "$inline$\n\n$$display$$\n",
        (
            {"Start": "Paragraph"},
            {"InlineMath": "inline"},
            {"End": "Paragraph"},
            {"Start": "Paragraph"},
            {"DisplayMath": "display"},
            {"End": "Paragraph"},
        ),
    ),
    "links": (
        "[inline](/u 't')\n\n[ref][lbl]\n\n[lbl][]\n\n[lbl]\n\n<http://foo.bar/baz>\n\n<john@example.org>\n\n![img](/i 'it')\n\n[lbl]: /url 'title'\n",
        (
            {"Start": "Paragraph"},
            {
                "Start": {
                    "Link": {
                        "link_type": "Inline",
                        "dest_url": "/u",
                        "title": "t",
                        "id": "",
                    }
                }
            },
            {"Text": "inline"},
            {"End": "Link"},
            {"End": "Paragraph"},
            {"Start": "Paragraph"},
            {
                "Start": {
                    "Link": {
                        "link_type": "Reference",
                        "dest_url": "/url",
                        "title": "title",
                        "id": "lbl",
                    }
                }
            },
            {"Text": "ref"},
            {"End": "Link"},
            {"End": "Paragraph"},
            {"Start": "Paragraph"},
            {
                "Start": {
                    "Link": {
                        "link_type": "Collapsed",
                        "dest_url": "/url",
                        "title": "title",
                        "id": "lbl",
                    }
                }
            },
            {"Text": "lbl"},
            {"End": "Link"},
            {"End": "Paragraph"},
            {"Start": "Paragraph"},
            {
                "Start": {
                    "Link": {
                        "link_type": "Shortcut",
                        "dest_url": "/url",
                        "title": "title",
                        "id": "lbl",
                    }
                }
            },
            {"Text": "lbl"},
            {"End": "Link"},
            {"End": "Paragraph"},
            {"Start": "Paragraph"},
            {
                "Start": {
                    "Link": {
                        "link_type": "Autolink",
                        "dest_url": "http://foo.bar/baz",
                        "title": "",
                        "id": "",
                    }
                }
            },
            {"Text": "http://foo.bar/baz"},
            {"End": "Link"},
            {"End": "Paragraph"},
            {"Start": "Paragraph"},
            {
                "Start": {
                    "Link": {
                        "link_type": "Email",
                        "dest_url": "john@example.org",
                        "title": "",
                        "id": "",
                    }
                }
            },
            {"Text": "john@example.org"},
            {"End": "Link"},
            {"End": "Paragraph"},
            {"Start": "Paragraph"},
            {
                "Start": {
                    "Image": {
                        "link_type": "Inline",
                        "dest_url": "/i",
                        "title": "it",
                        "id": "",
                    }
                }
            },
            {"Text": "img"},
            {"End": "Image"},
            {"End": "Paragraph"},
        ),
    ),
    "wikilinks": (
        "[[foo|bar]] and [[baz]]\n",
        (
            {"Start": "Paragraph"},
            {
                "Start": {
                    "Link": {
                        "link_type": {"WikiLink": {"has_pothole": True}},
                        "dest_url": "foo",
                        "title": "",
                        "id": "",
                    }
                }
            },
            {"Text": "bar"},
            {"End": "Link"},
            {"Text": " and "},
            {
                "Start": {
                    "Link": {
                        "link_type": {"WikiLink": {"has_pothole": False}},
                        "dest_url": "baz",
                        "title": "",
                        "id": "",
                    }
                }
            },
            {"Text": "baz"},
            {"End": "Link"},
            {"End": "Paragraph"},
        ),
    ),
}


CODE_BLOCKS = """```python
x = 1
```

    indented

```unknown-language
y = 2
```"""


NON_ASCII_DOC = "é日本\U0001f600 text\n\n" + "[foo]: /url"
