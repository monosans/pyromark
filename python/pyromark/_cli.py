from __future__ import annotations

import argparse
import errno
import os
import sys
from collections.abc import Sequence
from pathlib import Path

import pyromark

_THEMES = {
    name.lower().replace("_", "-"): theme
    for name, theme in pyromark.Theme.__members__.items()
}


def _parse_args(args: Sequence[str] | None, /) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        pyromark.__name__, description=pyromark.__doc__
    )
    parser.add_argument(
        "-v", "--version", action="version", version=pyromark.__version__
    )
    parser.add_argument(
        "-o", "--output", help="output file path, default is stdout"
    )
    parser.add_argument(
        "--highlight",
        choices=_THEMES,
        metavar="THEME",
        help="highlight code blocks with THEME: %(choices)s",
    )
    extensions = parser.add_argument_group(
        "markdown extensions",
        "off by default; see "
        "https://monosans.github.io/pyromark/guide/#enable-extensions",
    )
    for opt_name in pyromark.Options.__members__:
        extensions.add_argument(
            "--" + opt_name.lower().replace("_", "-"), action="store_true"
        )
    parser.add_argument("file", help="utf-8 input file path or '-' for stdin")
    return parser.parse_args(args)


def _read(file: str, /) -> str:
    data = sys.stdin.buffer.read() if file == "-" else Path(file).read_bytes()
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        msg = f"{file}: {exc}"
        raise ValueError(msg) from exc


def _render(parsed_args: argparse.Namespace, /) -> None:
    content = _read(parsed_args.file)
    options = pyromark.Options(0)
    for opt_name, opt in pyromark.Options.__members__.items():
        if getattr(parsed_args, opt_name.lower()):
            options |= opt
    highlight = _THEMES.get(parsed_args.highlight)

    if parsed_args.output is not None:
        with Path(parsed_args.output).open("wb") as file:
            pyromark.write_html(
                content, file, options=options, highlight=highlight
            )
        return
    try:
        pyromark.write_html(
            content, sys.stdout.buffer, options=options, highlight=highlight
        )
        sys.stdout.buffer.flush()
    except OSError as exc:
        # Windows reports a reader that quit before reading as EINVAL.
        if sys.platform == "win32" and exc.errno == errno.EINVAL:
            raise BrokenPipeError from exc
        raise


def _discard_stdout() -> None:
    try:
        fileno = sys.stdout.fileno()
    except (AttributeError, OSError, ValueError):
        return
    devnull = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(devnull, fileno)
    finally:
        os.close(devnull)


def main(args: Sequence[str] | None = None, /) -> None:
    parsed_args = _parse_args(args)
    try:
        _render(parsed_args)
    except BrokenPipeError:
        _discard_stdout()
        sys.exit(1)
    except (OSError, ValueError) as exc:
        _discard_stdout()
        sys.exit(f"{pyromark.__name__}: {exc}")
