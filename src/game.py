"""Main game controller and state machine."""

import logging
import sys
from typing import Any

import pygame

from level import Level
from maze_loader import load_level
from entities.player import Player
from renderer import Renderer
from utils.constants import CELL_SIZE, FPS, PLAYER_MOVE_INTERVAL_MS, WINDOW_TITLE
from entities.ghost import Ghost
FRIGHTENED_DURATION_MS = 7000

logger = logging.getLogger(__name__)


class Game:
    """Main game controller handling loop, states, and level progression."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize the game with configuration.

        Args:
            config: Configuration dictionary from load_config().
        """
        self.config = config
        self.running = False
        self.screen: pygame.Surface | None = None
        self.clock: pygame.time.Clock | None = None
        self.renderer: Renderer | None = None

        # Game state
        self.level: Level | None = None
        self.player: Player | None = None
        self.current_level_index = 0
        self.score = 0
        self.lives = config.get("lives", 3)

        # Cheat modes
        self.ghost_frozen = False
        self.player_invincible = False
        self.paused = False

        # Timing
        self.last_move_time = 0

        # Initialize Pygame
        pygame.init()
        self._setup_current_level()

    def _setup_current_level(self) -> None:
        """Load the current level based on config and level index."""
        levels_config = self.config.get("levels", [])
        if not levels_config:
            logger.error("No levels defined in config.")
            sys.exit(1)

        level_cfg = levels_config[self.current_level_index]
        width = level_cfg.get("width", 21)
        height = level_cfg.get("height", 21)
        seed = self.config.get("seed", 42)
        # After first level, use random seed (0 means random in mazegenerator)
        if self.current_level_index > 0:
            seed = 0

        try:
            data = load_level(width, height, seed)
        except Exception as exc:
            logger.error(f"Failed to load level: {exc}")
            print(f"Error: Could not generate level. {exc}")
            sys.exit(1)

        self.level = Level(data)
        self.player = Player(
            data.player_start[0],
            data.player_start[1],
            lives=self.lives
        )
        self.red_ghost = Ghost(
            data.ghost_starts[0][0],
            data.ghost_starts[0][1],
            spawn_point=data.ghost_starts[0]
        )
        self.pink_ghost = Ghost(
            data.ghost_starts[1][0],
            data.ghost_starts[1][1],
            spawn_point=data.ghost_starts[1]
        )
        self.blue_ghost = Ghost(
            data.ghost_starts[2][0],
            data.ghost_starts[2][1],
            spawn_point=data.ghost_starts[2]
        )
        self.orange_ghost = Ghost(
            data.ghost_starts[3][0],
            data.ghost_starts[3][1],
            spawn_point=data.ghost_starts[3]
        )

        window_width = data.width * CELL_SIZE
        window_height = data.height * CELL_SIZE
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        self.last_move_time = pygame.time.get_ticks()

    def run(self) -> None:
        """Main game loop."""
        self.running = True

        while self.running:
            self._handle_events()
            self._update()
            self._render()
            if self.clock:
                self.clock.tick(FPS)

        pygame.quit()
        sys.exit(0)

    def _handle_events(self) -> None:
        """Process input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN and self.player:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.player.set_direction("up")
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.player.set_direction("down")
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player.set_direction("left")
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.set_direction("right")
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_i:
                    print("Mode invencible activated!")
                    self.player_invincible = not self.player_invincible
                elif event.key == pygame.K_n:
                    print("Skipping to next level!")
                    self.current_level_index += 1
                    if self.current_level_index >= len(self.config.get("levels", [])):
                        print("No more levels! Restarting from first level.")
                        self.current_level_index = 0
                    self._setup_current_level()
                elif event.key == pygame.K_f:
                    print("Ghost are frozen!")
                    self.ghost_frozen = not self.ghost_frozen

    def _update(self) -> None:
        """Update game logic (movement, item collection)."""
        if not self.player or not self.level:
            return
        if self.paused:
            return

        now = pygame.time.get_ticks()
        if not self.ghost_frozen:
            self.red_ghost.update(self.level, self.player.get_position())
            self.pink_ghost.update(self.level, self.player.get_position())
            self.blue_ghost.update(self.level, self.player.get_position())
            self.orange_ghost.update(self.level, self.player.get_position())
            if (self.red_ghost.state == "frightened"
                    and now - self.red_ghost.frightened_time
                    >= FRIGHTENED_DURATION_MS):
                self.red_ghost.state = "chase"
            if (self.pink_ghost.state == "frightened"
                    and now - self.pink_ghost.frightened_time
                    >= FRIGHTENED_DURATION_MS):
                self.pink_ghost.state = "chase"
            if (self.blue_ghost.state == "frightened"
                    and now - self.blue_ghost.frightened_time
                    >= FRIGHTENED_DURATION_MS):
                self.blue_ghost.state = "chase"
            if (self.orange_ghost.state == "frightened"
                    and now - self.orange_ghost.frightened_time
                    >= FRIGHTENED_DURATION_MS):
                self.orange_ghost.state = "chase"
        if now - self.last_move_time < PLAYER_MOVE_INTERVAL_MS:
            return
        self.last_move_time = now

        self.player.update(self.level)

        # Check collisions with ghosts
        player_pos = self.player.get_position()
        if ((player_pos == self.red_ghost.get_position()
             and self.red_ghost.state == "chase")
                or (player_pos == self.pink_ghost.get_position()
                    and self.pink_ghost.state == "chase")
                or (player_pos == self.blue_ghost.get_position()
                    and self.blue_ghost.state == "chase")
                or (player_pos == self.orange_ghost.get_position()
                    and self.orange_ghost.state == "chase")):
            if not self.player_invincible:
                self.lives -= 1
                self.player.respawn(
                    self.level.data.player_start[0],
                    self.level.data.player_start[1]
                )
                self.red_ghost.respawn()
                self.pink_ghost.respawn()
                self.blue_ghost.respawn()
                self.orange_ghost.respawn()
                print(f"Player hit by ghost! Lives remaining: {self.lives}")
                if self.lives <= 0:
                    print(f"Game Over! Final Score: {self.score}")
                    self.running = False
        elif (player_pos == self.red_ghost.get_position()
              and self.red_ghost.state == "frightened"):
            self.score += self.config.get("points_per_ghost", 200)
            self.red_ghost.state = "eyes"
            print(f"Red ghost eaten! Score: {self.score}")
        elif (player_pos == self.pink_ghost.get_position()
              and self.pink_ghost.state == "frightened"):
            self.score += self.config.get("points_per_ghost", 200)
            self.pink_ghost.state = "eyes"
            print(f"Pink ghost eaten! Score: {self.score}")
        elif (player_pos == self.blue_ghost.get_position()
              and self.blue_ghost.state == "frightened"):
            self.score += self.config.get("points_per_ghost", 200)
            self.blue_ghost.state = "eyes"
            print(f"Blue ghost eaten! Score: {self.score}")
        elif (player_pos == self.orange_ghost.get_position()
              and self.orange_ghost.state == "frightened"):
            self.score += self.config.get("points_per_ghost", 200)
            self.orange_ghost.state = "eyes"
            print(f"Orange ghost eaten! Score: {self.score}")

        # Collect items
        px, py = self.player.get_position()
        item = self.level.collect_item(px, py)
        if item == "pacgum":
            self.score += self.config.get("points_per_pacgum", 10)
        elif item == "super_pacgum":
            self.score += self.config.get("points_per_super_pacgum", 50)
            self.red_ghost.state = "frightened"
            self.pink_ghost.state = "frightened"
            self.blue_ghost.state = "frightened"
            self.orange_ghost.state = "frightened"
            self.red_ghost.frightened_time = pygame.time.get_ticks()
            self.pink_ghost.frightened_time = pygame.time.get_ticks()
            self.blue_ghost.frightened_time = pygame.time.get_ticks()
            self.orange_ghost.frightened_time = pygame.time.get_ticks()

        # Check level completion
        if self.level.is_complete():
            print(f"Level complete! Score: {self.score}")
            # For Phase 1, just stop or restart
            self.running = False

    def _render(self) -> None:
        """Render the current frame."""
        if self.renderer and self.level and self.player:
            self.renderer.render_level(self.level, self.player)
            self.renderer._draw_ghost(self.red_ghost)
            self.renderer._draw_ghost(self.pink_ghost)
            self.renderer._draw_ghost(self.blue_ghost)
            self.renderer._draw_ghost(self.orange_ghost)
            pygame.display.flip()
