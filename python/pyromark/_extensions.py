from __future__ import annotations

from enum import IntFlag


class Extensions(IntFlag):
    """IntFlag containing flags for enabling Markdown extensions.

    Examples:
        All extensions:

        ```python
        extensions=(
            pyromark.Extensions.ENABLE_TABLES
            | pyromark.Extensions.ENABLE_FOOTNOTES
            | pyromark.Extensions.ENABLE_STRIKETHROUGH
            | pyromark.Extensions.ENABLE_TASKLISTS
            | pyromark.Extensions.ENABLE_SMART_PUNCTUATION
            | pyromark.Extensions.ENABLE_HEADING_ATTRIBUTES
        )
        ```
    """

    ENABLE_TABLES = 1 << 1
    """<https://github.github.com/gfm/#tables-extension->"""
    ENABLE_FOOTNOTES = 1 << 2
    """<https://www.markdownguide.org/extended-syntax/#footnotes>"""
    ENABLE_STRIKETHROUGH = 1 << 3
    """<https://github.github.com/gfm/#strikethrough-extension->"""
    ENABLE_TASKLISTS = 1 << 4
    """<https://github.github.com/gfm/#task-list-items-extension->"""
    ENABLE_SMART_PUNCTUATION = 1 << 5
    """Converts some characters to their HTML equivalents:

    | Character | Replacements |
    | --------- | ------------ |
    | '         | ‘ ’          |
    | "         | “ ”          |
    | ...       | …            |
    | --        | –            |
    | ---       | —            |
    """
    ENABLE_HEADING_ATTRIBUTES = 1 << 6
    """<https://docs.rs/pulldown-cmark/latest/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_HEADING_ATTRIBUTES>"""
