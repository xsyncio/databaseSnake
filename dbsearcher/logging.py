"""
Ultra-robust logging system for DBSearcher.

Provides structured, color-safe, console-optimized logging with
beautiful output using rich library integration.
"""

import logging
import sys
import typing

import rich.console
import rich.logging
import rich.theme

import dbsearcher.types


# Custom log level for SUCCESS (between INFO and WARNING)
SUCCESS_LEVEL: typing.Final[int] = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")


@typing.final
class DBSearcherLogger:
    """
    Type-safe logger wrapper with rich console integration.

    Provides structured logging with color-coded output, automatic
    TTY detection, and thread-safe operations.
    """

    __slots__: typing.ClassVar[tuple[str, ...]] = ("_logger", "_console", "_enabled")

    def __init__(
        self,
        name: str = "dbsearcher",
        *,
        level: dbsearcher.types.LogLevel = dbsearcher.types.LogLevel.INFO,
        enable_rich: bool = True,
    ) -> None:
        """
        Initialize the logger.

        Parameters
        ----------
        name
            Logger name for identification.
        level
            Minimum log level to display.
        enable_rich
            Whether to use rich formatting (auto-disabled for non-TTY).
        """
        self._logger: typing.Final[logging.Logger] = logging.getLogger(name)
        self._logger.setLevel(level.value)
        self._enabled: bool = True

        # Create custom theme for consistent colors
        custom_theme: rich.theme.Theme = rich.theme.Theme(
            {
                "logging.level.debug": "dim cyan",
                "logging.level.info": "blue",
                "logging.level.success": "bold green",
                "logging.level.warning": "yellow",
                "logging.level.error": "bold red",
                "logging.level.critical": "bold white on red",
            }
        )

        # Initialize console with TTY detection
        use_rich_formatting: bool = enable_rich and sys.stdout.isatty()
        self._console: typing.Final[rich.console.Console] = rich.console.Console(
            theme=custom_theme,
            force_terminal=use_rich_formatting,
            no_color=not use_rich_formatting,
        )

        # Configure handler
        if not self._logger.handlers:
            handler: rich.logging.RichHandler = rich.logging.RichHandler(
                console=self._console,
                show_time=True,
                show_path=False,
                rich_tracebacks=True,
                tracebacks_show_locals=False,
                markup=True,
            )
            handler.setLevel(level.value)
            self._logger.addHandler(handler)

    def _log(
        self,
        level: int,
        message: str,
        *,
        extra: dict[str, str | int | float | bool] | None = None,
    ) -> None:
        """
        Internal log method with consistent formatting.

        Parameters
        ----------
        level
            Numeric log level.
        message
            Log message.
        extra
            Optional extra data to include.
        """
        if not self._enabled:
            return

        if extra:
            formatted_extra: str = " | ".join(
                f"{key}={value}" for key, value in extra.items()
            )
            message = f"{message} [{formatted_extra}]"

        self._logger.log(level, message)

    def debug(
        self,
        message: str,
        *,
        extra: dict[str, str | int | float | bool] | None = None,
    ) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, message, extra=extra)

    def info(
        self,
        message: str,
        *,
        extra: dict[str, str | int | float | bool] | None = None,
    ) -> None:
        """Log info message."""
        self._log(logging.INFO, message, extra=extra)

    def success(
        self,
        message: str,
        *,
        extra: dict[str, str | int | float | bool] | None = None,
    ) -> None:
        """Log success message (custom level between INFO and WARNING)."""
        self._log(SUCCESS_LEVEL, f"[bold green]✓[/bold green] {message}", extra=extra)

    def warning(
        self,
        message: str,
        *,
        extra: dict[str, str | int | float | bool] | None = None,
    ) -> None:
        """Log warning message."""
        self._log(logging.WARNING, f"[yellow]⚠[/yellow] {message}", extra=extra)

    def error(
        self,
        message: str,
        *,
        extra: dict[str, str | int | float | bool] | None = None,
        exc_info: bool = False,
    ) -> None:
        """Log error message with optional exception info."""
        if exc_info:
            self._logger.exception(f"[bold red]✗[/bold red] {message}")
        else:
            self._log(logging.ERROR, f"[bold red]✗[/bold red] {message}", extra=extra)

    def critical(
        self,
        message: str,
        *,
        extra: dict[str, str | int | float | bool] | None = None,
    ) -> None:
        """Log critical message."""
        self._log(
            logging.CRITICAL,
            f"[bold white on red]🚨 CRITICAL[/bold white on red] {message}",
            extra=extra,
        )

    def set_level(self, level: dbsearcher.types.LogLevel) -> None:
        """Change the minimum log level."""
        self._logger.setLevel(level.value)
        for handler in self._logger.handlers:
            handler.setLevel(level.value)

    def disable(self) -> None:
        """Disable all logging output."""
        self._enabled = False

    def enable(self) -> None:
        """Enable logging output."""
        self._enabled = True

    @property
    def console(self) -> rich.console.Console:
        """Get the underlying rich console for direct output."""
        return self._console


# Module-level singleton logger instance
_logger: DBSearcherLogger | None = None


def get_logger(
    name: str = "dbsearcher",
    *,
    level: dbsearcher.types.LogLevel = dbsearcher.types.LogLevel.INFO,
) -> DBSearcherLogger:
    """
    Get or create the singleton logger instance.

    Parameters
    ----------
    name
        Logger name.
    level
        Minimum log level.

    Returns
    -------
    DBSearcherLogger
        The logger instance.
    """
    global _logger  # noqa: PLW0603
    if _logger is None:
        _logger = DBSearcherLogger(name, level=level)
    return _logger


__all__: list[str] = [
    "DBSearcherLogger",
    "get_logger",
    "SUCCESS_LEVEL",
]
