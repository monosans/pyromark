from __future__ import annotations

import pyromark
import pytest
from pyromark._cli import main as pyromark_cli  # noqa: PLC2701


def test_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        pyromark_cli(("--version",))
    assert exc.value.code == 0
    capture = capsys.readouterr()
    assert not capture.err
    assert capture.out == f"{pyromark.__version__}\n"
