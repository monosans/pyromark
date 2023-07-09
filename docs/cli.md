# Command-line interface

See [Extensions](../api/#pyromark.Extensions-attributes) for a description of the `--enable-*` options.

```bash
$ python -m pyromark --help
usage: pyromark [-h] [-v] [--enable-tables] [--enable-footnotes] [--enable-strikethrough] [--enable-tasklists] [--enable-smart-punctuation] [--enable-heading-attributes] file

Blazingly fast Markdown parser.

positional arguments:
  file                  input file path or '-' for stdin

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --enable-tables
  --enable-footnotes
  --enable-strikethrough
  --enable-tasklists
  --enable-smart-punctuation
  --enable-heading-attributes
```
