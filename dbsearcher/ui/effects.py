"""
Visual effects for console output.

Provides typing effects, loading animations, and progress indicators
with proper TTY detection and graceful fallback.
"""

import sys
import time

import dbsearcher.constants
import dbsearcher.ui.colors


def typing_effect(
    text: str,
    *,
    color: dbsearcher.ui.colors.AnsiCode = dbsearcher.ui.colors.AnsiCode.GREEN,
    delay: float = dbsearcher.constants.TYPING_EFFECT_DELAY,
) -> None:
    """
    Display text with typewriter-style animation.

    Parameters
    ----------
    text
        Text to display.
    color
        Color to apply to text.
    delay
        Delay between characters in seconds.
    """
    if not sys.stdout.isatty():
        # Non-interactive: just print immediately
        print(dbsearcher.ui.colors.colorize(text, color))
        return

    colored_char_prefix: str = ""
    if dbsearcher.ui.colors.supports_color():
        colored_char_prefix = color.value

    for char in text:
        _ = sys.stdout.write(colored_char_prefix + char)
        sys.stdout.flush()
        time.sleep(delay)

    if dbsearcher.ui.colors.supports_color():
        _ = sys.stdout.write(dbsearcher.ui.colors.AnsiCode.END.value)

    print()  # Newline at end


def loading_animation(
    *,
    duration: float = dbsearcher.constants.DEFAULT_LOADING_DURATION,
    message: str = "Loading",
) -> None:
    """
    Display animated loading spinner.

    Parameters
    ----------
    duration
        Total duration of animation in seconds.
    message
        Message to display next to spinner.
    """
    if not sys.stdout.isatty():
        # Non-interactive: just print message
        print(f"{message}...")
        return

    frames: tuple[str, ...] = dbsearcher.constants.LOADING_FRAMES
    frame_delay: float = dbsearcher.constants.LOADING_ANIMATION_FRAME_DELAY
    start_time: float = time.time()
    frame_idx: int = 0

    purple: str = dbsearcher.ui.colors.AnsiCode.PURPLE.value
    end: str = dbsearcher.ui.colors.AnsiCode.END.value

    while time.time() - start_time < duration:
        frame: str = frames[frame_idx % len(frames)]
        _ = sys.stdout.write(f"\r{purple}{message} {frame} {end}")
        sys.stdout.flush()
        time.sleep(frame_delay)
        frame_idx += 1

    # Clear the line
    _ = sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")
    sys.stdout.flush()


def progress_bar(
    current: int,
    total: int,
    *,
    width: int = 40,
    prefix: str = "Progress",
) -> None:
    """
    Display inline progress bar.

    Parameters
    ----------
    current
        Current progress value.
    total
        Total value.
    width
        Width of the progress bar in characters.
    prefix
        Text prefix before the bar.
    """
    if total == 0:
        return

    percentage: float = min(current / total, 1.0)
    filled: int = int(width * percentage)
    empty: int = width - filled

    bar: str = "█" * filled + "░" * empty
    percent_str: str = f"{percentage * 100:.1f}%"

    if dbsearcher.ui.colors.supports_color():
        cyan: str = dbsearcher.ui.colors.AnsiCode.CYAN.value
        green: str = dbsearcher.ui.colors.AnsiCode.GREEN.value
        end: str = dbsearcher.ui.colors.AnsiCode.END.value
        output: str = f"\r{cyan}{prefix}{end} [{green}{bar}{end}] {percent_str}"
    else:
        output = f"\r{prefix} [{bar}] {percent_str}"

    _ = sys.stdout.write(output)
    sys.stdout.flush()

    if current >= total:
        print()  # Newline when complete


__all__: list[str] = [
    "typing_effect",
    "loading_animation",
    "progress_bar",
]
