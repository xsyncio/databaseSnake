"""
High-performance file parsers for search operations.

Provides streaming parsers for CSV, TXT, and SQL files with
memory-mapped file support for large files.
"""

import collections.abc
import csv
import mmap
import pathlib
import typing

import dbsearcher.constants
import dbsearcher.exceptions
import dbsearcher.types


class BaseParser:
    """
    Base class for file parsers with shared functionality.

    Provides common utilities for file access, encoding detection,
    and memory-mapped file handling.
    """

    __slots__: typing.ClassVar[tuple[str, ...]] = ("_use_mmap_threshold",)

    def __init__(
        self,
        *,
        use_mmap_threshold: int = dbsearcher.constants.MMAP_THRESHOLD_BYTES,
    ) -> None:
        """
        Initialize the parser.

        Parameters
        ----------
        use_mmap_threshold
            File size threshold (bytes) above which mmap is used.
        """
        self._use_mmap_threshold: typing.Final[int] = use_mmap_threshold

    def _should_use_mmap(self, file_path: pathlib.Path) -> bool:
        """
        Determine if mmap should be used for the file.

        Parameters
        ----------
        file_path
            Path to the file.

        Returns
        -------
        bool
            True if file size exceeds mmap threshold.
        """
        try:
            size: int = file_path.stat().st_size
            return size > self._use_mmap_threshold
        except OSError:
            return False

    def _read_file_mmap(
        self,
        file_path: pathlib.Path,
    ) -> collections.abc.Generator[tuple[int, str], None, None]:
        """
        Read file using memory-mapped I/O for large files.

        Parameters
        ----------
        file_path
            Path to the file.

        Yields
        ------
        tuple[int, str]
            Line number and line content.
        """
        try:
            with open(file_path, "r+b") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    line_num: int = 0
                    for line_bytes in iter(mm.readline, b""):
                        line_num += 1
                        try:
                            line: str = line_bytes.decode(
                                dbsearcher.constants.DEFAULT_ENCODING, errors="ignore"
                            )
                            yield line_num, line.rstrip("\r\n")
                        except (UnicodeDecodeError, LookupError):
                            continue
        except OSError as e:
            raise dbsearcher.exceptions.FileAccessError(
                f"Failed to read file with mmap: {file_path}",
                path=str(file_path),
                details=str(e),
            ) from e

    def _read_file_standard(
        self,
        file_path: pathlib.Path,
    ) -> collections.abc.Generator[tuple[int, str], None, None]:
        """
        Read file using standard I/O for smaller files.

        Parameters
        ----------
        file_path
            Path to the file.

        Yields
        ------
        tuple[int, str]
            Line number and line content.
        """
        try:
            with open(
                file_path,
                "r",
                encoding=dbsearcher.constants.DEFAULT_ENCODING,
                errors="ignore",
            ) as f:
                for line_num, line in enumerate(f, start=1):
                    yield line_num, line.rstrip("\r\n")
        except OSError as e:
            raise dbsearcher.exceptions.FileAccessError(
                f"Failed to read file: {file_path}",
                path=str(file_path),
                details=str(e),
            ) from e

    def read_lines(
        self,
        file_path: pathlib.Path,
    ) -> collections.abc.Generator[tuple[int, str], None, None]:
        """
        Read file lines using optimal strategy (mmap or standard).

        Parameters
        ----------
        file_path
            Path to the file.

        Yields
        ------
        tuple[int, str]
            Line number and line content.
        """
        if self._should_use_mmap(file_path):
            yield from self._read_file_mmap(file_path)
        else:
            yield from self._read_file_standard(file_path)


@typing.final
class TextParser(BaseParser):
    """
    Parser for plain text files (.txt).

    Performs case-insensitive line-by-line search with streaming.
    """

    __slots__: typing.ClassVar[tuple[str, ...]] = ()

    def parse(
        self,
        file_path: pathlib.Path,
        query: str,
        *,
        case_sensitive: bool = False,
    ) -> dbsearcher.types.SearchResultIterator:
        """
        Parse text file and yield matching lines.

        Parameters
        ----------
        file_path
            Path to the text file.
        query
            Search query string.
        case_sensitive
            Whether search is case-sensitive.

        Yields
        ------
        SearchResult
            Matching search results.
        """
        # Use casefold for case-insensitive (faster than lower())
        search_query: str = query if case_sensitive else query.casefold()

        for line_num, line in self.read_lines(file_path):
            compare_line: str = line if case_sensitive else line.casefold()
            if search_query in compare_line:
                yield dbsearcher.types.SearchResult(
                    file_name=file_path.name,
                    file_path=file_path,
                    line_number=line_num,
                    content=line.strip(),
                    match_type=dbsearcher.types.MatchType.TXT,
                )


