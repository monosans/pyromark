# <img src="https://raw.githubusercontent.com/monosans/pyromark/main/docs/assets/logo.svg" alt="" width="40" align="top"> pyromark

[![Downloads](https://static.pepy.tech/badge/pyromark)](https://pepy.tech/project/pyromark)

pyromark (stands for Python Rust Optimized Markdown) is a blazingly fast CommonMark-compliant Markdown parser for Python, built on the [pulldown-cmark](https://github.com/pulldown-cmark/pulldown-cmark) Rust crate.

## Installation

```bash
uv add pyromark
# or
pip install -U pyromark
```

## Documentation

<https://monosans.github.io/pyromark>

## Examples

### Convert Markdown to HTML

```python
import pyromark

html = pyromark.html("# Hello world")
assert html == "<h1>Hello world</h1>\n"
```

The output is not sanitized, so sanitize it before serving Markdown you did not write.

### Iterate over Markdown elements

```python
import pyromark

for event in pyromark.events("# Hello world"):
    match event:
        case {"Start": {"Heading": {"level": heading_level}}}:
            print(f"Heading with {heading_level} level started")
        case {"Text": text}:
            print(f"Got {text!r} text")
        case {"End": {"Heading": heading_level}}:
            print(f"Heading with {heading_level} level ended")
        case other_event:
            print(f"Got {other_event!r}")
```

Events are fully type annotated, so your editor knows the shape of each one.

### Enable extensions and highlight code

```python
import pyromark

html = pyromark.html(
    "| a | b |\n| - | - |\n| 1 | 2 |",
    options=pyromark.Options.ENABLE_TABLES,
    highlight=pyromark.Theme.INSPIRED_GITHUB,
)
```

### Command line

```bash
pyromark README.md --enable-tables --highlight inspired-github -o out.html
```

## Performance

2.6x faster than [cmarkgfm](https://pypi.org/project/cmarkgfm/) (C) and [comrak](https://pypi.org/project/comrak/) (Rust).
86x to 367x faster than pure Python parsers:
[mistune](https://pypi.org/project/mistune/),
[markdown-it-py](https://pypi.org/project/markdown-it-py/),
[Markdown](https://pypi.org/project/Markdown/),
[mistletoe](https://pypi.org/project/mistletoe/),
[markdown2](https://pypi.org/project/markdown2/) and
[marko](https://pypi.org/project/marko/).

`html` and `write_html` release the [GIL](https://docs.python.org/3/glossary.html#term-global-interpreter-lock), so threads render in parallel.

See [benchmark](https://monosans.github.io/pyromark/performance/).

## License

[MIT](https://github.com/monosans/pyromark/blob/main/LICENSE)
