# Guide

## Render HTML

```python
import pyromark

html = pyromark.html("# Hello *world*")
assert html == "<h1>Hello <em>world</em></h1>\n"
```

For big documents, [`write_html`][pyromark.write_html] streams the HTML into a binary file instead of building one string:

```python
import pyromark

with open("out.html", "wb") as file:
    pyromark.write_html("# Hello world", file)
```

## Enable extensions

Everything beyond CommonMark is off by default. Combine [`Options`][pyromark.Options] flags with `|`:

```python
import pyromark

html = pyromark.html(
    "| a | b |\n| - | - |\n| 1 | 2 |", options=pyromark.Options.ENABLE_TABLES
)
assert html.startswith("<table>")
```

| Flag                                      | Enables                                    |
| ----------------------------------------- | ------------------------------------------ |
| `ENABLE_TABLES`                           | pipe tables                                |
| `ENABLE_FOOTNOTES`                        | `[^1]` footnotes                           |
| `ENABLE_OLD_FOOTNOTES`                    | footnotes, older syntax                    |
| `ENABLE_STRIKETHROUGH`                    | `~~strikethrough~~`                        |
| `ENABLE_TASKLISTS`                        | `- [x] done`                               |
| `ENABLE_GFM`                              | GitHub alerts, `> [!NOTE]`                 |
| `ENABLE_MATH`                             | `$inline$` and `$$display$$` math          |
| `ENABLE_SMART_PUNCTUATION`                | curly quotes, `--` and `---` dashes, `...` |
| `ENABLE_HEADING_ATTRIBUTES`               | `# Title { #id .class }`                   |
| `ENABLE_DEFINITION_LIST`                  | `: definition` lists                       |
| `ENABLE_SUPERSCRIPT`                      | `^superscript^`                            |
| `ENABLE_SUBSCRIPT`                        | `~subscript~`                              |
| `ENABLE_WIKILINKS`                        | `[[wikilinks]]`                            |
| `ENABLE_YAML_STYLE_METADATA_BLOCKS`       | `---` front matter                         |
| `ENABLE_PLUSES_DELIMITED_METADATA_BLOCKS` | `+++` front matter                         |

To render like GitHub:

```python
import pyromark

GITHUB = (
    pyromark.Options.ENABLE_TABLES
    | pyromark.Options.ENABLE_FOOTNOTES
    | pyromark.Options.ENABLE_STRIKETHROUGH
    | pyromark.Options.ENABLE_TASKLISTS
    | pyromark.Options.ENABLE_GFM
)
html = pyromark.html("- [x] ~~done~~", options=GITHUB)
```

## Highlight code

Pick a bundled [`Theme`][pyromark.Theme]. It emits inline styles, so no CSS is needed:

````python
import pyromark

html = pyromark.html(
    "```python\nprint('hi')\n```", highlight=pyromark.Theme.INSPIRED_GITHUB
)
assert html.startswith('<pre style="background-color:#ffffff;">')
````

Or pass a [function][pyromark.event.HighlightCallback] that gets the language and the code and returns HTML, or `None` to leave the block as is. Here with [Pygments](https://pygments.org), installed with `uv add pygments`:

````python
import pyromark
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound


def pygmentize(language: str | None, code: str) -> str | None:
    try:
        lexer = get_lexer_by_name(language or "")
    except ClassNotFound:
        return None
    return highlight(code, lexer, HtmlFormatter())


html = pyromark.html("```python\nprint('hi')\n```", highlight=pygmentize)
assert html.startswith('<div class="highlight">')
css = HtmlFormatter().get_style_defs(".highlight")
````

## Resolve unknown links

[`broken_link_callback`][pyromark.event.BrokenLinkCallback] turns `[label]` references that have no definition into links. Return `(url, title)`, or `None` to keep the text:

```python
import pyromark

html = pyromark.html(
    "See [Python].",
    broken_link_callback=lambda link: (f"/wiki/{link['reference']}", ""),
)
assert html == '<p>See <a href="/wiki/Python">Python</a>.</p>\n'
```

[`reference_definitions`][pyromark.reference_definitions] returns the definitions a document does have:

```python
import pyromark

definitions = pyromark.reference_definitions("[home]: https://example.com")
assert definitions["home"]["dest"] == "https://example.com"
```

## Reuse settings

[`Markdown`][pyromark.Markdown] keeps options and callbacks, so you pass them once:

```python
import pyromark

md = pyromark.Markdown(
    options=pyromark.Options.ENABLE_TABLES,
    highlight=pyromark.Theme.SOLARIZED_DARK,
)
first = md.html("# One")
second = md.html("# Two")
```

## Render in parallel

[`html`][pyromark.html] and [`write_html`][pyromark.write_html] release the GIL, so threads render in parallel. A `Markdown` can be shared between them:

```python
from concurrent.futures import ThreadPoolExecutor

import pyromark

md = pyromark.Markdown(options=pyromark.Options.ENABLE_TABLES)
documents = ["# One", "# Two", "# Three"]
with ThreadPoolExecutor() as pool:
    pages = list(pool.map(md.html, documents))
```

The GIL is held while your callbacks run. Event iterators hold it on every step and can't be shared between threads.
