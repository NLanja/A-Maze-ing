"""Shortest path solvers for A-Maze-ing mazes.

Provides several interchangeable algorithms (BFS, A*) that all share
the same signature, so a new algorithm can be plugged in later by
writing a `solve_xxx(grid, entry, exit_)` function and registering it
in ALGORITHMS, without touching the rest of the pipeline.

BFS is guaranteed to find the *shortest* path in an unweighted graph
such as a maze grid, which is what the output file format requires
(subject IV.5: "the shortest valid path from entry to exit"). A* with
a Manhattan-distance heuristic also finds the shortest path, usually
faster on large mazes, since moves have a uniform cost of 1.
"""

import heapq
from collections import deque
from typing import Callable, Optional

from mazegen.generator import DIRECTION, EAST, NORTH, SOUTH, WEST

DIRECTION_LETTER: dict[int, str] = {
    NORTH: "N",
    EAST: "E",
    SOUTH: "S",
    WEST: "W",
}

Coord = tuple[int, int]
SolverFn = Callable[[list[list[int]], Coord, Coord], Optional[list[str]]]


def solve_bfs(
    grid: list[list[int]],
    entry: Coord,
    exit_: Coord,
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

    visited: set[Coord] = {entry}
    queue: deque[tuple[Coord, list[str]]] = deque()
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


def solve_astar(
    grid: list[list[int]],
    entry: Coord,
    exit_: Coord,
) -> Optional[list[str]]:
    """Finds the shortest path between entry and exit using A*.

    Uses the Manhattan distance to `exit_` as heuristic, which is
    admissible here since every move costs exactly 1 and only 4
    cardinal moves are allowed. Result is equivalent in length to
    solve_bfs, but usually explores fewer cells on large mazes.

    Args:
        grid: maze grid, one wall-bitmask per cell (grid[y][x]).
        entry: (x, y) starting coordinates.
        exit_: (x, y) target coordinates.

    Returns:
        A list of single-letter moves ('N', 'E', 'S', 'W') describing
        a shortest path from entry to exit, or None if unreachable.
    """
    height = len(grid)
    width = len(grid[0]) if height else 0

    def heuristic(cell: Coord) -> int:
        return abs(cell[0] - exit_[0]) + abs(cell[1] - exit_[1])

    best_cost: dict[Coord, int] = {entry: 0}
    # heap entries: (priority, cost_so_far, cell, path_so_far)
    heap: list[tuple[int, int, Coord, list[str]]] = [
        (heuristic(entry), 0, entry, [])
    ]

    while heap:
        _, cost, (x, y), path = heapq.heappop(heap)

        if (x, y) == exit_:
            return path

        if cost > best_cost.get((x, y), float("inf")):
            continue  # a shorter route to this cell was already found

        for direction, (dx, dy) in DIRECTION.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            if grid[y][x] & direction:
                continue
            new_cost = cost + 1
            if new_cost < best_cost.get((nx, ny), float("inf")):
                best_cost[(nx, ny)] = new_cost
                priority = new_cost + heuristic((nx, ny))
                new_path = path + [DIRECTION_LETTER[direction]]
                heapq.heappush(
                    heap, (priority, new_cost, (nx, ny), new_path)
                )

    return None


ALGORITHMS: dict[str, SolverFn] = {
    "bfs": solve_bfs,
    "astar": solve_astar,
}


def solve(
    grid: list[list[int]],
    entry: Coord,
    exit_: Coord,
    algorithm: str = "bfs",
) -> Optional[list[str]]:
    """Finds the shortest path using the requested algorithm.

    Args:
        grid: maze grid, one wall-bitmask per cell (grid[y][x]).
        entry: (x, y) starting coordinates.
        exit_: (x, y) target coordinates.
        algorithm: name of the algorithm to use ("bfs" or "astar").

    Returns:
        A list of single-letter moves ('N', 'E', 'S', 'W'), or None
        if no path exists.

    Raises:
        ValueError: if `algorithm` is not a known name.
    """
    try:
        solver_fn = ALGORITHMS[algorithm]
    except KeyError as exc:
        raise ValueError(
            f"Unknown solving algorithm '{algorithm}', "
            f"choose one of {list(ALGORITHMS)}"
        ) from exc
    return solver_fn(grid, entry, exit_)


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
