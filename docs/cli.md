# CLI

Convert a file without writing any Python:

=== "uv"

    ```bash
    uvx pyromark README.md --enable-gfm --highlight inspired-github -o out.html
    ```

=== "pip"

    ```bash
    pip install -U pyromark
    pyromark README.md --enable-gfm --highlight inspired-github -o out.html
    ```

- `-` instead of a file reads stdin; without `-o` the HTML goes to stdout.
- Input and output are always UTF-8.
- `python -m pyromark` works too.

Each [`Options`](api.md#pyromark.Options) flag has a matching `--enable-*` switch, and `--highlight` takes a [`Theme`](api.md#pyromark.Theme) in kebab case. `pyromark --help` lists them all.
