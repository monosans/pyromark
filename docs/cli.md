# Command-line interface

```bash
pyromark --help
```

```bash
python -m pyromark --help
```

See [Options](api.md#pyromark.Options) for a description of the `--enable-*` options.

```
usage: pyromark [-h] [-v] [-o OUTPUT] [--enable-tables] [--enable-footnotes]
                [--enable-strikethrough] [--enable-tasklists]
                [--enable-smart-punctuation] [--enable-heading-attributes]
                [--enable-yaml-style-metadata-blocks]
                [--enable-pluses-delimited-metadata-blocks]
                [--enable-old-footnotes] [--enable-math] [--enable-gfm]
                [--enable-definition-list] [--enable-superscript]
                [--enable-subscript] [--enable-wikilinks]
                file

Blazingly fast Markdown parser.

positional arguments:
  file                  utf-8 input file path or '-' for stdin

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -o OUTPUT, --output OUTPUT
                        output file path, default is stdout
  --enable-tables
  --enable-footnotes
  --enable-strikethrough
  --enable-tasklists
  --enable-smart-punctuation
  --enable-heading-attributes
  --enable-yaml-style-metadata-blocks
  --enable-pluses-delimited-metadata-blocks
  --enable-old-footnotes
  --enable-math
  --enable-gfm
  --enable-definition-list
  --enable-superscript
  --enable-subscript
  --enable-wikilinks
```
