"""Rendering utilities for the game."""

from typing import Dict, List, Tuple

import pygame

from level import Level
from entities.player import Player
from entities.ghost import Ghost
from utils.constants import CELL_SIZE, COLORS


class Renderer:
    """Handles all drawing operations for the game."""

    def __init__(self, screen: pygame.Surface) -> None:
        """Initialize renderer with a Pygame surface.

        Args:
            screen: The main display surface.
        """
        self.screen = screen

    def _cell_rect(self, x: int, y: int) -> pygame.Rect:
        """Return a pixel rectangle for a grid cell.

        Args:
            x: Grid X coordinate.
            y: Grid Y coordinate.

        Returns:
            Pygame Rect in screen pixels.
        """
        return pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

    def _draw_walls(self, grid: List[List[int]],
                    width: int, height: int) -> None:
        """Draw maze walls as lines based on bitmask data.

        Args:
            grid: Maze grid with wall bitmasks.
            width: Maze width in cells.
            height: Maze height in cells.
        """
        wall_color = COLORS["wall"]
        thickness = 6
        for y in range(height):
            for x in range(width):
                cell = grid[y][x]
                rect = self._cell_rect(x, y)
                cx, cy = rect.centerx, rect.centery
                half = CELL_SIZE // 2

                # North wall
                if cell & 1:
                    pygame.draw.line(
                        self.screen, wall_color,
                        (cx - half, cy - half),
                        (cx + half, cy - half),
                        thickness
                    )
                # East wall
                if cell & 2:
                    pygame.draw.line(
                        self.screen, wall_color,
                        (cx + half, cy - half),
                        (cx + half, cy + half),
                        thickness
                    )
                # South wall
                if cell & 4:
                    pygame.draw.line(
                        self.screen, wall_color,
                        (cx - half, cy + half),
                        (cx + half, cy + half),
                        thickness
                    )
                # West wall
                if cell & 8:
                    pygame.draw.line(
                        self.screen, wall_color,
                        (cx - half, cy - half),
                        (cx - half, cy + half),
                        thickness
                    )

    def _draw_items(self, items: Dict[Tuple[int, int], str]) -> None:
        """Draw pacgums and super-pacgums.

        Args:
            items: Dictionary mapping positions to item types.
        """
        for (x, y), item_type in items.items():
            rect = self._cell_rect(x, y)
            center = rect.center
            if item_type == "pacgum":
                pygame.draw.circle(
                    self.screen, COLORS["pacgum"],
                    center, CELL_SIZE // 6
                )
            elif item_type == "super_pacgum":
                pygame.draw.circle(
                    self.screen, COLORS["super_pacgum"],
                    center, CELL_SIZE // 3
                )

    def _draw_player(self, player: Player) -> None:
        """Draw the player character.

        Args:
            player: Player instance.
        """
        x, y = player.get_position()
        rect = self._cell_rect(x, y)
        center = rect.center
        radius = CELL_SIZE // 2 - 2
        pygame.draw.circle(self.screen, COLORS["player"], center, radius)

    def _draw_ghost(self, ghost: Ghost) -> None:
        """Draw a ghost character.

        Args:
            ghost: Ghost instance.
        """
        x, y = ghost.get_position()
        rect = self._cell_rect(x, y)
        center = rect.center
        radius = CELL_SIZE // 2 - 2
        if ghost.state == "chase":
            color = COLORS["ghost_chase"]
        elif ghost.state == "frightened":
            color = COLORS["ghost_frightened"]
        elif ghost.state == "eyes":
            color = COLORS["ghost_eyes"]
        else:
            color = COLORS["ghost"]
        pygame.draw.circle(self.screen, color, center, radius)

    def render_level(self, level: Level, player: Player) -> None:
        """Render the complete game scene.

        Args:
            level: Current level with maze and items.
            player: Player instance.
        """
        self.screen.fill(COLORS["background"])
        self._draw_walls(
            level.data.grid, level.data.width, level.data.height
        )
        self._draw_items(level.items)
        self._draw_player(player)
