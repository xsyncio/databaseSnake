"""
Menu system with input validation.

Provides the main application menu loop with robust input handling
and error recovery.
"""

import time
import typing

import rich.console

import dbsearcher.exceptions
import dbsearcher.logging
import dbsearcher.search.engine
import dbsearcher.types
import dbsearcher.ui.display
import dbsearcher.ui.effects


@typing.final
class MainMenu:
    """
    Main application menu with search interface.

    Provides the primary user interaction loop with robust
    input validation and error handling.
    """

    __slots__: typing.ClassVar[tuple[str, ...]] = (
        "_console",
        "_logger",
        "_search_engine",
        "_running",
    )

    def __init__(self) -> None:
        """Initialize the main menu."""
        self._console: typing.Final[rich.console.Console] = rich.console.Console()
        self._logger: typing.Final[dbsearcher.logging.DBSearcherLogger] = (
            dbsearcher.logging.get_logger()
        )
        self._search_engine: typing.Final[dbsearcher.search.engine.SearchEngine] = (
            dbsearcher.search.engine.SearchEngine()
        )
        self._running: bool = True

    def _display_header(self) -> None:
        """Display the application header with stats."""
        dbsearcher.ui.display.clear_screen()

        file_count: int
        total_size: int
        file_count, total_size = self._search_engine.get_file_stats()

        dbsearcher.ui.display.display_banner(
            self._console,
            file_count=file_count,
            total_size_bytes=total_size,
        )

    def _handle_search(self) -> None:
        """Handle search option."""
        query: str = dbsearcher.ui.display.get_user_input(
            "\nEnter search query: ",
            color="yellow",
        )

        if not query.strip():
            self._console.print("[bold red]Please enter a query![/bold red]")
            time.sleep(1)
            return

        self._logger.info(f"Searching for: {query}")

        # Show loading animation
        dbsearcher.ui.effects.loading_animation(duration=0.5, message="Searching")

        # Perform parallel search for speed
        try:
            results: dbsearcher.types.SearchResultList
            stats: dbsearcher.types.SearchStats
            results, stats = self._search_engine.search_parallel(query)

            # Display results
            dbsearcher.ui.display.clear_screen()
            self._display_header()
            dbsearcher.ui.display.display_results(self._console, results, stats)

        except dbsearcher.exceptions.SearchError as e:
            self._logger.error(f"Search failed: {e}")
            self._console.print(f"[bold red]Search error: {e}[/bold red]")

        # Wait for user to continue
        _ = dbsearcher.ui.display.get_user_input(
            "\nPress Enter to continue...",
            color="cyan",
        )

    def _handle_exit(self) -> None:
        """Handle exit option."""
        self._console.print("\n[cyan]Goodbye! 🐍[/cyan]")
        time.sleep(0.5)
        self._running = False

    def _handle_invalid_choice(self) -> None:
        """Handle invalid menu choice."""
        self._console.print("[bold red]Invalid choice![/bold red]")
        time.sleep(1)

    def run(self) -> int:
        """
        Run the main menu loop.

        Returns
        -------
        int
            Exit code (0 for success).
        """
        self._logger.info("Starting databaseSnake")

        while self._running:
            try:
                self._display_header()
                dbsearcher.ui.display.display_search_examples(self._console)
                dbsearcher.ui.display.display_menu_options(self._console)

                choice: str = dbsearcher.ui.display.get_user_input(
                    "Choose an option: ",
                    color="cyan",
                )

                if choice == "1":
                    self._handle_search()
                elif choice == "2":
                    self._handle_exit()
                else:
                    self._handle_invalid_choice()

            except KeyboardInterrupt:
                self._console.print("\n[red]Interrupted[/red]")
                self._running = False
            except Exception as e:
                self._logger.error(f"Unexpected error: {e}", exc_info=True)
                self._console.print(f"[bold red]Error: {e}[/bold red]")
                time.sleep(2)

        self._logger.info("databaseSnake exiting")
        return 0


__all__: list[str] = [
    "MainMenu",
]
