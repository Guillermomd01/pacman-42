"""Game constants and configuration values."""

from typing import Final

# Window and grid settings
CELL_SIZE: Final[int] = 40
FPS: Final[int] = 60
WINDOW_TITLE: Final[str] = "Pac-Man"

# Timing
PLAYER_MOVE_INTERVAL_MS: Final[int] = 150  # ms between grid moves

# Colors (RGB)
COLORS: Final[dict[str, tuple[int, int, int]]] = {
    "background": (0, 0, 0),
    "wall": (33, 33, 222),
    "player": (255, 255, 0),
    "pacgum": (255, 184, 174),
    "super_pacgum": (39, 245, 73),
    "ghost_chase": (255, 0, 0),
    "ghost_frightened": (0, 0, 255),
    "ghost_eyes": (255, 255, 255),
    "ghost": (255, 0, 0),
    "text": (255, 255, 255),
}

# Bit masks for maze walls (from mazegenerator format)
WALL_NORTH: Final[int] = 1
WALL_EAST: Final[int] = 2
WALL_SOUTH: Final[int] = 4
WALL_WEST: Final[int] = 8

# Direction vectors and associated wall bits
DIRECTIONS: Final[dict[str, tuple[int, int, int]]] = {
    "up": (0, -1, WALL_NORTH),
    "down": (0, 1, WALL_SOUTH),
    "left": (-1, 0, WALL_WEST),
    "right": (1, 0, WALL_EAST),
}
