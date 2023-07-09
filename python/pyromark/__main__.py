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
    for extension in pyromark.Extensions:
        name = extension._name_.lower().replace(  # type: ignore[union-attr]
            "_", "-"
        )
        parser.add_argument(f"--{name}", action="store_true")
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

    extensions = pyromark.Extensions(0)
    for extension in pyromark.Extensions:
        if getattr(
            parsed_args, extension._name_.lower()  # type: ignore[union-attr]
        ):
            extensions |= extension

    html = pyromark.markdown(content, extensions=extensions)
    print(html, end="")


if __name__ == "__main__":
    main()
