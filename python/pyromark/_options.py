from __future__ import annotations

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
    """<https://docs.rs/pulldown-cmark/0.12.2/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_FOOTNOTES>"""
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
    """<https://docs.rs/pulldown-cmark/0.12.2/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_HEADING_ATTRIBUTES>"""
    ENABLE_YAML_STYLE_METADATA_BLOCKS = 1 << 7
    """<https://docs.rs/pulldown-cmark/0.12.2/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_YAML_STYLE_METADATA_BLOCKS>"""
    ENABLE_PLUSES_DELIMITED_METADATA_BLOCKS = 1 << 8
    """<https://docs.rs/pulldown-cmark/0.12.2/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_PLUSES_DELIMITED_METADATA_BLOCKS>"""
    ENABLE_OLD_FOOTNOTES = (1 << 9) | (1 << 2)
    """<https://docs.rs/pulldown-cmark/0.12.2/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_OLD_FOOTNOTES>"""
    ENABLE_MATH = 1 << 10
    """<https://docs.rs/pulldown-cmark/0.12.2/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_MATH>"""
    ENABLE_GFM = 1 << 11
    """<https://docs.rs/pulldown-cmark/0.12.2/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_GFM>"""
    ENABLE_DEFINITION_LIST = 1 << 12
    """<https://docs.rs/pulldown-cmark/0.12.2/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_DEFINITION_LIST>"""
