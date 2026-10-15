# Command-line interface

```bash
pyromark README.md --enable-gfm --highlight inspired-github -o out.html
```

Pass `-` instead of a file to read from stdin. Without `-o`, the HTML goes to stdout. Input and output are always UTF-8.

`python -m pyromark` works too. Run `pyromark --help` for every flag; see [Options](api.md#pyromark.Options) and [Theme](api.md#pyromark.Theme) for what they do.
