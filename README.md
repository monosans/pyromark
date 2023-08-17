# pyromark

[![CI](https://github.com/monosans/pyromark/actions/workflows/ci.yml/badge.svg)](https://github.com/monosans/pyromark/actions/workflows/ci.yml)
[![Downloads](https://static.pepy.tech/badge/pyromark)](https://pepy.tech/project/pyromark)

pyromark (stands for Python Rust Optimized Markdown) is a blazingly fast CommonMark-compliant Markdown parser for Python.

Uses [pulldown-cmark](https://github.com/raphlinus/pulldown-cmark) Rust crate under the hood.

## Installation

```bash
python -m pip install -U pyromark
```

## Documentation

<https://pyromark.readthedocs.io>

## Performance

128x faster than [Markdown](https://pypi.org/project/Markdown/),
105x faster than [markdown-it-py](https://pypi.org/project/markdown-it-py/),
79x faster than [mistune](https://pypi.org/project/mistune/),
8x faster than [markdown-it-pyrs](https://pypi.org/project/markdown-it-pyrs/).

If you use threading, the difference with other libraries will be even more enormous, since pyromark releases the [GIL](https://docs.python.org/3/glossary.html#term-global-interpreter-lock).

See [benchmark](https://pyromark.readthedocs.io/en/latest/performance/).

## License

[MIT](https://github.com/monosans/pyromark/blob/main/LICENSE)
