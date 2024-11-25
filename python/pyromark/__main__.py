# ruff: noqa: T201
from __future__ import annotations

import argparse
import sys
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from typing import Optional

import pyromark


@contextmanager
def _parse_args(
    args: Optional[Sequence[str]], /
) -> Iterator[argparse.Namespace]:
    parser = argparse.ArgumentParser(
        pyromark.__name__, description=pyromark.__doc__
    )
    parser.add_argument(
        "-v", "--version", action="version", version=pyromark.__version__
    )
    parser.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w", encoding="utf-8"),
        help="output file path, default is stdout",
    )
    for opt_name in pyromark.Options.__members__:
        parser.add_argument(
            "--" + opt_name.lower().replace("_", "-"), action="store_true"
        )
    parser.add_argument(
        "file",
        type=argparse.FileType("r", encoding="utf-8"),
        help="utf-8 input file path or '-' for stdin",
    )
    parsed_args = parser.parse_args(args)
    try:
        yield parsed_args
    finally:
        parsed_args.file.close()
        if parsed_args.output is not None:
            parsed_args.output.close()


def _main(args: Optional[Sequence[str]] = None, /) -> None:
    with _parse_args(args) as parsed_args:
        content = parsed_args.file.read()
        parsed_args.file.close()

        opts = pyromark.Options(0)
        for opt_name, opt in pyromark.Options.__members__.items():
            if getattr(parsed_args, opt_name.lower()):
                opts |= opt

        html = pyromark.html(content, options=opts)
        if parsed_args.output is None:
            print(html, end="")
        else:
            parsed_args.output.write(html)
            parsed_args.output.close()


if __name__ == "__main__":
    try:
        _main()
    except KeyboardInterrupt:
        sys.exit(130)
