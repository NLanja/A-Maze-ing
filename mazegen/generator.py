"""
Generate mazes with 42 pattern support.

Provide DFS generation and optional maze patterns.
"""

import random
from config import MazeConfig
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
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0),
}


class MazeGenerator:
    """
    Generate a maze using recursive backtracker (DFS).

    Supports:
        - Perfect maze (single path) or braided maze (loops) depending
          on config.perfect
        - Seed for reproducibility
        - 42 pattern with closed cells
        - Error message if pattern cannot be placed
    """

    BRAID_RATIO: float = 0.12

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
        self.steps: list[tuple[int, int, int, int, int]] = []
        self._recording = True

    def generate(self) -> None:
        """Generate the maze using DFS."""
        if self.seed is not None:
            random.seed(self.seed)

        visited: list[list[bool]] = [
            [False for _ in range(self.width)]
            for _ in range(self.height)
        ]

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

        self._dfs(0, 0, visited)

        if not self.config.perfect:
            self._recording = False
            self._braid()
            self._recording = True

    def _can_place_42(self) -> bool:
        """
        Check if the 42 pattern can fit in the maze.

        The pattern is 7x5. We need margins so it doesn't block entry/exit.
        Minimum recommended size: 12x10.

        Returns:
            True if pattern can be placed, False otherwise
        """
        return self.width >= 12 and self.height >= 10

    def _draw_42(self, visited: list[list[bool]]) -> None:
        """
        Draw the 42 pattern in the maze center.

        Pattern cells are completely closed (ALL_WALLS).

        Args:
            visited: grid of visited cells to mark pattern cells
        """
        pattern_h = len(PATTERN_42)
        pattern_w = len(PATTERN_42[0])

        start_x = (self.width - pattern_w) // 2
        start_y = (self.height - pattern_h) // 2

        if start_x < 0:
            start_x = 0
        if start_y < 0:
            start_y = 0

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
        Explore the maze using an iterative recursive-backtracker.

        Use an explicit stack instead of real recursion to avoid
        RecursionError on large mazes.

        Args:
            x: Starting cell column
            y: Starting cell row
            visited: Grid of already visited cells
        """
        visited[y][x] = True
        start_directions = list(DIRECTION.keys())
        random.shuffle(start_directions)
        start_directions.reverse()
        stack: list[tuple[int, int, list[int]]] = [(x, y, start_directions)]

        while stack:
            cx, cy, remaining = stack[-1]
            advanced = False

            while remaining:
                direction = remaining.pop()
                dx, dy = DIRECTION[direction]
                nx, ny = cx + dx, cy + dy

                if self._in_bounds(nx, ny) and not visited[ny][nx]:
                    self._remove_wall(cx, cy, nx, ny, direction)
                    visited[ny][nx] = True
                    next_directions = list(DIRECTION.keys())
                    random.shuffle(next_directions)
                    next_directions.reverse()
                    stack.append((nx, ny, next_directions))
                    advanced = True
                    break

            if not advanced:
                stack.pop()

    def _braid(self) -> None:
        """Punche extra loops into the perfect maze (PERFECT=False).

        Picks a random subset of the walls that are still closed
        between two non-pattern cells and opens them, as long as doing
        so does not create a fully-open 3x3 area (corridors must stay
        at most 2 cells wide, per the subject's requirements). '42'
        pattern cells are never touched: they must stay isolated.
        """
        candidates: list[tuple[int, int, int, int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == ALL_WALLS:
                    continue
                for direction, (dx, dy) in DIRECTION.items():
                    nx, ny = x + dx, y + dy
                    if not self._in_bounds(nx, ny):
                        continue
                    if self.grid[ny][nx] == ALL_WALLS:
                        continue
                    if self.grid[y][x] & direction:
                        candidates.append((x, y, nx, ny, direction))

        random.shuffle(candidates)
        target = int(len(candidates) * self.BRAID_RATIO)

        opened = 0
        for x, y, nx, ny, direction in candidates:
            if opened >= target:
                break
            if not (self.grid[y][x] & direction):
                continue
            if self._try_open_wall(x, y, nx, ny, direction):
                opened += 1

    def _try_open_wall(
            self,
            x: int,
            y: int,
            nx: int,
            ny: int,
            direction: int) -> bool:
        """Open a wall only if it doesn't create a 3x3 open area.

        Args:
            x: current cell column.
            y: current cell row.
            nx: neighbour cell column.
            ny: neighbour cell row.
            direction: direction from (x, y) toward (nx, ny).

        Returns:
            True if the wall was opened, False if it was rejected (and
            left untouched) because it would create too wide a corridor.
        """
        self._remove_wall(x, y, nx, ny, direction)

        if self._has_3x3_open_area(x, y) or self._has_3x3_open_area(nx, ny):
            self.grid[y][x] |= direction
            self.grid[ny][nx] |= OPPOSITE[direction]
            return False
        return True

    def _has_3x3_open_area(self, x: int, y: int) -> bool:
        """Check whether any 3x3 window around (x, y) is fully open.

        Args:
            x: column of a cell that was just modified.
            y: row of a cell that was just modified.

        Returns:
            True if a 3x3 block of cells exists with every internal
            wall open (forbidden by the subject), False otherwise.
        """
        for top_y in range(max(0, y - 2), min(y, self.height - 3) + 1):
            for top_x in range(max(0, x - 2), min(x, self.width - 3) + 1):
                if self._window_fully_open(top_x, top_y):
                    return True
        return False

    def _window_fully_open(self, top_x: int, top_y: int) -> bool:
        """Check if every internal wall in a 3x3 window is open.

        Args:
            top_x: column of the window's top-left cell.
            top_y: row of the window's top-left cell.

        Returns:
            True if all 12 internal East/South edges within the 3x3
            block starting at (top_x, top_y) are open.
        """
        for yy in range(top_y, top_y + 3):
            for xx in range(top_x, top_x + 2):
                if self.grid[yy][xx] & EAST:
                    return False
        for yy in range(top_y, top_y + 2):
            for xx in range(top_x, top_x + 3):
                if self.grid[yy][xx] & SOUTH:
                    return False
        return True

    def _in_bounds(self, x: int, y: int) -> bool:
        """Check if coordinates are inside the grid."""
        return 0 <= x < self.width and 0 <= y < self.height

    def _remove_wall(
            self,
            x: int,
            y: int,
            nx: int,
            ny: int,
            direction: int) -> None:
        """
        Open the wall between two neighboring cells.

        Args:
            x: Current cell column
            y: Current cell row
            nx: Neighbor cell column
            ny: Neighbor cell row
            direction: Direction toward the neighbor
        """
        self.grid[y][x] &= ~direction
        self.grid[ny][nx] &= ~OPPOSITE[direction]

        if self._recording:
            self.steps.append((x, y, nx, ny, direction))
