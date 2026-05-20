"""Ghost entity for Pac-Man."""

from typing import Final, Tuple
import pygame
from level import Level
GHOST_MOVE_INTERVAL_MS: Final[int] = 600


class Ghost:
    """Represents a ghost enemy in the game."""

    def __init__(self, grid_x: int, grid_y: int,
                 spawn_point: Tuple[int, int]) -> None:
        """Initialize the ghost at the given grid coordinates.

        Args:
            grid_x: Initial X position in grid coordinates.
            grid_y: Initial Y position in grid coordinates.
            spawn_point: The location where the ghost will spawn.
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.spawn_point = spawn_point
        self.direction = "left"
        self.state = "chase"
        self.alive = True
        self.last_move_time = 0
        self.frightened_time = 0

    def get_position(self) -> Tuple[int, int]:
        """Return current grid position.

        Returns:
            Tuple of (x, y) grid coordinates.
        """
        return (self.grid_x, self.grid_y)

    def update(self, level: Level,
               player_pos: Tuple[int, int]) -> None:
        """Update ghost position based on current state and level walls.

        Args:
            level: Level instance providing can_move() method.
            player_pos: Tuple of player's current grid position (x, y).
        """
        time_to_move = (pygame.time.get_ticks() - self.last_move_time
                        >= GHOST_MOVE_INTERVAL_MS)
        if not time_to_move:
            return

        if self.state == "chase":
            posible_direction = self._choose_direction_manhattan_chase(
                level, player_pos
            )
        elif self.state == "frightened":
            posible_direction = self._choose_direction_manhattan_frightened(
                level, player_pos
            )
        elif self.state == "eyes":
            posible_direction = self._choose_direction_manhattan_eyes(
                level, self.spawn_point
            )
        else:
            posible_direction = self.direction

        if level.can_move(self.grid_x, self.grid_y, posible_direction):
            if posible_direction == "up":
                self.grid_y -= 1
                self.direction = "up"
            elif posible_direction == "down":
                self.grid_y += 1
                self.direction = "down"
            elif posible_direction == "left":
                self.grid_x -= 1
                self.direction = "left"
            elif posible_direction == "right":
                self.grid_x += 1
                self.direction = "right"
        if self.state == "eyes" and (self.grid_x, self.grid_y) == self.spawn_point:
            self.state = "chase"
        self.last_move_time = pygame.time.get_ticks()

    def respawn(self) -> None:
        """Respawn the ghost at its spawn point."""
        self.grid_x, self.grid_y = self.spawn_point
        self.state = "chase"
        self.alive = True

    def _get_valid_moves(self, level: Level) -> list[str]:
        """Return valid directions from the current position.

        Filters out the opposite direction unless it is the only way.

        Args:
            level: Current level instance.

        Returns:
            List of valid direction strings.
        """
        valid_moves: list[str] = []
        opposites = {
            "up": "down", "down": "up",
            "left": "right", "right": "left"
        }

        if level.can_move(self.grid_x, self.grid_y, "up"):
            valid_moves.append("up")
        if level.can_move(self.grid_x, self.grid_y, "down"):
            valid_moves.append("down")
        if level.can_move(self.grid_x, self.grid_y, "left"):
            valid_moves.append("left")
        if level.can_move(self.grid_x, self.grid_y, "right"):
            valid_moves.append("right")

        if len(valid_moves) > 1:
            valid_moves = [
                move for move in valid_moves
                if opposites[move] != self.direction
            ]

        if not valid_moves:
            valid_moves.append(opposites[self.direction])

        return valid_moves

    def _calculate_distances(self, level: Level,
                             target_pos: Tuple[int, int]) -> list[tuple[int, str]]:
        """Calculate Manhattan distances for all valid moves.

        Args:
            level: Current level instance.
            target_pos: Target position to measure distance to.

        Returns:
            List of tuples (distance, direction).
        """
        ghost_x, ghost_y = self.grid_x, self.grid_y
        target_x, target_y = target_pos

        directions = {
            "up": (ghost_x, ghost_y - 1),
            "down": (ghost_x, ghost_y + 1),
            "left": (ghost_x - 1, ghost_y),
            "right": (ghost_x + 1, ghost_y),
        }

        valid_moves = self._get_valid_moves(level)
        distance_moves: list[tuple[int, str]] = []

        for move in valid_moves:
            new_x, new_y = directions[move]
            distance = abs(new_x - target_x) + abs(new_y - target_y)
            distance_moves.append((distance, move))

        return distance_moves

    def _choose_direction_manhattan_chase(self, level: Level,
                                          player_pos: Tuple[int, int]) -> str:
        """Choose direction minimizing distance to the player."""
        distance_moves = self._calculate_distances(level, player_pos)
        distance_moves.sort(key=lambda x: x[0])
        return distance_moves[0][1]

    def _choose_direction_manhattan_frightened(self, level: Level,
                                               player_pos: Tuple[int, int]) -> str:
        """Choose direction maximizing distance to the player."""
        distance_moves = self._calculate_distances(level, player_pos)
        distance_moves.sort(key=lambda x: x[0], reverse=True)
        return distance_moves[0][1]

    def _choose_direction_manhattan_eyes(self, level: Level,
                                         respawn_pos: Tuple[int, int]) -> str:
        """Choose direction minimizing distance to the respawn point."""
        distance_moves = self._calculate_distances(level, respawn_pos)
        distance_moves.sort(key=lambda x: x[0])
        return distance_moves[0][1]
