"""Level logic: movement validation, item collection, and state."""

from typing import Dict, Tuple

from maze_loader import LevelData
from utils.constants import DIRECTIONS


class Level:
    """Represents a playable level with maze data and items."""

    def __init__(self, data: LevelData) -> None:
        """Initialize level from generated data.

        Args:
            data: LevelData containing grid, items, and spawn points.
        """
        self.data = data
        self.items: Dict[Tuple[int, int], str] = data.items.copy()
        self.score = 0
        self.pacgums_eaten = 0

    def can_move(self, x: int, y: int, direction: str) -> bool:
        """Check if an entity can move from (x, y) in the given direction.

        Args:
            x: Current grid X coordinate.
            y: Current grid Y coordinate.
            direction: One of 'up', 'down', 'left', 'right'.

        Returns:
            True if the move is valid (no wall blocking).
        """
        if direction not in DIRECTIONS:
            return False
        dx, dy, wall_bit = DIRECTIONS[direction]
        nx = x + dx
        ny = y + dy
        if not (0 <= nx < self.data.width and 0 <= ny < self.data.height):
            return False
        # Check wall on current cell for that direction
        if self.data.grid[y][x] & wall_bit:
            return False
        return True

    def collect_item(self, x: int, y: int) -> str | None:
        """Collect an item at the given position if present.

        Args:
            x: Grid X coordinate.
            y: Grid Y coordinate.

        Returns:
            The item type string if collected, else None.
        """
        pos = (x, y)
        item = self.items.pop(pos, None)
        if item == "pacgum":
            self.pacgums_eaten += 1
        return item

    def is_complete(self) -> bool:
        """Check if all pacgums and super-pacgums have been eaten.

        Returns:
            True when no items remain on the level.
        """
        return len(self.items) == 0

    def get_remaining_items(self) -> int:
        """Return the number of remaining collectable items.

        Returns:
            Count of items still on the board.
        """
        return len(self.items)
