from __future__ import annotations

from enum import IntFlag


class Options(IntFlag):
    """Markdown extensions to enable, combined with `|`. All are off by default.

    Passing bits pulldown-cmark does not define raises `ValueError`. See
    [pulldown-cmark](https://docs.rs/pulldown-cmark/0.13.4/pulldown_cmark/struct.Options.html)
    for the details of each extension.

    Examples:
        ```python
        options = (
            pyromark.Options.ENABLE_TABLES
            | pyromark.Options.ENABLE_MATH
            | pyromark.Options.ENABLE_GFM
        )
        ```
    """

    ENABLE_TABLES = 1 << 1
    """Pipe tables, as in GitHub Flavored Markdown."""
    ENABLE_FOOTNOTES = 1 << 2
    """Footnotes, referenced with `[^1]` and defined with `[^1]: text`."""
    ENABLE_STRIKETHROUGH = 1 << 3
    """`~~strikethrough~~`, as in GitHub Flavored Markdown."""
    ENABLE_TASKLISTS = 1 << 4
    """Task list items, `- [ ]` and `- [x]`."""
    ENABLE_SMART_PUNCTUATION = 1 << 5
    """Typographic replacements: `--` and `---` become dashes, `...` an
    ellipsis, and straight quotes become curly ones.
    """
    ENABLE_HEADING_ATTRIBUTES = 1 << 6
    """Headings carrying an id, classes and attributes, as in
    `# text { #id .class1 .class2 myattr other_attr=myvalue }`.
    """
    ENABLE_YAML_STYLE_METADATA_BLOCKS = 1 << 7
    """A metadata block opened by a `---` line and closed by `---` or `...`."""
    ENABLE_PLUSES_DELIMITED_METADATA_BLOCKS = 1 << 8
    """A metadata block delimited by `+++` lines."""
    ENABLE_OLD_FOOTNOTES = (1 << 9) | (1 << 2)
    """The older footnote syntax. Includes `ENABLE_FOOTNOTES`."""
    ENABLE_MATH = 1 << 10
    """`$inline$` and `$$display$$` formulas, emitted as `InlineMath` and
    `DisplayMath` events.
    """
    ENABLE_GFM = 1 << 11
    """GitHub alerts: `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`,
    `> [!WARNING]` and `> [!CAUTION]`.
    """
    ENABLE_DEFINITION_LIST = 1 << 12
    """Definition lists, a title followed by lines starting with `:`."""
    ENABLE_SUPERSCRIPT = 1 << 13
    """`^superscript^`."""
    ENABLE_SUBSCRIPT = 1 << 14
    """`~subscript~`."""
    ENABLE_WIKILINKS = 1 << 15
    """Obsidian-style `[[wikilinks]]`."""
