# Performance

128x faster than [Markdown](https://pypi.org/project/Markdown/),
105x faster than [markdown-it-py](https://pypi.org/project/markdown-it-py/),
79x faster than [mistune](https://pypi.org/project/mistune/),
8x faster than [markdown-it-pyrs](https://pypi.org/project/markdown-it-pyrs/).

If you use threading, the difference with other libraries will be even more enormous, since pyromark releases the [GIL](https://docs.python.org/3/glossary.html#term-global-interpreter-lock).

```python
Python 3.12.7 (main, Oct  1 2024, 11:15:50) [GCC 14.2.1 20240910]
Type 'copyright', 'credits' or 'license' for more information
IPython 8.18.1 -- An enhanced Interactive Python. Type '?' for help.

In [1]: import requests, markdown, markdown_it, mistune, markdown_it_pyrs, pyromark

In [2]: (
   ...:     markdown.__version__,
   ...:     markdown_it.__version__,
   ...:     mistune.__version__,
   ...:     markdown_it_pyrs.__version__,
   ...: )
Out[2]: ('3.7', '3.0.0', '3.0.2', '0.4.0')

In [3]: text = requests.get(
   ...:     "https://raw.githubusercontent.com/rust-lang/rust/refs/tags/1.82.0/INSTALL.md"
   ...: ).text

In [4]: %timeit markdown.markdown(text)
3.12 ms ± 10.3 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

In [5]: %timeit markdown_it.MarkdownIt().render(text)
2.42 ms ± 13.5 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

In [6]: %timeit mistune.html(text)
1.7 ms ± 3.41 µs per loop (mean ± std. dev. of 7 runs, 1,000 loops each)

In [7]: %timeit markdown_it_pyrs.MarkdownIt().render(text)
180 µs ± 135 ns per loop (mean ± std. dev. of 7 runs, 10,000 loops each)

In [8]: %timeit pyromark.html(text)
24.1 µs ± 41 ns per loop (mean ± std. dev. of 7 runs, 10,000 loops each)
```
