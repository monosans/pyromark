# pyromark

[![CI](https://github.com/monosans/pyromark/actions/workflows/ci.yml/badge.svg)](https://github.com/monosans/pyromark/actions/workflows/ci.yml)
[![Downloads](https://static.pepy.tech/badge/pyromark)](https://pepy.tech/project/pyromark)

pyromark (stands for Python Rust Optimized Markdown) is a blazingly fast CommonMark-compliant Markdown parser for Python.

Uses [pulldown-cmark](https://github.com/raphlinus/pulldown-cmark) Rust crate under the hood.

## Installation

```bash
pip install -U pyromark
```

## Documentation

<https://pyromark.readthedocs.io>

### Basic examples

See documentation for more comprehensive examples.

#### Convert Markdown to HTML

```python
import pyromark

html = pyromark.html("# Hello world")
assert html == "<h1>Hello world</h1>\n"
```

#### Iterating over Markdown elements

```python
import pyromark

for event in pyromark.events("# Hello world"):
    # All event types are fully type annotated
    # so you will get static type checking
    # and Tab completions in your IDE!
    match event:
        case ("Start", ("Heading", {"level": heading_level})):
            print(f"Heading with {heading_level} level started")
        case ("Text", text):
            print(f"Got {text!r} text")
        case ("End", ("Heading", heading_level)):
            print(f"Heading with {heading_level} level ended")
        case other_event:
            print(f"Got {other_event!r}")
```

## Performance

130x faster than [Markdown](https://pypi.org/project/Markdown/),
101x faster than [markdown-it-py](https://pypi.org/project/markdown-it-py/),
71x faster than [mistune](https://pypi.org/project/mistune/),
8x faster than [markdown-it-pyrs](https://pypi.org/project/markdown-it-pyrs/).

If you use threading, the difference with other libraries will be even more enormous, since pyromark releases the [GIL](https://docs.python.org/3/glossary.html#term-global-interpreter-lock).

See [benchmark](https://pyromark.readthedocs.io/en/latest/performance/).

## License

[MIT](https://github.com/monosans/pyromark/blob/main/LICENSE)
