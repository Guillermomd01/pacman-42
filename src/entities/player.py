"""Player entity for Pac-Man."""

from typing import Tuple

from level import Level


class Player:
    """Represents the Pac-Man player character."""

    def __init__(self, grid_x: int, grid_y: int, lives: int = 3) -> None:
        """Initialize the player at the given grid coordinates.

        Args:
            grid_x: Initial X position in grid coordinates.
            grid_y: Initial Y position in grid coordinates.
            lives: Starting number of lives (default 3).
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.direction = "right"
        self.next_direction = ""
        self.lives = lives
        self.alive = True

    def set_direction(self, direction: str) -> None:
        """Queue a direction change.

        The direction will be applied on the next update if valid.

        Args:
            direction: One of 'up', 'down', 'left', 'right'.
        """
        if direction in ("up", "down", "left", "right"):
            self.next_direction = direction

    def update(self, level: Level) -> None:
        """Update player position based on queued direction and level walls.

        Args:
            level: Level instance providing can_move() method.
        """
        # Try to switch to queued direction immediately
        if self.next_direction and level.can_move(
            self.grid_x, self.grid_y, self.next_direction
        ):
            self.direction = self.next_direction
            self.next_direction = ""

        # Continue moving in current direction if possible
        if level.can_move(self.grid_x, self.grid_y, self.direction):
            dx, dy, _ = {
                "up": (0, -1, 0),
                "down": (0, 1, 0),
                "left": (-1, 0, 0),
                "right": (1, 0, 0),
            }[self.direction]
            self.grid_x += dx
            self.grid_y += dy

    def get_position(self) -> Tuple[int, int]:
        """Return current grid position.

        Returns:
            Tuple of (x, y) grid coordinates.
        """
        return (self.grid_x, self.grid_y)

    def respawn(self, x: int, y: int) -> None:
        """Respawn the player at a new position.

        Typically called after losing a life.

        Args:
            x: New grid X coordinate.
            y: New grid Y coordinate.
        """
        self.grid_x = x
        self.grid_y = y
        self.direction = "right"
        self.next_direction = ""
        self.alive = True
