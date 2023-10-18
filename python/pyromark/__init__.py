"""Blazingly fast Markdown parser."""

from __future__ import annotations

from ._extensions import Extensions
from ._pyromark import (
    Markdown,
    __version__ as __version__,  # noqa: PLC0414
    markdown,
)

__all__ = ("Extensions", "Markdown", "markdown")
