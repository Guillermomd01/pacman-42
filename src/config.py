"""Configuration loader with comment support and safe defaults."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_CONFIG: dict[str, Any] = {
    "highscore_filename": "highscores.json",
    "lives": 3,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90,
    "levels": [{"width": 21, "height": 21}],
}


def _strip_comments(text: str) -> str:
    """Remove lines starting with # (allowing leading whitespace).

    Args:
        text: Raw file content.

    Returns:
        Clean text without comment lines.
    """
    lines = [line for line in text.splitlines()
             if not line.strip().startswith("#")]
    return "\n".join(lines)


def _validate_and_merge(user: dict[str, Any],
                        base: dict[str, Any]) -> dict[str, Any]:
    """Merge user config into base, validating types.

    Args:
        user: Parsed user configuration.
        base: Default configuration.

    Returns:
        Merged configuration dictionary.
    """
    result = base.copy()
    for key, value in user.items():
        if key not in base:
            logger.info(f"Ignoring unknown config key: {key}")
            continue
        expected_type = type(base[key])
        if isinstance(value, expected_type):
            result[key] = value
        else:
            logger.warning(
                f"Invalid type for '{key}': expected "
                f"{expected_type.__name__}, got {type(value).__name__}. "
                f"Using default."
            )
    return result


def load_config(path: Path) -> dict[str, Any]:
    """Load a JSON config file, stripping comments and applying defaults.

    On missing file, invalid JSON, or type mismatches, logs a clear
    message and returns safe defaults.

    Args:
        path: Path to the JSON configuration file.

    Returns:
        A dictionary with merged configuration values.
    """
    if not path.exists():
        logger.warning(f"Config file not found: {path}. Using defaults.")
        return DEFAULT_CONFIG.copy()

    try:
        raw_text = path.read_text(encoding="utf-8")
        clean_text = _strip_comments(raw_text)
        user_config = json.loads(clean_text)
    except json.JSONDecodeError as exc:
        logger.warning(f"Invalid JSON in config file: {exc}. Using defaults.")
        return DEFAULT_CONFIG.copy()
    except Exception as exc:
        logger.warning(f"Error reading config: {exc}. Using defaults.")
        return DEFAULT_CONFIG.copy()

    if not isinstance(user_config, dict):
        logger.warning("Config root is not a JSON object. Using defaults.")
        return DEFAULT_CONFIG.copy()

    return _validate_and_merge(user_config, DEFAULT_CONFIG)
