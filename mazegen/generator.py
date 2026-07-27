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
        - Perfect maze (single path) or braided maze (loops) depending
          on config.perfect
        - Seed for reproducibility
        - 42 pattern with closed cells
        - Error message if pattern cannot be placed
    """

    # Fraction of the remaining closed walls that are candidates for
    # removal when PERFECT=False (braiding step). Kept low so the
    # maze still reads as a maze, not an open room.
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

        # 3. If the maze must NOT be perfect, punch extra loops in it
        if not self.config.perfect:
            self._braid()

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
        Explores the maze using an iterative recursive-backtracker
        (DFS with an explicit stack instead of real recursion, to
        avoid RecursionError on large mazes where Python's default
        recursion limit would otherwise be exceeded).

        Each stack entry holds a cell together with its own shuffled
        list of remaining directions to try, so the resulting maze is
        identical (for a given seed) to what a true recursive DFS
        would produce: one shuffle per visited cell, tried in order,
        backtracking (popping the stack) once a cell has no more
        unvisited neighbours.

        Args:
            x: Starting cell column
            y: Starting cell row
            visited: Grid of already visited cells
        """
        visited[y][x] = True
        start_directions = list(DIRECTION.keys())
        random.shuffle(start_directions)
        # Reversed so remaining.pop() below consumes it front-to-back,
        # i.e. in the exact same order a `for direction in directions`
        # loop would (pop() removes from the end of the list).
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
        """Punches extra loops into the perfect maze (PERFECT=False).

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
                    continue  # '42' pattern cell: must stay isolated
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
            # Wall may already have been opened as a side effect of an
            # earlier candidate in this loop; skip if so.
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
        """Opens a wall only if it doesn't create a 3x3 open area.

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
            # Revert: close both sides of the wall again.
            self.grid[y][x] |= direction
            self.grid[ny][nx] |= OPPOSITE[direction]
            return False
        return True

    def _has_3x3_open_area(self, x: int, y: int) -> bool:
        """Checks whether any 3x3 window around (x, y) is fully open.

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
        """Checks if every internal wall in a 3x3 window is open.

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
