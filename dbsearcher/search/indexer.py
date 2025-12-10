"""
File indexer for O(1) file lookups and metadata caching.

Provides fast file discovery and metadata retrieval without
redundant filesystem operations.
"""

import collections.abc
import pathlib
import typing

import dbsearcher.constants
import dbsearcher.exceptions
import dbsearcher.types


@typing.final
class FileIndexer:
    """
    File index for fast file discovery and metadata caching.

    Maintains an in-memory index of searchable files with their
    metadata for O(1) lookups.
    """

    __slots__: typing.ClassVar[tuple[str, ...]] = (
        "_base_dir",
        "_extensions",
        "_index",
        "_is_stale",
    )

    def __init__(
        self,
        base_dir: pathlib.Path,
        *,
        extensions: tuple[str, ...] = dbsearcher.constants.SUPPORTED_EXTENSIONS,
    ) -> None:
        """
        Initialize the file indexer.

        Parameters
        ----------
        base_dir
            Base directory to index.
        extensions
            File extensions to include in index.
        """
        self._base_dir: typing.Final[pathlib.Path] = base_dir
        self._extensions: typing.Final[tuple[str, ...]] = extensions
        self._index: dict[str, dbsearcher.types.FileInfo] = {}
        self._is_stale: bool = True

    def _get_match_type(self, extension: str) -> dbsearcher.types.MatchType:
        """
        Get match type for file extension.

        Parameters
        ----------
        extension
            File extension (lowercase, with dot).

        Returns
        -------
        MatchType
            Corresponding match type.
        """
        extension_lower: str = extension.lower()
        if extension_lower == ".csv":
            return dbsearcher.types.MatchType.CSV
        elif extension_lower == ".txt":
            return dbsearcher.types.MatchType.TXT
        elif extension_lower == ".sql":
            return dbsearcher.types.MatchType.SQL
        else:
            return dbsearcher.types.MatchType.TXT  # Default

    def refresh(self) -> int:
        """
        Refresh the file index by scanning the base directory.

        Returns
        -------
        int
            Number of files indexed.
        """
        self._index.clear()

        if not self._base_dir.exists():
            self._is_stale = False
            return 0

        if not self._base_dir.is_dir():
            raise dbsearcher.exceptions.ConfigurationError(
                f"Base path is not a directory: {self._base_dir}",
                config_key="base_dir",
            )

        try:
            for file_path in self._base_dir.iterdir():
                if not file_path.is_file():
                    continue

                extension: str = file_path.suffix.lower()
                if extension not in self._extensions:
                    continue

                try:
                    size: int = file_path.stat().st_size
                    file_info: dbsearcher.types.FileInfo = dbsearcher.types.FileInfo(
                        path=file_path,
                        name=file_path.name,
                        size_bytes=size,
                        match_type=self._get_match_type(extension),
                    )
                    self._index[file_path.name] = file_info
                except OSError:
                    # Skip files we can't stat
                    continue

        except OSError as e:
            raise dbsearcher.exceptions.FileAccessError(
                f"Failed to scan directory: {self._base_dir}",
                path=str(self._base_dir),
                details=str(e),
            ) from e

        self._is_stale = False
        return len(self._index)

    def get_files(self) -> dbsearcher.types.FileInfoList:
        """
        Get all indexed files.

        Returns
        -------
        list[FileInfo]
            List of all indexed files.
        """
        if self._is_stale:
            self.refresh()
        return list(self._index.values())

    def get_file(self, name: str) -> dbsearcher.types.FileInfo | None:
        """
        Get file info by name (O(1) lookup).

        Parameters
        ----------
        name
            File name to look up.

        Returns
        -------
        FileInfo | None
            File info if found, None otherwise.
        """
        if self._is_stale:
            self.refresh()
        return self._index.get(name)

    def get_total_size(self) -> int:
        """
        Get total size of all indexed files in bytes.

        Returns
        -------
        int
            Total size in bytes.
        """
        if self._is_stale:
            self.refresh()
        return sum(f.size_bytes for f in self._index.values())

    def get_file_count(self) -> int:
        """
        Get number of indexed files.

        Returns
        -------
        int
            Number of files.
        """
        if self._is_stale:
            self.refresh()
        return len(self._index)

    def invalidate(self) -> None:
        """Mark index as stale, forcing refresh on next access."""
        self._is_stale = True

    def __len__(self) -> int:
        """Get number of indexed files."""
        return self.get_file_count()

    def __iter__(self) -> collections.abc.Iterator[dbsearcher.types.FileInfo]:
        """Iterate over indexed files."""
        return iter(self.get_files())


__all__: list[str] = [
    "FileIndexer",
]
