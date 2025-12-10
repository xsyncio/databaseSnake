"""
Custom exception hierarchy for DBSearcher.

All exceptions inherit from DBSearcherError for consistent error handling.
"""

import typing

import typing_extensions


class DBSearcherError(Exception):
    """
    Base exception for all DBSearcher errors.

    All custom exceptions should inherit from this class to enable
    unified exception handling.
    """

    def __init__(self, message: str, *, details: str | None = None) -> None:
        """
        Initialize the exception.

        Parameters
        ----------
        message
            Human-readable error message.
        details
            Optional additional details for debugging.
        """
        super().__init__(message)
        self.message: typing.Final[str] = message
        self.details: typing.Final[str | None] = details

    @typing_extensions.override
    def __str__(self) -> str:
        """Return formatted error string."""
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class SearchError(DBSearcherError):
    """
    Exception raised when search operations fail.

    Examples include malformed queries, search timeout, or
    internal search engine errors.
    """

    def __init__(
        self,
        message: str,
        *,
        query: str | None = None,
        details: str | None = None,
    ) -> None:
        """
        Initialize the search error.

        Parameters
        ----------
        message
            Human-readable error message.
        query
            The search query that caused the error.
        details
            Optional additional details for debugging.
        """
        super().__init__(message, details=details)
        self.query: typing.Final[str | None] = query


class FileAccessError(DBSearcherError):
    """
    Exception raised when file operations fail.

    Examples include missing files, permission errors, or
    encoding issues.
    """

    def __init__(
        self,
        message: str,
        *,
        path: str | None = None,
        details: str | None = None,
    ) -> None:
        """
        Initialize the file access error.

        Parameters
        ----------
        message
            Human-readable error message.
        path
            Path to the file that caused the error.
        details
            Optional additional details for debugging.
        """
        super().__init__(message, details=details)
        self.path: typing.Final[str | None] = path


class ConfigurationError(DBSearcherError):
    """
    Exception raised when configuration is invalid.

    Examples include invalid settings, missing required config,
    or incompatible option combinations.
    """

    def __init__(
        self,
        message: str,
        *,
        config_key: str | None = None,
        details: str | None = None,
    ) -> None:
        """
        Initialize the configuration error.

        Parameters
        ----------
        message
            Human-readable error message.
        config_key
            The configuration key that caused the error.
        details
            Optional additional details for debugging.
        """
        super().__init__(message, details=details)
        self.config_key: typing.Final[str | None] = config_key


class ParsingError(DBSearcherError):
    """
    Exception raised when file parsing fails.

    Examples include malformed CSV, invalid SQL syntax,
    or unexpected file format.
    """

    def __init__(
        self,
        message: str,
        *,
        file_path: str | None = None,
        line_number: int | None = None,
        details: str | None = None,
    ) -> None:
        """
        Initialize the parsing error.

        Parameters
        ----------
        message
            Human-readable error message.
        file_path
            Path to the file being parsed.
        line_number
            Line number where parsing failed.
        details
            Optional additional details for debugging.
        """
        super().__init__(message, details=details)
        self.file_path: typing.Final[str | None] = file_path
        self.line_number: typing.Final[int | None] = line_number


__all__: list[str] = [
    "DBSearcherError",
    "SearchError",
    "FileAccessError",
    "ConfigurationError",
    "ParsingError",
]
