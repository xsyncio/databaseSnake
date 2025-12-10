"""
Type-safe ANSI color system.

Provides color codes as an enum with TTY detection and
safe fallback for non-color terminals.
"""

import enum
import os
import sys
import typing


class AnsiCode(enum.Enum):
    """ANSI escape codes for terminal colors and formatting."""

    # Colors
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    PURPLE = "\033[35m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"

    # Formatting
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"

    # Reset
    END = "\033[0m"
    RESET = "\033[0m"


# Cache for color support detection
_color_support_cache: bool | None = None


def supports_color() -> bool:
    """
    Detect if the terminal supports ANSI colors.

    Returns
    -------
    bool
        True if colors are supported.
    """
    global _color_support_cache  # noqa: PLW0603

    if _color_support_cache is not None:
        return _color_support_cache

    # Check for explicit NO_COLOR env var
    if os.environ.get("NO_COLOR"):
        _color_support_cache = False
        return False

    # Check for FORCE_COLOR env var
    if os.environ.get("FORCE_COLOR"):
        _color_support_cache = True
        return True

    # Check if stdout is a TTY
    if not hasattr(sys.stdout, "isatty"):
        _color_support_cache = False
        return False

    if not sys.stdout.isatty():
        _color_support_cache = False
        return False

    # Check for TERM env var
    term: str | None = os.environ.get("TERM")
    if term == "dumb":
        _color_support_cache = False
        return False

    _color_support_cache = True
    return True


def colorize(
    text: str,
    color: AnsiCode,
    *,
    bold: bool = False,
    underline: bool = False,
) -> str:
    """
    Apply ANSI color codes to text.

    Parameters
    ----------
    text
        Text to colorize.
    color
        Color to apply.
    bold
        Whether to make text bold.
    underline
        Whether to underline text.

    Returns
    -------
    str
        Colorized text string.
    """
    if not supports_color():
        return text

    prefix: str = ""
    if bold:
        prefix += AnsiCode.BOLD.value
    if underline:
        prefix += AnsiCode.UNDERLINE.value
    prefix += color.value

    return f"{prefix}{text}{AnsiCode.END.value}"


def strip_ansi(text: str) -> str:
    """
    Remove ANSI escape codes from text.

    Parameters
    ----------
    text
        Text with potential ANSI codes.

    Returns
    -------
    str
        Text with all ANSI codes removed.
    """
    import re

    ansi_pattern: typing.Final[str] = r"\033\[[0-9;]*m"
    return re.sub(ansi_pattern, "", text)


__all__: list[str] = [
    "AnsiCode",
    "supports_color",
    "colorize",
    "strip_ansi",
]
