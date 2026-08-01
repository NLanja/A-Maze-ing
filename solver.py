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
from typing import Callable, Optional, Any

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


def solve_bfs_animated(
    grid: list[list[int]],
    entry: Coord,
    exit_: Coord,
) -> tuple[Optional[list[str]], list[dict[str, Any]]]:
    """BFS solver that records each step for animation.

    Records visited cells, frontier queue, and current cell at each step.

    Args:
        grid: maze grid, one wall-bitmask per cell (grid[y][x]).
        entry: (x, y) starting coordinates.
        exit_: (x, y) target coordinates.

    Returns:
        A tuple (path, steps) where:
            - path: list of moves or None if no path
            - steps: list of dicts with keys:
                'visited': set of visited cells
                'frontier': deque of cells in queue
                'current': current cell being explored
                'path': current path to current cell
                'type': 'init', 'explore', 'discover', or 'found'
    """
    height = len(grid)
    width = len(grid[0]) if height else 0

    visited: set[Coord] = {entry}
    queue: deque[tuple[Coord, list[str]]] = deque()
    queue.append((entry, []))
    steps = []

    # Initial state
    steps.append({
        'visited': set(visited),
        'frontier': deque(queue),
        'current': entry,
        'path': [],
        'type': 'init'
    })

    while queue:
        (x, y), path = queue.popleft()

        # Exploration state
        steps.append({
            'visited': set(visited),
            'frontier': deque(queue),
            'current': (x, y),
            'path': path,
            'type': 'explore'
        })

        if (x, y) == exit_:
            steps.append({
                'visited': set(visited),
                'frontier': deque(queue),
                'current': (x, y),
                'path': path,
                'type': 'found'
            })
            return path, steps

        for direction, (dx, dy) in DIRECTION.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            if (nx, ny) in visited:
                continue
            if grid[y][x] & direction:
                continue
            visited.add((nx, ny))
            queue.append(((nx, ny), path + [DIRECTION_LETTER[direction]]))

            # Discovery state
            steps.append({
                'visited': set(visited),
                'frontier': deque(queue),
                'current': (nx, ny),
                'path': path + [DIRECTION_LETTER[direction]],
                'type': 'discover',
                'parent': (x, y)
            })

    return None, steps


def _exact_distances_to(
    grid: list[list[int]], target: Coord
) -> dict[Coord, int]:
    """Computes the true (wall-aware) graph distance from `target` to
    every cell reachable from it, via one full BFS starting at target.

    Wall openings are symmetric in this maze format (carving a passage
    clears the matching bit on both sides, see mazegen.generator), so
    a BFS run backwards from `target` gives exactly the same distances
    as a forward BFS from any cell to `target` would.

    Args:
        grid: maze grid, one wall-bitmask per cell (grid[y][x]).
        target: the cell to measure distances to (typically the exit).

    Returns:
        A dict mapping each cell reachable from `target` to its exact
        number of moves to reach it. Unreachable cells are absent.
    """
    height = len(grid)
    width = len(grid[0]) if height else 0

    dist: dict[Coord, int] = {target: 0}
    queue: deque[Coord] = deque([target])
    while queue:
        x, y = queue.popleft()
        for direction, (dx, dy) in DIRECTION.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            if (nx, ny) in dist:
                continue
            if grid[y][x] & direction:
                continue
            dist[(nx, ny)] = dist[(x, y)] + 1
            queue.append((nx, ny))
    return dist


