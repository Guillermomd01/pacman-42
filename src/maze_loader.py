"""Adapter for the external A-Maze-ing package (mazegenerator)."""

import logging
from dataclasses import dataclass
from typing import List, Tuple

from mazegenerator.mazegenerator import MazeGenerator

logger = logging.getLogger(__name__)


@dataclass
class LevelData:
    """Data representing a single game level."""

    grid: List[List[int]]
    width: int
    height: int
    player_start: Tuple[int, int]
    ghost_starts: List[Tuple[int, int]]
    items: dict[Tuple[int, int], str]


def _find_center_open_cell(grid: List[List[int]],
                           width: int, height: int) -> Tuple[int, int]:
    """Find a suitable central cell for the player.

    Starts at the exact center and spirals outward looking for a
    cell that is not completely enclosed.

    Args:
        grid: Maze grid with wall bitmasks.
        width: Maze width.
        height: Maze height.

    Returns:
        Grid coordinates (x, y) for the player start.
    """
    cx = width // 2
    cy = height // 2
    # Spiral search
    for radius in range(max(width, height)):
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < width and 0 <= y < height:
                    if grid[y][x] != 15:  # Not fully enclosed
                        return (x, y)
    # Fallback to entry point
    return (0, 0)


def _place_items(grid: List[List[int]],
                 width: int, height: int,
                 player_start: Tuple[int, int],
                 ghost_starts: List[Tuple[int, int]]) -> dict[Tuple[int, int], str]:
    """Place pacgums and super-pacgums on the maze.

    Args:
        grid: Maze grid.
        width: Maze width.
        height: Maze height.
        player_start: Player starting position.
        ghost_starts: Ghost starting positions.

    Returns:
        Dictionary mapping position tuples to item type strings.
    """
    items: dict[Tuple[int, int], str] = {}
    blocked = {player_start} | set(ghost_starts)

    corners = [
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
    ]

    for pos in corners:
        if pos not in blocked:
            items[pos] = "super_pacgum"
            blocked.add(pos)

    for y in range(height):
        for x in range(width):
            pos = (x, y)
            if pos in blocked:
                continue
            items[pos] = "pacgum"

    return items


def load_level(width: int, height: int, seed: int) -> LevelData:
    """Generate a level using the external maze generator.

    Args:
        width: Maze width (should be odd for best results).
        height: Maze height (should be odd for best results).
        seed: Random seed for reproducibility.

    Returns:
        Populated LevelData instance.
    """
    try:
        generator = MazeGenerator(
            size=(width, height),
            perfect=False,
            seed=seed,
        )
        grid = generator.maze
    except Exception as exc:
        logger.error(f"Maze generation failed: {exc}")
        raise RuntimeError(f"Failed to generate maze: {exc}") from exc

    actual_height = len(grid)
    actual_width = len(grid[0]) if grid else 0

    player_start = _find_center_open_cell(grid, actual_width, actual_height)
    ghost_starts = [
        (0, 0),
        (actual_width - 1, 0),
        (0, actual_height - 1),
        (actual_width - 1, actual_height - 1),
    ]

    items = _place_items(grid, actual_width, actual_height,
                         player_start, ghost_starts)

    return LevelData(
        grid=grid,
        width=actual_width,
        height=actual_height,
        player_start=player_start,
        ghost_starts=ghost_starts,
        items=items,
    )
