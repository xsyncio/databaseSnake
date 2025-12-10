"""
Search result data structures and formatting.

Provides immutable result containers and formatting utilities.
"""

import rich.panel
import rich.table
import rich.text

import dbsearcher.types


def format_result_for_display(
    result: dbsearcher.types.SearchResult,
    *,
    highlight_color: str = "yellow",
) -> rich.panel.Panel:
    """
    Format a search result as a rich panel for display.

    Parameters
    ----------
    result
        The search result to format.
    highlight_color
        Color to use for content highlighting.

    Returns
    -------
    rich.panel.Panel
        Formatted panel ready for console output.
    """
    content: rich.text.Text = rich.text.Text()
    content.append("File: ", style="bold cyan")
    content.append(result.file_name, style="cyan")
    content.append("\n")
    content.append("Line: ", style="dim")
    content.append(str(result.line_number), style="dim")
    content.append("\n\n")
    content.append(result.content, style=highlight_color)

    panel: rich.panel.Panel = rich.panel.Panel(
        content,
        title=f"[bold magenta]Match #{result.line_number}[/bold magenta]",
        border_style="magenta",
        padding=(0, 1),
    )
    return panel


def create_results_table(
    results: dbsearcher.types.SearchResultList,
    *,
    max_content_width: int = 80,
) -> rich.table.Table:
    """
    Create a table view of search results.

    Parameters
    ----------
    results
        List of search results.
    max_content_width
        Maximum width for content column.

    Returns
    -------
    rich.table.Table
        Formatted table ready for console output.
    """
    table: rich.table.Table = rich.table.Table(
        title="[bold cyan]Search Results[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
        border_style="dim",
        row_styles=["", "dim"],
    )

    table.add_column("#", style="dim", width=5)
    table.add_column("File", style="cyan", width=25)
    table.add_column("Line", style="dim", width=8)
    table.add_column("Content", style="yellow", max_width=max_content_width)

    for idx, result in enumerate(results, start=1):
        # Truncate content if too long
        content: str = result.content
        if len(content) > max_content_width:
            content = content[: max_content_width - 3] + "..."

        table.add_row(
            str(idx),
            result.file_name,
            str(result.line_number),
            content,
        )

    return table


def format_stats(stats: dbsearcher.types.SearchStats) -> rich.panel.Panel:
    """
    Format search statistics as a panel.

    Parameters
    ----------
    stats
        Search statistics to format.

    Returns
    -------
    rich.panel.Panel
        Formatted panel with stats.
    """
    content: rich.text.Text = rich.text.Text()
    content.append("📁 Files Searched: ", style="cyan")
    content.append(str(stats.files_searched), style="bold cyan")
    content.append("\n")
    content.append("🎯 Matches Found: ", style="green")
    content.append(str(stats.total_matches), style="bold green")
    content.append("\n")
    content.append("⏱️  Duration: ", style="yellow")
    content.append(f"{stats.duration_seconds:.3f}s", style="bold yellow")

    panel: rich.panel.Panel = rich.panel.Panel(
        content,
        title="[bold cyan]Search Statistics[/bold cyan]",
        border_style="cyan",
        padding=(0, 1),
    )
    return panel


__all__: list[str] = [
    "format_result_for_display",
    "create_results_table",
    "format_stats",
]
