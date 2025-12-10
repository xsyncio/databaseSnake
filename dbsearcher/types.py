"""
Type definitions for DBSearcher.

All type aliases, protocols, TypedDicts, and dataclasses used throughout
the application are defined here for maximum type safety.
"""

import collections.abc
import dataclasses
import enum
import pathlib
import typing


class MatchType(enum.Enum):
    """Enumeration of supported file match types."""

    CSV = "csv"
    TXT = "txt"
    SQL = "sql"


class LogLevel(enum.Enum):
    """Enumeration of log levels with severity ordering."""

    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SearchResult:
    """
    Immutable search result with file location and matched content.

    Attributes
    ----------
    file_name
        Name of the file containing the match.
    file_path
        Full path to the file.
    line_number
        1-indexed line number where match was found.
    content
        The matched line or row content.
    match_type
        Type of file the match was found in.
    """

    file_name: str
    file_path: pathlib.Path
    line_number: int
    content: str
    match_type: MatchType


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class FileInfo:
    """
    Metadata about a searchable file.

    Attributes
    ----------
    path
        Full path to the file.
    name
        Basename of the file.
    size_bytes
        Size of the file in bytes.
    match_type
        Type classification of the file.
    """

    path: pathlib.Path
    name: str
    size_bytes: int
    match_type: MatchType


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SearchStats:
    """
    Statistics from a search operation.

    Attributes
    ----------
    files_searched
        Number of files that were searched.
    total_matches
        Total number of matches found.
    duration_seconds
        Time taken to complete the search.
    """

    files_searched: int
    total_matches: int
    duration_seconds: float


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class PlatformInfo:
    """
    Platform detection information.

    Attributes
    ----------
    is_termux
        Whether running in Termux environment.
    system
        Operating system name.
    python_version
        Python version string.
    """

    is_termux: bool
    system: str
    python_version: str


class SearchConfigProtocol(typing.Protocol):
    """Protocol defining search configuration interface."""

    @property
    def base_dir(self) -> pathlib.Path:
        """Base directory to search in."""
        ...

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        """Tuple of supported file extensions."""
        ...

    @property
    def max_results(self) -> int:
        """Maximum number of results to return."""
        ...

    @property
    def case_sensitive(self) -> bool:
        """Whether search is case-sensitive."""
        ...

    @property
    def parallel_workers(self) -> int:
        """Number of parallel workers for search."""
        ...


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SearchConfig:
    """
    Configuration for search operations.

    Implements SearchConfigProtocol with sensible defaults.
    """

    base_dir: pathlib.Path = dataclasses.field(
        default_factory=lambda: pathlib.Path("base")
    )
    supported_extensions: tuple[str, ...] = (".csv", ".txt", ".sql")
    max_results: int = 10000
    case_sensitive: bool = False
    parallel_workers: int = 4
    use_mmap_threshold: int = 10 * 1024 * 1024  # 10 MB


# Type aliases for complex generic types
SearchResultIterator: typing.TypeAlias = collections.abc.Iterator[SearchResult]
SearchResultList: typing.TypeAlias = list[SearchResult]
FileInfoList: typing.TypeAlias = list[FileInfo]
PathLike: typing.TypeAlias = pathlib.Path | str


__all__: list[str] = [
    "MatchType",
    "LogLevel",
    "SearchResult",
    "FileInfo",
    "SearchStats",
    "PlatformInfo",
    "SearchConfigProtocol",
    "SearchConfig",
    "SearchResultIterator",
    "SearchResultList",
    "FileInfoList",
    "PathLike",
]
