# Performance

| Library     | Version | Seconds | n times slower than pyromark |
| ----------- | ------- | ------- | ---------------------------- |
| markdown2   | 2.5.3   | 4.005   | 160                          |
| markdown    | 3.7     | 3.245   | 130                          |
| mistletoe   | 1.4.0   | 2.980   | 119                          |
| markdown_it | 3.0.0   | 2.583   | 103                          |
| mistune     | 3.1.1   | 1.885   | 75                           |
| pyromark    | 0.9.0   | 0.025   | 1                            |

```python
# pip install markdown markdown2 markdown-it-py mistletoe mistune pyromark requests
from operator import itemgetter
from timeit import timeit

import markdown
import markdown2
import markdown_it
import mistletoe
import mistune
import pyromark
import requests

text = requests.get(
    "https://raw.githubusercontent.com/rust-lang/rust/refs/tags/1.82.0/INSTALL.md"
).text

results = {
    library: timeit(renderer, number=1000)
    for library, renderer in (
        (markdown_it, lambda: markdown_it.MarkdownIt().render(text)),
        (markdown, lambda: markdown.markdown(text)),
        (mistune, lambda: mistune.html(text)),
        (markdown2, lambda: markdown2.markdown(text)),
        (mistletoe, lambda: mistletoe.markdown(text)),
        (pyromark, lambda: pyromark.html(text)),
    )
}

print("| Library | Version | Seconds | n times slower than pyromark |")
print("| ------- | ------- | ------- | ---------------------------- |")
for library, seconds in sorted(
    results.items(), key=itemgetter(1), reverse=True
):
    print(
        "|",
        library.__name__,
        "|",
        library.__version__,
        "|",
        format(seconds, ".3f"),
        "|",
        format(seconds / results[pyromark], ".0f"),
        "|",
    )
```
