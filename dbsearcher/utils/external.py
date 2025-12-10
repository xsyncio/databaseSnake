"""
External application launching utilities.

Provides cross-platform external app launching with Termux support.
"""

import subprocess
import webbrowser

import dbsearcher.logging
import dbsearcher.utils.platform


def open_url(url: str) -> bool:
    """
    Open a URL in the default browser.

    Handles Termux environment with Android intents.

    Parameters
    ----------
    url
        URL to open.

    Returns
    -------
    bool
        True if successfully opened.
    """
    logger: dbsearcher.logging.DBSearcherLogger = dbsearcher.logging.get_logger()

    try:
        if dbsearcher.utils.platform.is_termux():
            # Use Android intent for Termux
            result: subprocess.CompletedProcess[bytes] = subprocess.run(
                [
                    "am",
                    "start",
                    "-a",
                    "android.intent.action.VIEW",
                    "-d",
                    url,
                ],
                capture_output=True,
                check=False,
            )
            success: bool = result.returncode == 0
            if success:
                logger.debug(f"Opened URL via Termux: {url}")
            else:
                logger.warning(f"Failed to open URL via Termux: {url}")
            return success
        else:
            # Use standard webbrowser module
            success = webbrowser.open(url)
            if success:
                logger.debug(f"Opened URL in browser: {url}")
            else:
                logger.warning(f"Failed to open URL: {url}")
            return success
    except Exception as e:
        logger.error(f"Error opening URL: {e}")
        return False


__all__: list[str] = [
    "open_url",
]
