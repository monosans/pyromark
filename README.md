# PyroMark

[![CI](https://github.com/monosans/pyromark/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/monosans/pyromark/actions/workflows/ci.yml?query=event%3Apush+branch%3Amain)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/monosans/pyromark/main.svg)](https://results.pre-commit.ci/latest/github/monosans/pyromark/main)
[![PyPI Downloads](https://img.shields.io/pypi/dm/pyromark?logo=pypi)](https://pypi.org/project/pyromark/)

PyroMark (stands for Python Rust Optimized Markdown) is a blazingly fast Markdown parser for Python.

Uses [pulldown-cmark](https://github.com/raphlinus/pulldown-cmark) Rust crate under the hood.

## Installation

```bash
python -m pip install pyromark
```

## Usage

### pyromark.markdown

```python
import pyromark

html = pyromark.markdown(
    "# Hello world",
    # Optional, include the ones you want
    extensions=(
        "tables",
        "footnotes",
        "strikethrough",
        "tasklists",
        "smart_punctuation",
        "heading_attributes",
    ),
)
print(html)  # <h1>Hello world</h1>\n
```

### pyromark.Markdown

```python
import pyromark

md = pyromark.Markdown(
    # Optional, include the ones you want
    extensions=(
        "tables",
        "footnotes",
        "strikethrough",
        "tasklists",
        "smart_punctuation",
        "heading_attributes",
    )
)
html = md.convert("# Hello world")
print(html)  # <h1>Hello world</h1>\n
```

### Extensions

You can see examples of how each extension affects the result in the [tests](https://github.com/monosans/pyromark/tree/main/tests).

- [tables](https://github.github.com/gfm/#tables-extension-)
- [footnotes](https://www.markdownguide.org/extended-syntax/#footnotes)
- [strikethrough](https://github.github.com/gfm/#strikethrough-extension-)
- [tasklists](https://github.github.com/gfm/#task-list-items-extension-)
- `smart_punctuation` converts some characters to their HTML equivalents:
  | Character | Replacements |
  | ------------ | ------------ |
  | ' | ‘ ’ |
  | " | “ ” |
  | ... | … |
  | -- | – |
  | --- | — |
- [heading_attributes](https://docs.rs/pulldown-cmark/latest/pulldown_cmark/struct.Options.html#associatedconstant.ENABLE_HEADING_ATTRIBUTES)

## Performance

125x faster than [Markdown](https://pypi.org/project/Markdown/),
109x faster than [markdown-it-py](https://pypi.org/project/markdown-it-py/),
86x faster than [mistune](https://pypi.org/project/mistune/).

```python
Python 3.11.3 (main, Apr  5 2023, 15:52:25) [GCC 12.2.1 20230201]
Type 'copyright', 'credits' or 'license' for more information
IPython 8.13.2 -- An enhanced Interactive Python. Type '?' for help.

In [1]: import requests, markdown, markdown_it, mistune, pyromark

In [2]: markdown.__version__, markdown_it.__version__, mistune.__version__
Out[2]: ('3.4.3', '2.2.0', '2.0.5')

In [3]: text = requests.get(
   ...:     "https://raw.githubusercontent.com/rust-lang/rust/1.69.0/README.md"
   ...: ).text

In [4]: %timeit markdown.markdown(text)
7.51 ms ± 22 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

In [5]: %timeit markdown_it.MarkdownIt().render(text)
6.5 ms ± 42.8 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

In [6]: %timeit mistune.html(text)
5.16 ms ± 40.1 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

In [7]: %timeit pyromark.markdown(text)
59.9 µs ± 202 ns per loop (mean ± std. dev. of 7 runs, 10,000 loops each)
```

## License

[MIT](LICENSE)
