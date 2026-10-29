# ruff: noqa: E501
from __future__ import annotations

import errno
import io
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import IO

import pyromark
import pytest
from pyromark._cli import main as pyromark_cli  # noqa: PLC2701
from typing_extensions import Buffer, override


@pytest.mark.parametrize("flag", ["-o", "--output"])
def test_cli_output(
    flag: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    input_file = tmp_path / "input.md"
    input_file.write_text("# Hello world", encoding="utf-8")
    output_file = tmp_path / "output.html"

    pyromark_cli((flag, str(output_file), str(input_file)))

    capture = capsys.readouterr()
    assert not capture.out
    assert not capture.err
    assert output_file.read_text(encoding="utf-8") == "<h1>Hello world</h1>\n"


class _Stdin:
    """A stdin whose text layer is not UTF-8.

    Models a console on a legacy code page, which mangles a UTF-8 document
    instead of failing on it. Decoding is pinned rather than taken from the
    locale so that a caller reaching for the text layer is caught on a
    UTF-8 host too.
    """

    def __init__(self, buffer: IO[bytes]) -> None:
        self.buffer = buffer

    def read(self) -> str:
        return self.buffer.read().decode("latin-1")


def test_cli_stdin_is_utf8(
    monkeypatch: pytest.MonkeyPatch,
    capsysbinary: pytest.CaptureFixture[bytes],
    tmp_path: Path,
) -> None:
    markdown = "# 日本語 héllo"
    file = tmp_path / "stdin.md"
    file.write_bytes(markdown.encode())
    with file.open("rb") as stdin:
        monkeypatch.setattr(sys, "stdin", _Stdin(stdin))

        pyromark_cli(("-",))

    capture = capsysbinary.readouterr()
    assert not capture.err
    assert capture.out == pyromark.html(markdown).encode()
    assert capture.out == "<h1>日本語 héllo</h1>\n".encode()


def test_cli_reports_unusable_files_without_a_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "nope.md"
    not_utf8 = tmp_path / "bad.md"
    not_utf8.write_bytes(b"\xff\xfe")
    source = tmp_path / "in.md"
    source.write_text("# Hello world", encoding="utf-8")

    invocations = (
        (str(missing),),
        (str(not_utf8),),
        (str(source), "-o", str(tmp_path / "nosuchdir" / "out.html")),
    )
    for invocation in invocations:
        with pytest.raises(SystemExit) as exc:
            pyromark_cli(invocation)

        assert exc.value.code != 0
        assert str(exc.value).startswith("pyromark: ")
        assert not capsys.readouterr().out


@pytest.mark.parametrize(
    "markdown",
    [b"a <b\r\nclass='x'>y</b> z\r\n", b"```\r\rx\r\r```\r", b"# Hi\r\n"],
    ids=["crlf-inline-html", "lone-cr", "crlf-heading"],
)
def test_cli_reads_a_file_and_stdin_identically(
    markdown: bytes,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsysbinary: pytest.CaptureFixture[bytes],
) -> None:
    file = tmp_path / "in.md"
    file.write_bytes(markdown)

    pyromark_cli((str(file),))
    from_file = capsysbinary.readouterr().out

    with file.open("rb") as stdin:
        monkeypatch.setattr(sys, "stdin", _Stdin(stdin))
        pyromark_cli(("-",))
    from_stdin = capsysbinary.readouterr().out

    assert from_file == from_stdin == pyromark.html(markdown.decode()).encode()


README = Path(__file__).parent.parent / "README.md"

CLI_DOC = Path(__file__).parent.parent / "docs" / "cli.md"


def test_cli_stdout_is_utf8(
    capsysbinary: pytest.CaptureFixture[bytes], tmp_path: Path
) -> None:
    markdown = "# 日本語 héllo"
    file = tmp_path / "unicode.md"
    file.write_text(markdown, encoding="utf-8")

    pyromark_cli((str(file),))

    capture = capsysbinary.readouterr()
    assert not capture.err
    assert capture.out == pyromark.html(markdown).encode()
    assert capture.out == "<h1>日本語 héllo</h1>\n".encode()


class _Buffer(io.BytesIO):
    """A byte stream that records whether anyone flushed it."""

    flushes = 0

    @override
    def flush(self) -> None:
        self.flushes += 1


class _Stdout:
    """A stdout whose text layer cannot represent every document.

    Models a console that is not UTF-8, and holds written text until it is
    flushed, as the real text layer does.
    """

    def __init__(self) -> None:
        self.buffer = _Buffer()
        self._pending: list[str] = []

    def write(self, text: str, /) -> int:
        self._pending.append(text)
        return len(text)

    def flush(self) -> None:
        for text in self._pending:
            self.buffer.write(text.encode("latin-1", "replace"))
        self._pending.clear()


def test_cli_stdout_bypasses_a_non_utf8_text_layer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    markdown = "# 日本語 héllo"
    file = tmp_path / "unicode.md"
    file.write_text(markdown, encoding="utf-8")
    stdout = _Stdout()
    monkeypatch.setattr(sys, "stdout", stdout)

    pyromark_cli((str(file),))

    assert stdout.buffer.getvalue() == pyromark.html(markdown).encode()


def test_cli_stdout_flushes_what_it_wrote(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    file = tmp_path / "in.md"
    file.write_text("# Hello world", encoding="utf-8")
    stdout = _Stdout()
    monkeypatch.setattr(sys, "stdout", stdout)

    pyromark_cli((str(file),))

    assert stdout.buffer.flushes > 0


def test_cli_output_is_utf8(tmp_path: Path) -> None:
    markdown = "# 日本語 héllo"
    input_file = tmp_path / "unicode.md"
    input_file.write_text(markdown, encoding="utf-8")
    output_file = tmp_path / "out.html"

    pyromark_cli(("-o", str(output_file), str(input_file)))

    assert output_file.read_bytes() == pyromark.html(markdown).encode()


def test_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        pyromark_cli(("--version",))
    assert exc.value.code == 0
    capture = capsys.readouterr()
    assert not capture.err
    assert capture.out == f"{pyromark.__version__}\n"


_CLI_THEME_FLAGS = {
    name.lower().replace("_", "-"): theme
    for name, theme in pyromark.Theme.__members__.items()
}


@pytest.mark.parametrize(("flag", "theme"), _CLI_THEME_FLAGS.items())
def test_cli_highlight(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    flag: str,
    theme: pyromark.Theme,
) -> None:
    markdown = "~~~python\nx = 1\n~~~"
    file = tmp_path / "in.md"
    file.write_text(markdown, encoding="utf-8")
    stdout = _Stdout()
    monkeypatch.setattr(sys, "stdout", stdout)

    pyromark_cli(("--highlight", flag, str(file)))

    assert (
        stdout.buffer.getvalue()
        == pyromark.html(markdown, highlight=theme).encode()
    )


def test_cli_highlight_writes_to_the_output_file(tmp_path: Path) -> None:
    markdown = "~~~python\nx = 1\n~~~"
    input_file = tmp_path / "in.md"
    input_file.write_text(markdown, encoding="utf-8")
    output_file = tmp_path / "out.html"

    pyromark_cli((
        "--highlight",
        "solarized-dark",
        "-o",
        str(output_file),
        str(input_file),
    ))

    assert (
        output_file.read_bytes()
        == pyromark.html(
            markdown, highlight=pyromark.Theme.SOLARIZED_DARK
        ).encode()
    )


def test_cli_rejects_an_unknown_highlight_theme(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    file = tmp_path / "in.md"
    file.write_text("# Hello world", encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        pyromark_cli(("--highlight", "nonexistent", str(file)))

    assert exc.value.code != 0
    assert "invalid choice" in capsys.readouterr().err


def test_cli_help_keeps_urls_and_theme_names_whole(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("COLUMNS", "60")
    monkeypatch.setenv("PYTHON_COLORS", "0")

    with pytest.raises(SystemExit) as exc:
        pyromark_cli(("--help",))

    assert exc.value.code == 0
    words = {word.rstrip(",") for word in capsys.readouterr().out.split()}
    assert (
        "https://monosans.github.io/pyromark/guide/#enable-extensions" in words
    )
    assert words >= set(_CLI_THEME_FLAGS)


class _BrokenPipeBuffer(io.BytesIO):
    """A byte stream whose reader has gone away."""

    @override
    def write(self, buffer: Buffer, /) -> int:
        raise BrokenPipeError


class _BrokenPipeStdout:
    """A stdout whose reader has gone away, as when output is piped to head."""

    def __init__(self, fileno: int | None = None) -> None:
        self.buffer = _BrokenPipeBuffer()
        self._fileno = fileno

    def fileno(self) -> int:
        if self._fileno is None:
            raise io.UnsupportedOperation
        return self._fileno

    def flush(self) -> None: ...


def test_cli_exits_quietly_on_a_broken_pipe(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    file = tmp_path / "in.md"
    file.write_text("# Hello world", encoding="utf-8")
    monkeypatch.setattr(sys, "stdout", _BrokenPipeStdout())

    with pytest.raises(SystemExit) as exc:
        pyromark_cli((str(file),))

    assert exc.value.code == 1
    assert not capsys.readouterr().err


def test_cli_stops_writing_to_a_broken_pipe(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    file = tmp_path / "in.md"
    file.write_text("# Hello world", encoding="utf-8")
    sink = tmp_path / "sink"

    with sink.open("wb") as handle:
        monkeypatch.setattr(sys, "stdout", _BrokenPipeStdout(handle.fileno()))

        with pytest.raises(SystemExit):
            pyromark_cli((str(file),))

        os.write(handle.fileno(), b"discarded at interpreter shutdown")

    assert sink.read_bytes() == b""


BOM = b"\xef\xbb\xbf"


@pytest.mark.parametrize(
    "markdown",
    [b"# Hi\n\nText\n", b"", b"\n"],
    ids=["heading", "empty", "newline"],
)
def test_cli_strips_a_byte_order_mark(
    markdown: bytes, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    expected = pyromark.html(markdown.decode()).encode()
    plain = tmp_path / "plain.md"
    plain.write_bytes(markdown)
    bom = tmp_path / "bom.md"
    bom.write_bytes(BOM + markdown)

    outputs = []
    for path in (plain, bom):
        stdout = _Stdout()
        monkeypatch.setattr(sys, "stdout", stdout)
        pyromark_cli((str(path),))
        outputs.append(stdout.buffer.getvalue())

    monkeypatch.setattr(sys, "stdin", _Stdin(io.BytesIO(BOM + markdown)))
    stdout = _Stdout()
    monkeypatch.setattr(sys, "stdout", stdout)
    pyromark_cli(("-",))
    outputs.append(stdout.buffer.getvalue())

    assert outputs == [expected] * 3
    assert BOM not in expected


class _ClosedPipeBuffer(io.BytesIO):
    """A stdout whose reader quit before reading anything, as Windows reports it."""

    @override
    def write(self, buffer: Buffer, /) -> int:
        raise OSError(errno.EINVAL, "Invalid argument")


class _ClosedPipeStdout:
    def __init__(self) -> None:
        self.buffer = _ClosedPipeBuffer()

    def flush(self) -> None: ...


@pytest.mark.parametrize(
    ("platform", "quiet"),
    [("win32", True), ("linux", False), ("darwin", False)],
)
def test_cli_treats_einval_on_stdout_as_a_closed_pipe_only_on_windows(
    platform: str,
    quiet: bool,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    file = tmp_path / "in.md"
    file.write_text("# Hello world", encoding="utf-8")
    monkeypatch.setattr(sys, "platform", platform)
    monkeypatch.setattr(sys, "stdout", _ClosedPipeStdout())

    with pytest.raises(SystemExit) as exc:
        pyromark_cli((str(file),))

    if quiet:
        assert exc.value.code == 1
        assert not capsys.readouterr().err
    else:
        assert str(exc.value).startswith("pyromark: ")
        assert "Invalid argument" in str(exc.value)


def test_cli_still_reports_einval_from_the_output_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    file = tmp_path / "in.md"
    file.write_text("# Hello world", encoding="utf-8")
    monkeypatch.setattr(sys, "platform", "win32")

    def refuse(*_args: object, **_kwargs: object) -> None:
        raise OSError(errno.EINVAL, "Invalid argument")

    monkeypatch.setattr(pyromark, "write_html", refuse)

    with pytest.raises(SystemExit) as exc:
        pyromark_cli(("-o", str(tmp_path / "out.html"), str(file)))

    assert str(exc.value).startswith("pyromark: ")
    assert "Invalid argument" in str(exc.value)
    assert not capsys.readouterr().out


def test_python_m_pyromark_runs_the_cli(tmp_path: Path) -> None:
    file = tmp_path / "in.md"
    file.write_text("# Hello world", encoding="utf-8")

    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "pyromark", str(file)],
        capture_output=True,
        check=True,
    )

    assert result.stdout == pyromark.html("# Hello world").encode()


class _FailingStdout:
    """A stdout whose byte stream refuses every write with a plain OSError."""

    def __init__(self, fileno: int) -> None:
        self.buffer = _RefusingBuffer()
        self._fileno = fileno

    def fileno(self) -> int:
        return self._fileno

    def flush(self) -> None: ...


class _RefusingBuffer(io.BytesIO):
    @override
    def write(self, buffer: Buffer, /) -> int:
        raise OSError(errno.ENOSPC, "No space left on device")


def test_cli_stops_writing_to_stdout_after_a_plain_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    file = tmp_path / "in.md"
    file.write_text("# Hello world", encoding="utf-8")
    sink = tmp_path / "sink"

    with sink.open("wb") as handle:
        monkeypatch.setattr(sys, "stdout", _FailingStdout(handle.fileno()))

        with pytest.raises(SystemExit) as exc:
            pyromark_cli((str(file),))

        os.write(handle.fileno(), b"discarded at interpreter shutdown")

    assert str(exc.value).startswith("pyromark: ")
    assert sink.read_bytes() == b""


def _shell_commands(page: Path, /) -> list[str]:
    """The pyromark commands in the page's bash blocks, run with uvx or not."""
    commands = []
    inside = False
    for line in map(str.strip, page.read_text("utf-8").splitlines()):
        if line.startswith("```"):
            inside = line.startswith("```bash")
            continue
        command = line.removeprefix("uvx ")
        if inside and command.startswith("pyromark "):
            commands.append(command)
    return commands


@pytest.mark.parametrize("page", [README, CLI_DOC], ids=lambda page: page.name)
def test_documented_command_line_examples_run(
    page: Path, tmp_path: Path
) -> None:
    commands = _shell_commands(page)
    assert commands

    for command in commands:
        arguments = [
            str(Path(__file__).parent.parent / argument)
            if argument.endswith(".md")
            else argument
            for argument in shlex.split(command)[1:]
        ]
        if "-o" in arguments:
            arguments[arguments.index("-o") + 1] = str(tmp_path / "out.html")
        pyromark_cli(arguments)
