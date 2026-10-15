# pyromark

A CommonMark-compliant Markdown parser for Python, built on the [pulldown-cmark](https://github.com/pulldown-cmark/pulldown-cmark) Rust crate.

- 75 to 160 times faster than pure Python parsers ([benchmark](performance.md)).
- Supports tables, footnotes, task lists, math, GitHub alerts and [other extensions](guide.md#enable-extensions).
- Highlights code in about 190 languages with bundled themes, so you don't need Pygments.
- Every event is typed, so your editor knows its shape.
- Releases the GIL while rendering, so threads render in parallel.

## Install

=== "uv"

    ```bash
    uv add pyromark
    ```

=== "pip"

    ```bash
    pip install -U pyromark
    ```

Python 3.11+ on Linux, macOS and Windows, including PyPy and free-threaded builds.

## Quick start

```python
import pyromark

html = pyromark.html("# Hello *world*")
assert html == "<h1>Hello <em>world</em></h1>\n"
```

!!! warning "The output is not sanitized"

    Raw HTML and `javascript:` links pass through, as CommonMark requires. Clean the output of Markdown you did not write, for example with [nh3](https://pypi.org/project/nh3/).

## Next

- [Guide](guide.md): extensions, code highlighting, links, threads.
- [Events](events.md): walk the document to build a table of contents, collect links or extract text.
- [CLI](cli.md): convert files from the terminal.
- [API reference](api.md): every function, class and type.
