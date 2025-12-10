"""
Platform detection utilities.

Provides platform-specific information and environment detection.
"""

import os
import platform
import sys

import dbsearcher.types


def is_termux() -> bool:
    """
    Detect if running in Termux environment.

    Returns
    -------
    bool
        True if running in Termux.
    """
    prefix: str = os.getenv("PREFIX", "")
    return "com.termux" in prefix


def get_platform_info() -> dbsearcher.types.PlatformInfo:
    """
    Get comprehensive platform information.

    Returns
    -------
    PlatformInfo
        Platform detection information.
    """
    return dbsearcher.types.PlatformInfo(
        is_termux=is_termux(),
        system=platform.system(),
        python_version=sys.version,
    )


__all__: list[str] = [
    "is_termux",
    "get_platform_info",
]
