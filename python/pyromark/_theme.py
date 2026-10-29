from __future__ import annotations

from enum import StrEnum


class Theme(StrEnum):
    r"""Bundled syntax highlighting themes, for the `highlight` argument.

    Themes emit inline styles, so no stylesheet is needed, but the
    background is fixed and ignores `prefers-color-scheme`. Pass a callable
    instead to emit your own classes or to use Pygments. The ~190 languages
    of [bat](https://github.com/sharkdp/bat) are recognized by name or file
    extension; blocks in other languages are left unhighlighted.

    Examples:
        ```python
        html = pyromark.html(
            "~~~python\nx = 1\n~~~", highlight=pyromark.Theme.INSPIRED_GITHUB
        )
        assert html.startswith('<pre style="background-color:#ffffff;">')
        ```
    """

    INSPIRED_GITHUB = "InspiredGitHub"
    """Light, resembling GitHub."""
    SOLARIZED_DARK = "Solarized (dark)"
    """Solarized, dark."""
    SOLARIZED_LIGHT = "Solarized (light)"
    """Solarized, light."""
    BASE16_EIGHTIES_DARK = "base16-eighties.dark"
    """base16 Eighties, dark."""
    BASE16_MOCHA_DARK = "base16-mocha.dark"
    """base16 Mocha, dark."""
    BASE16_OCEAN_DARK = "base16-ocean.dark"
    """base16 Ocean, dark."""
    BASE16_OCEAN_LIGHT = "base16-ocean.light"
    """base16 Ocean, light."""
