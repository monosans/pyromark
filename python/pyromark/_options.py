from __future__ import annotations

import sys
from enum import IntFlag


class Options(IntFlag):
    """IntFlag containing flags for enabling pulldown_cmark options.

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
    """<https://github.github.com/gfm/#tables-extension->"""
    ENABLE_FOOTNOTES = 1 << 2
    """<https://docs.rs/pulldown-cmark/0.13.0/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_FOOTNOTES>"""
    ENABLE_STRIKETHROUGH = 1 << 3
    """<https://github.github.com/gfm/#strikethrough-extension->"""
    ENABLE_TASKLISTS = 1 << 4
    """<https://github.github.com/gfm/#task-list-items-extension->"""
    ENABLE_SMART_PUNCTUATION = 1 << 5
    """<https://docs.rs/pulldown-cmark/0.13.0/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_SMART_PUNCTUATION>"""
    ENABLE_HEADING_ATTRIBUTES = 1 << 6
    """<https://docs.rs/pulldown-cmark/0.13.0/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_HEADING_ATTRIBUTES>"""
    ENABLE_YAML_STYLE_METADATA_BLOCKS = 1 << 7
    """<https://docs.rs/pulldown-cmark/0.13.0/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_YAML_STYLE_METADATA_BLOCKS>"""
    ENABLE_PLUSES_DELIMITED_METADATA_BLOCKS = 1 << 8
    """<https://docs.rs/pulldown-cmark/0.13.0/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_PLUSES_DELIMITED_METADATA_BLOCKS>"""
    ENABLE_OLD_FOOTNOTES = (1 << 9) | (1 << 2)
    """<https://docs.rs/pulldown-cmark/0.13.0/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_OLD_FOOTNOTES>"""
    ENABLE_MATH = 1 << 10
    """<https://docs.rs/pulldown-cmark/0.13.0/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_MATH>"""
    ENABLE_GFM = 1 << 11
    """<https://docs.rs/pulldown-cmark/0.13.0/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_GFM>"""
    ENABLE_DEFINITION_LIST = 1 << 12
    """<https://docs.rs/pulldown-cmark/0.13.0/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_DEFINITION_LIST>"""
    ENABLE_SUPERSCRIPT = 1 << 13
    """<https://docs.rs/pulldown-cmark/0.13.0/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_SUPERSCRIPT>"""
    ENABLE_SUBSCRIPT = 1 << 14
    """<https://docs.rs/pulldown-cmark/0.13.0/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_SUBSCRIPT>"""
    ENABLE_WIKILINKS = 1 << 15
    """<https://docs.rs/pulldown-cmark/0.13.0/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_WIKILINKS>"""

    if sys.version_info < (3, 11):
        __str__ = int.__repr__
        __format__ = int.__format__  # type: ignore[assignment]
