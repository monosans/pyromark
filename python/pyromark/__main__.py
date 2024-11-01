# ruff: noqa: T201
from __future__ import annotations

import argparse
from collections.abc import Sequence
from typing import Optional

import pyromark


def _parse_args(args: Optional[Sequence[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        pyromark.__name__, description=pyromark.__doc__
    )
    parser.add_argument(
        "-v", "--version", action="version", version=pyromark.__version__
    )
    for opt_name in pyromark.Options.__members__:
        parser.add_argument(
            "--" + opt_name.lower().replace("_", "-"), action="store_true"
        )
    parser.add_argument(
        "file",
        type=argparse.FileType(),
        help="input file path or '-' for stdin",
    )
    return parser.parse_args(args=args)


def _main(args: Optional[Sequence[str]] = None) -> None:
    parsed_args = _parse_args(args=args)

    with parsed_args.file as f:
        content = f.read()

    opts = pyromark.Options(0)
    for opt_name, opt in pyromark.Options.__members__.items():
        opt_enabled = getattr(parsed_args, opt_name.lower())
        if opt_enabled:
            opts |= opt

    html = pyromark.html(content, options=opts)
    print(html, end="")


if __name__ == "__main__":
    _main()
