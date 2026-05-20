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
    for radius in range(max(width, height)):
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < width and 0 <= y < height:
                    if grid[y][x] != 15:
                        return (x, y)
    return (0, 0)


def _find_accessible_near(grid: List[List[int]],
                          width: int, height: int,
                          start_x: int, start_y: int,
                          blocked: set[Tuple[int, int]]) -> Tuple[int, int] | None:
    """Find the nearest accessible cell that is not blocked.

    Searches in a spiral pattern from the starting position.

    Args:
        grid: Maze grid with wall bitmasks.
        width: Maze width.
        height: Maze height.
        start_x: Starting X coordinate.
        start_y: Starting Y coordinate.
        blocked: Set of blocked positions to avoid.

    Returns:
        Nearest accessible grid coordinate, or None if none found.
    """
    if (0 <= start_x < width and 0 <= start_y < height
            and grid[start_y][start_x] != 15
            and (start_x, start_y) not in blocked):
        return (start_x, start_y)

    for radius in range(1, max(width, height)):
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x, y = start_x + dx, start_y + dy
                if 0 <= x < width and 0 <= y < height:
                    if grid[y][x] != 15 and (x, y) not in blocked:
                        return (x, y)
    return None


def _place_items(
    grid: List[List[int]], width: int, height: int,
    player_start: Tuple[int, int]
) -> Tuple[dict[Tuple[int, int], str], List[Tuple[int, int]]]:
    """Place pacgums, super-pacgums, and ghost spawns on the maze.

    Super-pacgums are placed at the corners (or nearest accessible cell).
    Ghosts are placed at cells adjacent to corners.

    Args:
        grid: Maze grid.
        width: Maze width.
        height: Maze height.
        player_start: Player starting position.

    Returns:
        Tuple of (items dictionary, ghost_starts list).
    """
    items: dict[Tuple[int, int], str] = {}
    blocked: set[Tuple[int, int]] = {player_start}

    corners = [
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
    ]

    ghost_starts: List[Tuple[int, int]] = []

    for corner in corners:
        # Place super-pacgum at corner or nearest accessible cell
        sp_pos = _find_accessible_near(
            grid, width, height, corner[0], corner[1], blocked
        )
        if sp_pos:
            items[sp_pos] = "super_pacgum"
            blocked.add(sp_pos)

        # Place ghost at a cell adjacent to the corner
        ghost_pos = None
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = corner[0] + dx, corner[1] + dy
            if 0 <= nx < width and 0 <= ny < height:
                if grid[ny][nx] != 15 and (nx, ny) not in blocked:
                    ghost_pos = (nx, ny)
                    break

        if ghost_pos is None:
            # Fallback: search in spiral from corner
            ghost_pos = _find_accessible_near(
                grid, width, height, corner[0], corner[1], blocked
            )

        if ghost_pos:
            ghost_starts.append(ghost_pos)
            blocked.add(ghost_pos)

    # Fill remaining accessible cells with pacgums
    for y in range(height):
        for x in range(width):
            pos = (x, y)
            if pos in blocked:
                continue
            if grid[y][x] != 15:
                items[pos] = "pacgum"

    return items, ghost_starts


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

    items, ghost_starts = _place_items(
        grid, actual_width, actual_height, player_start
    )

    return LevelData(
        grid=grid,
        width=actual_width,
        height=actual_height,
        player_start=player_start,
        ghost_starts=ghost_starts,
        items=items,
    )