@typing.final
class CSVParser(BaseParser):
    """
    Parser for CSV files with streaming row-by-row search.

    Handles malformed CSV gracefully with error recovery.
    """

    __slots__: typing.ClassVar[tuple[str, ...]] = ()

    def parse(
        self,
        file_path: pathlib.Path,
        query: str,
        *,
        case_sensitive: bool = False,
    ) -> dbsearcher.types.SearchResultIterator:
        """
        Parse CSV file and yield matching rows.

        Parameters
        ----------
        file_path
            Path to the CSV file.
        query
            Search query string.
        case_sensitive
            Whether search is case-sensitive.

        Yields
        ------
        SearchResult
            Matching search results.
        """
        search_query: str = query if case_sensitive else query.casefold()

        try:
            with open(
                file_path,
                "r",
                encoding=dbsearcher.constants.DEFAULT_ENCODING,
                errors="ignore",
                newline="",
            ) as f:
                # Use csv.reader for proper parsing
                reader: collections.abc.Iterator[list[str]] = csv.reader(f)
                for line_num, row in enumerate(reader, start=1):
                    row_str: str = ", ".join(row)
                    compare_str: str = row_str if case_sensitive else row_str.casefold()
                    if search_query in compare_str:
                        yield dbsearcher.types.SearchResult(
                            file_name=file_path.name,
                            file_path=file_path,
                            line_number=line_num,
                            content=row_str,
                            match_type=dbsearcher.types.MatchType.CSV,
                        )
        except csv.Error as e:
            raise dbsearcher.exceptions.ParsingError(
                f"CSV parsing error in {file_path}",
                file_path=str(file_path),
                details=str(e),
            ) from e
        except OSError as e:
            raise dbsearcher.exceptions.FileAccessError(
                f"Failed to read CSV file: {file_path}",
                path=str(file_path),
                details=str(e),
            ) from e


@typing.final
class SQLParser(BaseParser):
    """
    Parser for SQL files with line-by-line search.

    Handles SQL files similar to text but with SQL-specific match type.
    """

    __slots__: typing.ClassVar[tuple[str, ...]] = ()

    def parse(
        self,
        file_path: pathlib.Path,
        query: str,
        *,
        case_sensitive: bool = False,
    ) -> dbsearcher.types.SearchResultIterator:
        """
        Parse SQL file and yield matching lines.

        Parameters
        ----------
        file_path
            Path to the SQL file.
        query
            Search query string.
        case_sensitive
            Whether search is case-sensitive.

        Yields
        ------
        SearchResult
            Matching search results.
        """
        search_query: str = query if case_sensitive else query.casefold()

        for line_num, line in self.read_lines(file_path):
            compare_line: str = line if case_sensitive else line.casefold()
            if search_query in compare_line:
                yield dbsearcher.types.SearchResult(
                    file_name=file_path.name,
                    file_path=file_path,
                    line_number=line_num,
                    content=line.strip(),
                    match_type=dbsearcher.types.MatchType.SQL,
                )


def get_parser_for_file(file_path: pathlib.Path) -> BaseParser:
    """
    Get the appropriate parser for a file based on extension.

    Parameters
    ----------
    file_path
        Path to the file.

    Returns
    -------
    BaseParser
        Appropriate parser instance.

    Raises
    ------
    ConfigurationError
        If file extension is not supported.
    """
    extension: str = file_path.suffix.lower()

    if extension == ".txt":
        return TextParser()
    elif extension == ".csv":
        return CSVParser()
    elif extension == ".sql":
        return SQLParser()
    else:
        raise dbsearcher.exceptions.ConfigurationError(
            f"Unsupported file extension: {extension}",
            config_key="file_extension",
            details=f"Supported: {dbsearcher.constants.SUPPORTED_EXTENSIONS}",
        )


__all__: list[str] = [
    "BaseParser",
    "TextParser",
    "CSVParser",
    "SQLParser",
    "get_parser_for_file",
]
