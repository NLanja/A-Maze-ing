"""
Maze generator with 42 pattern support.
"""

import random
from config import MazeConfig
NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8

ALL_WALLS: int = NORTH | EAST | SOUTH | WEST

# Pattern "42" - 1 = wall closed, 0 = wall open
PATTERN_42: list[list[int]] = [
    [1, 0, 1, 0, 1, 1, 1],
    [1, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 1, 1],
]

OPPOSITE: dict[int, int] = {
    NORTH: SOUTH,
    EAST: WEST,
    SOUTH: NORTH,
    WEST: EAST,
}

DIRECTION: dict[int, tuple[int, int]] = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0),
}


class MazeGenerator:
    """
    Generates a maze using recursive backtracker (DFS).

    Supports:
        - Perfect maze (single path)
        - Seed for reproducibility
        - 42 pattern with closed cells
        - Error message if pattern cannot be placed
    """

    def __init__(
            self,
            config: MazeConfig
            ) -> None:
        """
        Initialize maze generator.

        Args:
            width: Number of cells horizontally
            height: Number of cells vertically
            seed: Optional seed for reproducibility
        """
        self.config = config
        self.width = config.width
        self.height = config.height
        self.seed = config.seed
        self.pattern_placed = False
        self.grid = [
            [ALL_WALLS for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def generate(self) -> None:
        """Generates the maze using DFS."""
        if self.seed is not None:
            random.seed(self.seed)

        visited: list[list[bool]] = [
            [False for _ in range(self.width)]
            for _ in range(self.height)
        ]

        # 1. Draw 42 pattern if maze is large enough
        if self._can_place_42():
            self._draw_42(visited)
            self.pattern_placed = True
            print(
                f"42 pattern placed successfully ("
                f"{self.width}x{self.height})")
        else:
            self.pattern_placed = False
            print(
                f"Error: 42 pattern omitted - maze "
                f"{self.width}x{self.height}"
                "is too small (need at least 12x10)")

        # 2. Launch DFS from entry (0,0)
        self._dfs(0, 0, visited)

    def _can_place_42(self) -> bool:
        """
        Check if the 42 pattern can fit in the maze.

        The pattern is 7x5. We need margins so it doesn't block entry/exit.
        Minimum recommended size: 12x10.

        Returns:
            True if pattern can be placed, False otherwise
        """
        # Le sujet dit : "peut être omis si la taille ne le permet pas"
        # On met un seuil à 12x10 pour être sûr que le chemin fonctionne
        return self.width >= 12 and self.height >= 10

    def _draw_42(self, visited: list[list[bool]]) -> None:
        """
        Draws the 42 pattern in the maze center.

        Pattern cells are completely closed (ALL_WALLS).

        Args:
            visited: grid of visited cells to mark pattern cells
        """
        pattern_h = len(PATTERN_42)
        pattern_w = len(PATTERN_42[0])

        # Center the pattern
        start_x = (self.width - pattern_w) // 2
        start_y = (self.height - pattern_h) // 2

        # Ensure pattern stays within bounds
        if start_x < 0:
            start_x = 0
        if start_y < 0:
            start_y = 0

        # Draw the pattern
        for row in range(pattern_h):
            for col in range(pattern_w):
                if PATTERN_42[row][col] == 1:
                    x = start_x + col
                    y = start_y + row
                    if self.config.entry != (x, y) and \
                            self.config.exit != (x, y):
                        if 0 <= x < self.width and 0 <= y < self.height:
                            self.grid[y][x] = ALL_WALLS
                            visited[y][x] = True
                    else:
                        raise Exception(
                            "Error: 42 pattern overlaps with entry or exit "
                            "point.")

    def _dfs(self, x: int, y: int, visited: list[list[bool]]) -> None:
        """
        Explores the maze recursively using DFS.

        Args:
            x: Current cell column
            y: Current cell row
            visited: Grid of already visited cells
        """
        visited[y][x] = True

        directions = list(DIRECTION.keys())
        random.shuffle(directions)

        for direction in directions:
            dx, dy = DIRECTION[direction]
            nx = x + dx
            ny = y + dy

            if self._in_bounds(nx, ny) and not visited[ny][nx]:
                self._remove_wall(x, y, nx, ny, direction)
                self._dfs(nx, ny, visited)

    def _in_bounds(self, x: int, y: int) -> bool:
        """Checks if coordinates are inside the grid."""
        return 0 <= x < self.width and 0 <= y < self.height

    def _remove_wall(
            self,
            x: int,
            y: int,
            nx: int,
            ny: int,
            direction: int) -> None:
        """
        Opens the wall between two neighboring cells.

        Args:
            x: Current cell column
            y: Current cell row
            nx: Neighbor cell column
            ny: Neighbor cell row
            direction: Direction toward the neighbor
        """
        # Open wall on current cell side
        self.grid[y][x] &= ~direction

        # Open opposite wall on neighbor side
        self.grid[ny][nx] &= ~OPPOSITE[direction]
