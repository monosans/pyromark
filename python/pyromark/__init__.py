"""Blazingly fast Markdown pull parser."""

from __future__ import annotations

from pyromark._options import Options
from pyromark._pyromark import (
    Markdown,
    __version__ as __version__,
    events,
    events_with_range,
    html,
    reference_definitions,
    write_html,
)
from pyromark._theme import Theme

__all__ = (
    "Markdown",
    "Options",
    "Theme",
    "events",
    "events_with_range",
    "html",
    "reference_definitions",
    "write_html",
)
