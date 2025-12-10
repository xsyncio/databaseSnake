"""
Filesystem utilities.

Provides file operations with proper error handling and type safety.
"""

import pathlib

import dbsearcher.constants
import dbsearcher.exceptions


def get_folder_size(path: pathlib.Path) -> int:
    """
    Calculate total size of all files in a directory.

    Parameters
    ----------
    path
        Directory path to calculate size for.

    Returns
    -------
    int
        Total size in bytes.
    """
    if not path.exists():
        return 0

    if not path.is_dir():
        raise dbsearcher.exceptions.FileAccessError(
            f"Path is not a directory: {path}",
            path=str(path),
        )

    total_size: int = 0
    try:
        for item in path.rglob("*"):
            if item.is_file():
                try:
                    total_size += item.stat().st_size
                except OSError:
                    # Skip files we can't access
                    continue
    except OSError as e:
        raise dbsearcher.exceptions.FileAccessError(
            f"Failed to scan directory: {path}",
            path=str(path),
            details=str(e),
        ) from e

    return total_size


def count_files(
    path: pathlib.Path,
    *,
    extensions: tuple[str, ...] = dbsearcher.constants.SUPPORTED_EXTENSIONS,
) -> int:
    """
    Count files with specified extensions in a directory.

    Parameters
    ----------
    path
        Directory path to count files in.
    extensions
        File extensions to count.

    Returns
    -------
    int
        Number of matching files.
    """
    if not path.exists():
        return 0

    if not path.is_dir():
        return 0

    count: int = 0
    try:
        for item in path.iterdir():
            if item.is_file() and item.suffix.lower() in extensions:
                count += 1
    except OSError:
        return 0

    return count


def ensure_directory(path: pathlib.Path) -> bool:
    """
    Ensure a directory exists, creating it if necessary.

    Parameters
    ----------
    path
        Directory path to ensure exists.

    Returns
    -------
    bool
        True if directory was created, False if it already existed.
    """
    if path.exists():
        return False

    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except OSError as e:
        raise dbsearcher.exceptions.FileAccessError(
            f"Failed to create directory: {path}",
            path=str(path),
            details=str(e),
        ) from e


def format_size(size_bytes: int) -> str:
    """
    Format byte size to human-readable string.

    Parameters
    ----------
    size_bytes
        Size in bytes.

    Returns
    -------
    str
        Human-readable size string.
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / 1024 / 1024:.2f} MB"
    else:
        return f"{size_bytes / 1024 / 1024 / 1024:.2f} GB"


__all__: list[str] = [
    "get_folder_size",
    "count_files",
    "ensure_directory",
    "format_size",
]
