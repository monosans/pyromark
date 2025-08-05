# ruff: noqa: T201
from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import Optional

import pyromark


def _parse_args(args: Optional[Sequence[str]], /) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        pyromark.__name__, description=pyromark.__doc__
    )
    parser.add_argument(
        "-v", "--version", action="version", version=pyromark.__version__
    )
    parser.add_argument(
        "-o", "--output", help="output file path, default is stdout"
    )
    for opt_name in pyromark.Options.__members__:
        parser.add_argument(
            "--" + opt_name.lower().replace("_", "-"), action="store_true"
        )
    parser.add_argument("file", help="utf-8 input file path or '-' for stdin")
    return parser.parse_args(args)


def main(args: Optional[Sequence[str]] = None, /) -> None:
    parsed_args = _parse_args(args)
    content = Path(parsed_args.file).read_text(encoding="utf-8")

    opts = pyromark.Options(0)
    for opt_name, opt in pyromark.Options.__members__.items():
        if getattr(parsed_args, opt_name.lower()):
            opts |= opt

    html = pyromark.html(content, options=opts)
    if parsed_args.output is None:
        print(html, end="")
    else:
        Path(parsed_args.output).write_text(html, encoding="utf-8")
