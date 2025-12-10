"""
Immutable constants for databaseSnake.

All application-wide constants are defined here. All values are Final
to prevent accidental modification.
"""

import pathlib
import typing

# Application metadata
VERSION: typing.Final[str] = "1.0.0"
APP_NAME: typing.Final[str] = "databaseSnake"
AUTHOR: typing.Final[str] = "Xsyncio"
GITHUB_URL: typing.Final[str] = "https://github.com/xsyncio"

# Directory configuration
BASE_DIR: typing.Final[pathlib.Path] = pathlib.Path("base")
DEFAULT_ENCODING: typing.Final[str] = "utf-8"

# Supported file extensions
SUPPORTED_EXTENSIONS: typing.Final[tuple[str, ...]] = (".csv", ".txt", ".sql")

# Performance tuning
MMAP_THRESHOLD_BYTES: typing.Final[int] = 10 * 1024 * 1024  # 10 MB
DEFAULT_PARALLEL_WORKERS: typing.Final[int] = 4
MAX_RESULTS_DEFAULT: typing.Final[int] = 10000
CHUNK_SIZE_BYTES: typing.Final[int] = 64 * 1024  # 64 KB for streaming reads

# UI timing constants
TYPING_EFFECT_DELAY: typing.Final[float] = 0.03
LOADING_ANIMATION_FRAME_DELAY: typing.Final[float] = 0.1
DEFAULT_LOADING_DURATION: typing.Final[float] = 1.0

# Loading animation frames
LOADING_FRAMES: typing.Final[tuple[str, ...]] = (
    "⣾",
    "⣽",
    "⣻",
    "⢿",
    "⡿",
    "⣟",
    "⣯",
    "⣷",
)

# ASCII art banner - databaseSnake
BANNER_ART: typing.Final[str] = """
   ▄▄                  ▄▄                       ▄▄▄▄▄▄▄                          
   ██        ██        ██                      █████▀▀▀             ▄▄           
▄████  ▀▀█▄ ▀██▀▀ ▀▀█▄ ████▄  ▀▀█▄ ▄█▀▀▀ ▄█▀█▄  ▀████▄  ████▄  ▀▀█▄ ██ ▄█▀ ▄█▀█▄ 
██ ██ ▄█▀██  ██  ▄█▀██ ██ ██ ▄█▀██ ▀███▄ ██▄█▀    ▀████ ██ ██ ▄█▀██ ████   ██▄█▀ 
▀████ ▀█▄██  ██  ▀█▄██ ████▀ ▀█▄██ ▄▄▄█▀ ▀█▄▄▄ ███████▀ ██ ██ ▀█▄██ ██ ▀█▄ ▀█▄▄▄ 
"""

# Menu text constants
MENU_SEARCH_EXAMPLES: typing.Final[str] = """🔍 Search Examples:
• User ID: 556343434
• Phone: +19000000000
• Name: John
• Email: example@mail.eg"""

MENU_OPTIONS: typing.Final[tuple[tuple[str, str], ...]] = (
    ("1", "Search in databases"),
    ("2", "Exit"),
)


__all__: list[str] = [
    "VERSION",
    "APP_NAME",
    "AUTHOR",
    "GITHUB_URL",
    "BASE_DIR",
    "DEFAULT_ENCODING",
    "SUPPORTED_EXTENSIONS",
    "MMAP_THRESHOLD_BYTES",
    "DEFAULT_PARALLEL_WORKERS",
    "MAX_RESULTS_DEFAULT",
    "CHUNK_SIZE_BYTES",
    "TYPING_EFFECT_DELAY",
    "LOADING_ANIMATION_FRAME_DELAY",
    "DEFAULT_LOADING_DURATION",
    "LOADING_FRAMES",
    "BANNER_ART",
    "MENU_SEARCH_EXAMPLES",
    "MENU_OPTIONS",
]
