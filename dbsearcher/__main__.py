"""
databaseSnake CLI entry point.

This module provides the command-line interface entry point for the
databaseSnake application.
"""

import sys
import typing

import dbsearcher.constants
import dbsearcher.logging
import dbsearcher.ui.menu
import dbsearcher.utils.filesystem


def main() -> int:
    """
    Main entry point for databaseSnake.

    Returns
    -------
    int
        Exit code (0 for success, non-zero for errors).
    """
    logger: dbsearcher.logging.DBSearcherLogger = dbsearcher.logging.get_logger()

    try:
        # Ensure base directory exists
        base_path: typing.Final = dbsearcher.constants.BASE_DIR
        created: bool = dbsearcher.utils.filesystem.ensure_directory(base_path)
        if created:
            logger.info(f"Created '{base_path}' directory")

        # Run main menu
        menu: dbsearcher.ui.menu.MainMenu = dbsearcher.ui.menu.MainMenu()
        return menu.run()

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 0
    except Exception as e:
        logger.critical(f"Fatal error: {e}", extra={"error": str(e)})
        return 1


if __name__ == "__main__":
    sys.exit(main())
