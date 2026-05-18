#!/usr/bin/env python3
"""Entry point for the Pac-Man game.

Usage:
    python3 pac-man.py <config_file.json>
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import load_config  # noqa: E402
from game import Game  # noqa: E402


def main() -> None:
    """Parse CLI args and launch the game."""
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config_file.json>")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    config = load_config(config_path)

    try:
        game = Game(config)
        game.run()
    except Exception as exc:
        logging.error(f"Fatal error: {exc}")
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
