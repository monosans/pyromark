# Performance

123x faster than [Markdown](https://pypi.org/project/Markdown/),
101x faster than [markdown-it-py](https://pypi.org/project/markdown-it-py/),
76x faster than [mistune](https://pypi.org/project/mistune/).

If you use threading, the difference with other libraries will be even more enormous, since pyromark releases the [GIL](https://docs.python.org/3/glossary.html#term-global-interpreter-lock).

```python
Python 3.11.3 (main, Jun  5 2023, 09:32:32) [GCC 13.1.1 20230429]
Type 'copyright', 'credits' or 'license' for more information
IPython 8.14.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: import requests, markdown, markdown_it, mistune, pyromark

In [2]: markdown.__version__, markdown_it.__version__, mistune.__version__
Out[2]: ('3.4.3', '3.0.0', '3.0.1')

In [3]: text = requests.get(
   ...:     "https://raw.githubusercontent.com/rust-lang/rust/1.70.0/README.md"
   ...: ).text

In [4]: %timeit markdown.markdown(text)
7.41 ms ± 30.9 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

In [5]: %timeit markdown_it.MarkdownIt().render(text)
6.09 ms ± 31.2 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

In [6]: %timeit mistune.html(text)
4.56 ms ± 30.4 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

In [7]: %timeit pyromark.markdown(text)
61 µs ± 246 ns per loop (mean ± std. dev. of 7 runs, 10,000 loops each)
```
