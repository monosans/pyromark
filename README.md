# pyromark

[![Downloads](https://static.pepy.tech/badge/pyromark)](https://pepy.tech/project/pyromark)

pyromark (stands for Python Rust Optimized Markdown) is a blazingly fast CommonMark-compliant Markdown parser for Python, built on the [pulldown-cmark](https://github.com/pulldown-cmark/pulldown-cmark) Rust crate.

## Installation

```bash
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

160x faster than [markdown2](https://pypi.org/project/markdown2/),
130x faster than [Markdown](https://pypi.org/project/Markdown/),
119x faster than [mistletoe](https://pypi.org/project/mistletoe/),
103x faster than [markdown-it-py](https://pypi.org/project/markdown-it-py/),
75x faster than [mistune](https://pypi.org/project/mistune/).

`html` and `write_html` release the [GIL](https://docs.python.org/3/glossary.html#term-global-interpreter-lock), so threads render in parallel.

See [benchmark](https://monosans.github.io/pyromark/performance/).

## License

[MIT](https://github.com/monosans/pyromark/blob/main/LICENSE)
