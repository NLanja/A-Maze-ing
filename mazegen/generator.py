import random
from typing import Optional

NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8

ALL_WALLS: int = NORTH | EAST | SOUTH | WEST

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
    EAST:  (1,  0),
    SOUTH: (0,  1),
    WEST:  (-1, 0),
}


class MazeGenerator:
    def __init__(self, width: int,
                 height: int, seed: Optional[int] = None) -> None:
        self.width = width
        self.height = height
        self.seed = seed
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
        # 1. Draw 42 pattern first
        self._draw_42(visited)

        # 2. Launch DFS (avoids 42 cells)
        self._dfs(0, 0, visited)

    def _dfs(
        self,
        x: int,
        y: int,
        visited: list[list[bool]],
    ) -> None:
        """Explores the maze recursively using DFS.

        Args:
            x: current cell column.
            y: current cell row.
            visited: grid of already visited cells.
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
        if x < 0 or x >= self.width:
            return False
        if y < 0 or y >= self.height:
            return False
        return True

    def _draw_42(self, visited: list[list[bool]]) -> None:
        """Draws the 42 pattern in the maze center.

    Args:
        visited: grid of visited cells to mark 42 cells.
    """
        start_x = (self.width - 7) // 2
        start_y = (self.height - 5) // 2

        for row in range(5):
            for col in range(7):
                if PATTERN_42[row][col] == 1:
                    x = start_x + col
                    y = start_y + row
                    self.grid[y][x] = ALL_WALLS
                    visited[y][x] = True

    def _remove_wall(
        self,
        x: int,
        y: int,
        nx: int,
        ny: int,
        direction: int,
    ) -> None:
        """Opens the wall between two neighboring cells.

        Args:
            x: current cell column.
            y: current cell row.
            nx: neighbor cell column.
            ny: neighbor cell row.
            direction: direction toward the neighbor.
        """
        # Open wall on current cell side
        self.grid[y][x] &= ~direction

        # Open opposite wall on neighbor side
        self.grid[ny][nx] &= ~OPPOSITE[direction]
