"""Shortest path solver for A-Maze-ing mazes.

Uses a breadth-first search (BFS) rather than a DFS, because BFS is
guaranteed to find the *shortest* path in an unweighted graph such as
a maze grid, which is what the output file format requires (see the
subject, section IV.5: "the shortest valid path from entry to exit").
"""

from collections import deque
from typing import Optional

from mazegen.generator import DIRECTION, EAST, NORTH, SOUTH, WEST

DIRECTION_LETTER: dict[int, str] = {
    NORTH: "N",
    EAST: "E",
    SOUTH: "S",
    WEST: "W",
}


def solve(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
) -> Optional[list[str]]:
    """Finds the shortest path between entry and exit using BFS.

    Args:
        grid: maze grid, one wall-bitmask per cell (grid[y][x]),
            using the same NORTH/EAST/SOUTH/WEST bit encoding as
            mazegen.generator (1 = wall closed).
        entry: (x, y) starting coordinates.
        exit_: (x, y) target coordinates.

    Returns:
        A list of single-letter moves ('N', 'E', 'S', 'W') describing
        the shortest path from entry to exit, or None if no path
        exists (should not happen on a valid connected maze).
    """
    height = len(grid)
    width = len(grid[0]) if height else 0

    visited: set[tuple[int, int]] = {entry}
    queue: deque[tuple[tuple[int, int], list[str]]] = deque()
    queue.append((entry, []))

    while queue:
        (x, y), path = queue.popleft()

        if (x, y) == exit_:
            return path

        for direction, (dx, dy) in DIRECTION.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            if (nx, ny) in visited:
                continue
            if grid[y][x] & direction:
                continue  # wall closed on this side, can't pass
            visited.add((nx, ny))
            queue.append(((nx, ny), path + [DIRECTION_LETTER[direction]]))

    return None


def load_hex_grid(path: str) -> list[list[int]]:
    """Loads a maze wall-grid from a hex-encoded maze file.

    Reads lines of hex digits until the first blank line (ignores any
    trailing entry/exit/path section that may follow it).

    Args:
        path: path to the hex maze file (e.g. "maze.txt").

    Returns:
        The decoded grid, one wall-bitmask per cell.
    """
    grid: list[list[int]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                break
            grid.append([int(c, 16) for c in line])
    return grid
