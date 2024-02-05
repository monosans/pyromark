# ruff: noqa: T201
from __future__ import annotations

import argparse
from typing import Optional, Sequence

import pyromark


def parse_args(args: Optional[Sequence[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        pyromark.__name__, description=pyromark.__doc__
    )
    parser.add_argument(
        "-v", "--version", action="version", version=pyromark.__version__
    )
    for ext_name in pyromark.Extensions.__members__:
        parser.add_argument(
            "--" + ext_name.lower().replace("_", "-"), action="store_true"
        )
    parser.add_argument(
        "file",
        type=argparse.FileType(),
        help="input file path or '-' for stdin",
    )
    return parser.parse_args(args=args)


def main(args: Optional[Sequence[str]] = None) -> None:
    parsed_args = parse_args(args=args)

    with parsed_args.file as f:
        content = f.read()

    exts = pyromark.Extensions(0)
    for ext_name, ext in pyromark.Extensions.__members__.items():
        ext_enabled = getattr(parsed_args, ext_name.lower())
        if ext_enabled:
            exts |= ext

    html = pyromark.markdown(content, extensions=exts)
    print(html, end="")


if __name__ == "__main__":
    main()
