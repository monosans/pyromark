# Performance

Time to render [Rust's INSTALL.md](https://raw.githubusercontent.com/rust-lang/rust/refs/tags/1.82.0/INSTALL.md) to HTML 1000 times, on Python 3.14 and an AMD Ryzen 9 9900X:

| Library        | Version    | Written in | Seconds | Times slower than pyromark |
| -------------- | ---------- | ---------- | ------- | -------------------------- |
| marko          | 2.2.4      | Python     | 12.675  | 367                        |
| markdown2      | 2.5.5      | Python     | 6.050   | 175                        |
| mistletoe      | 1.6.0      | Python     | 3.928   | 114                        |
| markdown       | 3.11.1     | Python     | 3.925   | 114                        |
| markdown-it-py | 4.2.0      | Python     | 3.356   | 99                         |
| mistune        | 3.3.4      | Python     | 2.951   | 86                         |
| cmarkgfm       | 2025.10.22 | C          | 0.090   | 2.6                        |
| comrak         | 0.0.16     | Rust       | 0.088   | 2.6                        |
| pyromark       | 0.10.0     | Rust       | 0.034   | 1                          |

Each library ran once per round, in random order, for 30 rounds. The table shows medians, and each ratio is taken within a round, so load from other programs affects both sides alike. markdown-it-pyrs is left out: it has no wheels for Python 3.13 and newer, and a build from source crashes on 3.14.

```python
# pip install cmarkgfm comrak markdown markdown2 markdown-it-py marko mistletoe mistune pyromark requests
import random
import statistics
from importlib.metadata import version
from timeit import timeit

import cmarkgfm
import comrak
import markdown
import markdown2
import markdown_it
import marko
import mistletoe
import mistune
import pyromark
import requests

text = requests.get(
    "https://raw.githubusercontent.com/rust-lang/rust/refs/tags/1.82.0/INSTALL.md"
).text

renderers = {
    "marko": lambda: marko.convert(text),
    "markdown2": lambda: markdown2.markdown(text),
    "mistletoe": lambda: mistletoe.markdown(text),
    "markdown": lambda: markdown.markdown(text),
    "markdown-it-py": lambda: markdown_it.MarkdownIt().render(text),
    "mistune": lambda: mistune.html(text),
    "cmarkgfm": lambda: cmarkgfm.markdown_to_html(text),
    "comrak": lambda: comrak.render_markdown(text),
    "pyromark": lambda: pyromark.html(text),
}
times = {name: [] for name in renderers}
for _ in range(30):
    for name in random.sample(list(renderers), len(renderers)):
        times[name].append(timeit(renderers[name], number=1000))

for name, seconds in times.items():
    ratio = statistics.median(
        t / p for t, p in zip(seconds, times["pyromark"], strict=True)
    )
    print(
        f"| {name} | {version(name)} | {statistics.median(seconds):.3f} | {ratio:.1f} |"
    )
```