def solve_astar_animated(
    grid: list[list[int]],
    entry: Coord,
    exit_: Coord,
) -> tuple[Optional[list[str]], list[dict[str, Any]]]:
    """A* solver for animation, using an exact (wall-aware) heuristic.

    `solve_astar` (the plain solver used for the graded shortest path
    and the output file) uses the textbook Manhattan-distance
    heuristic. That heuristic is admissible and gives a correct
    shortest path, but it only measures straight-line distance - it
    can't "see" walls, so a Manhattan-guided search still visibly
    backtracks whenever it heads toward a cell that *looks* close but
    is actually walled off.

    This animated variant instead precomputes the exact graph distance
    from every cell to `exit_` with one full BFS starting at the exit
    (see `_exact_distances_to`), before the animated search even
    starts. That "perfect" heuristic already reflects every wall, so
    A* here expands, one by one, exactly the cells on a shortest path
    to the exit - no wasted exploration, no backtracking. This exact
    heuristic is kept out of `solve_astar`/`solve` on purpose: it is
    display-only, since computing it amounts to solving the maze once
    already, which isn't the point of the graded solver.

    Mirrors the step schema produced by `solve_bfs_animated` (keys
    'visited', 'frontier', 'current', 'path', 'type') so that a single
    display-side animator can replay either algorithm without knowing
    which one actually ran.

    Args:
        grid: maze grid, one wall-bitmask per cell (grid[y][x]).
        entry: (x, y) starting coordinates.
        exit_: (x, y) target coordinates.

    Returns:
        A tuple (path, steps) where:
            - path: list of moves or None if no path
            - steps: list of dicts with keys:
                'visited': set of expanded ("closed") cells
                'frontier': set of cells currently in the open set
                'current': current cell being explored
                'path': current path to current cell
                'type': 'init', 'explore', 'discover', or 'found'
    """
    height = len(grid)
    width = len(grid[0]) if height else 0

    true_dist = _exact_distances_to(grid, exit_)

    def heuristic(cell: Coord) -> int:
        # Falls back to Manhattan only if `cell` is somehow unreachable
        # from the exit (shouldn't happen on a connected maze) so the
        # search still terminates instead of raising a KeyError.
        return true_dist.get(
            cell, abs(cell[0] - exit_[0]) + abs(cell[1] - exit_[1])
        )

    best_cost: dict[Coord, int] = {entry: 0}
    # heap entries: (priority, cost_so_far, cell, path_so_far)
    heap: list[tuple[int, int, Coord, list[str]]] = [
        (heuristic(entry), 0, entry, [])
    ]
    closed: set[Coord] = set()
    steps: list[dict[str, Any]] = []

    def open_cells() -> set[Coord]:
        return {cell for _, _, cell, _ in heap}

    # Initial state
    steps.append({
        'visited': set(closed),
        'frontier': open_cells(),
        'current': entry,
        'path': [],
        'type': 'init'
    })

    while heap:
        _, cost, (x, y), path = heapq.heappop(heap)

        if cost > best_cost.get((x, y), float("inf")):
            continue  # a shorter route to this cell was already found

        closed.add((x, y))

        # Exploration state
        steps.append({
            'visited': set(closed),
            'frontier': open_cells(),
            'current': (x, y),
            'path': path,
            'type': 'explore'
        })

        if (x, y) == exit_:
            steps.append({
                'visited': set(closed),
                'frontier': open_cells(),
                'current': (x, y),
                'path': path,
                'type': 'found'
            })
            return path, steps

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

                # Discovery state
                steps.append({
                    'visited': set(closed),
                    'frontier': open_cells(),
                    'current': (nx, ny),
                    'path': new_path,
                    'type': 'discover',
                    'parent': (x, y)
                })

    return None, steps


AnimatedSolverFn = Callable[
    [list[list[int]], Coord, Coord],
    tuple[Optional[list[str]], list[dict[str, Any]]],
]

ALGORITHMS_ANIMATED: dict[str, AnimatedSolverFn] = {
    "bfs": solve_bfs_animated,
    "astar": solve_astar_animated,
}


def solve_animated(
    grid: list[list[int]],
    entry: Coord,
    exit_: Coord,
    algorithm: str = "bfs",
) -> tuple[Optional[list[str]], list[dict[str, Any]]]:
    """Finds a shortest path with the requested algorithm, recording steps.

    Centralizes the animated solve the same way `solve` centralizes the
    plain solve: pick the algorithm named by `algorithm` (typically
    `config.algorithm`, itself read from ALGORITHM in config.txt) and
    run its animated variant, so callers (e.g. the MLX display) never
    have to hardcode a specific algorithm's animated function.

    Args:
        grid: maze grid, one wall-bitmask per cell (grid[y][x]).
        entry: (x, y) starting coordinates.
        exit_: (x, y) target coordinates.
        algorithm: name of the algorithm to use ("bfs" or "astar").

    Returns:
        A tuple (path, steps) as returned by the underlying animated
        solver (see `solve_bfs_animated` / `solve_astar_animated`).

    Raises:
        ValueError: if `algorithm` is not a known name.
    """
    try:
        solver_fn = ALGORITHMS_ANIMATED[algorithm]
    except KeyError as exc:
        raise ValueError(
            f"Unknown solving algorithm '{algorithm}', "
            f"choose one of {list(ALGORITHMS_ANIMATED)}"
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
