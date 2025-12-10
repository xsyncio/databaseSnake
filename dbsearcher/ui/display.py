"""
Screen management and display utilities.

Provides clear screen, banner display, and result formatting
with rich console integration.
"""

import os
import sys

import rich.console
import rich.panel
import rich.text

import dbsearcher.constants
import dbsearcher.search.results
import dbsearcher.types
import dbsearcher.ui.colors


def clear_screen() -> None:
    """Clear the terminal screen in a cross-platform way."""
    if sys.stdout.isatty():
        _ = os.system("clear" if os.name != "nt" else "cls")


def display_banner(
    console: rich.console.Console,
    *,
    file_count: int = 0,
    total_size_bytes: int = 0,
) -> None:
    """
    Display the application banner with ASCII art and statistics.

    Parameters
    ----------
    console
        Rich console for output.
    file_count
        Number of files in database.
    total_size_bytes
        Total size of files in bytes.
    """
    # ASCII art banner
    banner_text: rich.text.Text = rich.text.Text()
    banner_text.append(dbsearcher.constants.BANNER_ART, style="cyan bold")

    banner_panel: rich.panel.Panel = rich.panel.Panel(
        banner_text,
        border_style="cyan",
        padding=(0, 2),
    )
    console.print(banner_panel)

    # Version info
    version_text: str = (
        f"v{dbsearcher.constants.VERSION} | "
        f"by {dbsearcher.constants.AUTHOR} | "
        f"{dbsearcher.constants.GITHUB_URL}"
    )
    console.print(
        rich.panel.Panel(
            version_text,
            border_style="green",
            padding=(0, 1),
        )
    )

    # Statistics
    size_mb: float = total_size_bytes / 1024 / 1024
    stats_text: str = f"📁 Files: {file_count} | 💾 Size: {size_mb:.2f} MB"
    console.print(f"\n[yellow]{stats_text}[/yellow]\n")


def display_search_examples(console: rich.console.Console) -> None:
    """
    Display search examples for user guidance.

    Parameters
    ----------
    console
        Rich console for output.
    """
    console.print("[cyan]🔍 Search Examples:[/cyan]")
    console.print("[yellow]• User ID: 556343434[/yellow]")
    console.print("[yellow]• Phone: +19000000000[/yellow]")
    console.print("[yellow]• Name: John[/yellow]")
    console.print("[yellow]• Email: example@mail.eg[/yellow]\n")


def display_menu_options(console: rich.console.Console) -> None:
    """
    Display main menu options.

    Parameters
    ----------
    console
        Rich console for output.
    """
    console.print("[bold green]1.[/bold green] Search in databases")
    console.print("[bold red]2.[/bold red] Exit\n")


def display_results(
    console: rich.console.Console,
    results: dbsearcher.types.SearchResultList,
    stats: dbsearcher.types.SearchStats,
) -> None:
    """
    Display search results with formatting.

    Parameters
    ----------
    console
        Rich console for output.
    results
        List of search results.
    stats
        Search statistics.
    """
    if not results:
        console.print("\n[bold red]❌ No results found[/bold red]\n")
        return

    # Show stats
    stats_panel: rich.panel.Panel = dbsearcher.search.results.format_stats(stats)
    console.print(stats_panel)
    console.print()

    # Show results (limit to first 50 for console display)
    display_limit: int = 50
    displayed: int = 0

    for result in results:
        if displayed >= display_limit:
            remaining: int = len(results) - display_limit
            console.print(f"\n[dim]... and {remaining} more results[/dim]")
            break

        result_panel: rich.panel.Panel = (
            dbsearcher.search.results.format_result_for_display(result)
        )
        console.print(result_panel)
        displayed += 1


def get_user_input(prompt: str, *, color: str = "cyan") -> str:
    """
    Get user input with styled prompt.

    Parameters
    ----------
    prompt
        Prompt text to display.
    color
        Color for the prompt.

    Returns
    -------
    str
        User input string.
    """
    # Use raw input for better compatibility
    if dbsearcher.ui.colors.supports_color():
        color_code: str = getattr(
            dbsearcher.ui.colors.AnsiCode,
            color.upper(),
            dbsearcher.ui.colors.AnsiCode.CYAN,
        ).value
        end_code: str = dbsearcher.ui.colors.AnsiCode.END.value
        return input(f"{color_code}{prompt}{end_code}")
    else:
        return input(prompt)


__all__: list[str] = [
    "clear_screen",
    "display_banner",
    "display_search_examples",
    "display_menu_options",
    "display_results",
    "get_user_input",
]
