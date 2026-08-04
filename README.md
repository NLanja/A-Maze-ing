*This project has been created as part of the 42 curriculum by lanasain, njrafano.*

# A-Maze-ing

# Description

**A-Maze-ing** is a Python project. It creates a maze from a configuration file, saves it to an output file, and then shows it and solves it in an interactive way.

The project uses:

* procedural generation with **DFS (Depth-First Search)**;
* shortest-path search with **BFS (Breadth-First Search)**;
* search with **A\*** and a heuristic;
* graphic display with **MiniLibX (MLX)**;
* animation of the generation and the solving;
* a reusable generation module, made as a Python package called `mazegen`.

The maximum size supported is **75 × 35 cells**, and a `SEED` lets you create the same maze again.

## Features

* Random or repeatable (with `SEED`) maze generation, perfect or not (`PERFECT=True`).
* Solving with BFS and with A*.
* Animation of the generation and of the solvers.
* Graphic display with MiniLibX: walls, entry, exit, path.
* Regeneration, showing/hiding the path, changing the wall color.
* Parsing and checking of the configuration file, with error handling.
* Reusable `mazegen` package.

---

# Instructions

## Installation

```bash
make install
```

This installs MiniLibX (from the given `.whl` file), `build`, `flake8`, and `mypy`.

## Requirements

* Python 3.10 or higher
* MiniLibX, Flake8, Mypy, Build

We recommend using a Python virtual environment.

## Running the program

```bash
make run
```

This is the same as:

```bash
python3 a_maze_ing.py config.txt
```

The program reads `config.txt`, checks the parameters, generates the maze, writes the result to the output file, and then shows it with MLX.

## Debug

```bash
make debug
```

This is the same as:

```bash
python3 -m pdb a_maze_ing.py config.txt
```

## Lint

```bash
make lint
```

This runs:

```bash
flake8 .
mypy . --warn-return-any \
       --warn-unused-ignores \
       --ignore-missing-imports \
       --disallow-untyped-defs \
       --check-untyped-defs
```

## Strict lint

```bash
make lint-strict
```

This runs:

```bash
flake8 .
mypy --strict .
```

## Cleaning

```bash
make clean
```

This removes `__pycache__`, `.mypy_cache`, `.pytest_cache`, and `*.pyc` files.

---

# Choice of algorithms

## Generation: DFS

DFS starts from one cell and slowly explores neighbor cells that have not been visited yet. The wall between the two chosen cells is removed, and then the exploration goes on from the new cell. When there are no more neighbors to explore, the algorithm goes back.

**Why DFS?** It is easy to build, it works well for making a connected and perfect maze, it creates long and winding paths, and it is very interesting to animate.

## Solving: BFS

BFS explores the maze level by level (by growing distance from the entry). Because every move has the same cost, BFS always finds a shortest path. It is also used as a reference to compare with A*.

## Solving: A*

A* uses a heuristic to guide the search toward the exit:

```text
g(n) = cost from the entry
h(n) = estimated cost to the exit
f(n) = g(n) + h(n)
```

The cells with the lowest `f(n)` are explored first.

## Summary

| Algorithm | Used for   | How it works                                 |
| --------- | ---------- | --------------------------------------------- |
| **DFS**   | Generation | Explores deeply and goes back when stuck      |
| **BFS**   | Solving    | Explores the maze level by level              |
| **A***   | Solving    | Guides the search with a heuristic            |
| **MLX**   | Display    | Shows the maze on the screen                  |

---

# Configuration

The program reads a text file where each line follows the format `KEY=VALUE` (lines that start with `#` are comments).

## Example of `config.txt`

```text
WIDTH=25
HEIGHT=20
ENTRY=0,0
EXIT=0,14
OUTPUT_FILE=maze.txt
PERFECT=True
ALGORITHM=astar
SEED=42
```

## Parameters

| Parameter     | Description                          | Example                 |
| ------------- | ------------------------------------- | ------------------------ |
| `WIDTH`       | Width of the maze (max **75**)        | `WIDTH=25`               |
| `HEIGHT`      | Height of the maze (max **35**)       | `HEIGHT=20`              |
| `ENTRY`       | Coordinates of the entry              | `ENTRY=0,0`              |
| `EXIT`        | Coordinates of the exit               | `EXIT=0,14`              |
| `OUTPUT_FILE` | Output file                           | `OUTPUT_FILE=maze.txt`   |
| `PERFECT`     | Whether the maze is perfect           | `PERFECT=True`           |
| `ALGORITHM`   | Solving algorithm                     | `ALGORITHM=astar`        |
| `SEED`        | Generation seed (for repeatable runs) | `SEED=42`                |

---

# Resources

* [VisuAlgo](https://visualgo.net/en) — a tool to see DFS, BFS, and other graph traversals
* [Maze Generation Algorithms - An Exploration](https://professor-l.github.io/mazes/) — a tool to see DFS and other graph traversals
* [Red Blob Games — Introduction to A*](https://www.redblobgames.com/pathfinding/a-star/introduction.html)
* [Jamis Buck — Maze Generation Algorithms](https://www.jamisbuck.org/mazes/)
* [GeeksforGeeks](https://www.geeksforgeeks.org/dsa/) — algorithm theory
* [w3schools](https://www.w3schools.com/python/) — learning Python modules
* [`build` documentation](https://build.pypa.io/en/stable/)
* [`pyproject.toml` guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

## Use of AI

`Claude` was used as a learning tool: to understand some Python concepts and algorithms (DFS, BFS, A*, heuristics), to think about how to organize the parsing, to find errors, and to improve the documentation. Both students checked, tested, and understood every answer that was generated, following the rules given in the project subject.

---

# Team and project management

The project was made by a team of two: **lanasain** and **njrafano**.

## Roles

| Member       | Contributions                                                                                                                        |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| **lanasain** | Parsing and checking of the configuration, BFS, A*, A* heuristic, animation of the DFS generation, putting all parts together        |
| **njrafano** | Maze generation with DFS, maze structure, MiniLibX, graphic display, animation of the solvers                                        |

## Planning and how it evolved

We first split the work along the two obvious layers of the project: config
parsing / solving (lanasain) and generation / display (njrafano), and agreed
on the grid and wall-bitmask format early so the two sides could be developed
in parallel without waiting on each other. The initial plan was:

1. Config parsing + a minimal generator producing a valid (but not
   necessarily perfect) maze.
2. Output file writing, then BFS solving.
3. MLX display with the required interactions (regenerate, path, colors).
4. Bonuses: A*, animations, the reusable `mazegen` package.

In practice, step 1 took longer than expected because of all the edge cases
in the config file (duplicate keys, out-of-bounds entry/exit, the "42"
pattern overlapping entry/exit, etc.), so the MLX display started later than
planned. The reusable-package requirement was also underestimated at first:
our first version of `mazegen` still imported the CLI's `config.py`, which
only became obvious once we tried installing the built wheel in an isolated
environment — we then refactored `MazeGenerator` to take plain arguments
(`width`, `height`, `entry`, `exit_`, `perfect`, `seed`) instead of a config
object, precisely so it has zero dependency on the rest of the repository.

## What worked well / what could be improved

**Worked well:**
* Agreeing on the wall-bitmask grid format up front let both of us work in
  parallel without much friction.
* Writing the DFS generation as an explicit stack (instead of real
  recursion) avoided `RecursionError` on large mazes and made it trivial to
  record steps for the generation animation "for free".
* Centralizing BFS/A* behind a single `solve()` / `solve_animated()` entry
  point in `solver.py` made it easy to add A* after BFS already worked, and
  to reuse the exact same rendering code for both in the MLX display.

**Could be improved:**
* The reusable `mazegen` module should have been designed as fully
  standalone from the very first commit instead of being refactored later;
  we now systematically test every "reusable" module by installing its
  built wheel in a throw-away virtual environment before considering it
  done.
* Error handling in `config.py` was not fully consistent (one validation
  path printed and exited directly instead of raising `ConfigError` like
  every other check) — this is the kind of inconsistency that peer review
  catches faster than working alone.
* More automated tests (currently mostly manual/ad-hoc scripts) would have
  caught both issues above earlier.

## Tools used

* **Python 3.10**, `venv` for dependency isolation.
* **flake8** and **mypy `--strict`** (via the `lint` / `lint-strict` Makefile
  targets) to keep the codebase clean as we went, not just before handing
  in.
* **`build`** (PyPA) to produce the `mazegen` wheel/sdist from
  `pyproject.toml`.
* **Git** for version control and code review between the two of us.
* **Claude** (see "Use of AI" above) as a learning and debugging aid.

# The `mazegen` package

The maze generator is built as **one single class**, `MazeGenerator`, inside a
standalone module. It has **no dependency on the rest of this repository**
(not even on `config.py`): it only uses the Python standard library, so it can
be pip-installed and imported from any other project, completely separately
from the MLX display, the CLI, or the config parser.

## Structure

```text
mazegen/
├── __init__.py      # exposes MazeGenerator and MazeGenerationError
└── generator.py
```

Main class: `MazeGenerator`. The structure it creates (a grid of wall
bitmasks, see below) does not have to be the same as the format of the
output file — `a_maze_ing.py` is the piece that turns it into that format.

## Instantiate and use the generator (basic example)

```python
from mazegen import MazeGenerator

# width and height are the only required arguments.
generator = MazeGenerator(width=50, height=30)
generator.generate()

# The carved maze is available right away as a grid of wall bitmasks.
print(generator.width, generator.height)   # 50 30
print(generator.grid[0][0])                # e.g. 9 (North+West closed)
```

## Passing custom parameters (size, seed, entry/exit, perfect)

```python
from mazegen import MazeGenerator, MazeGenerationError

generator = MazeGenerator(
    width=50,
    height=30,
    entry=(0, 0),        # optional, defaults to (0, 0)
    exit_=(49, 29),       # optional, defaults to (width - 1, height - 1)
    perfect=True,         # optional, default True: exactly one path
    seed=123,              # optional: same seed -> same maze every time
)
try:
    generator.generate()
except MazeGenerationError as exc:
    # e.g. the '42' pattern would overlap the entry or exit cell
    print(f"Could not generate maze: {exc}")
```

* `width` / `height`: number of cells (this project's CLI caps them at
  75 × 35, but the class itself has no built-in limit).
* `perfect=False` produces a braided maze (loops added, still no 3×3 fully
  open area).
* `seed` makes the run reproducible: the same `seed` with the same
  `width`/`height` always regenerates an identical maze.

## Accessing the generated structure and a solution

```python
from collections import deque
from mazegen import MazeGenerator

generator = MazeGenerator(width=20, height=15, seed=1)
generator.generate()

# The maze itself: one wall-bitmask per cell, grid[y][x].
# Bit 1=North, 2=East, 4=South, 8=West (1 = wall closed, 0 = open).
grid = generator.grid
entry, exit_ = generator.entry, generator.exit_
print(f"{generator.width}x{generator.height} maze, "
      f"'42' pattern placed: {generator.pattern_placed}")

# Access at least a solution: a minimal BFS shortest-path example
# (the actual project uses solver.py, which is not part of mazegen).
DIRS = {1: (0, -1), 2: (1, 0), 4: (0, 1), 8: (-1, 0)}


def shortest_path(grid, entry, exit_):
    seen = {entry}
    queue = deque([(entry, [])])
    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == exit_:
            return path
        for direction, (dx, dy) in DIRS.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < len(grid[0]) and 0 <= ny < len(grid)):
                continue
            if (nx, ny) in seen or grid[y][x] & direction:
                continue
            seen.add((nx, ny))
            queue.append(((nx, ny), path + [direction]))
    return None


path = shortest_path(grid, entry, exit_)
print(f"Solution length: {len(path) if path else 'no path found'}")
```

## `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mazegen"
version = "1.1.0"
description = "Maze generation"
authors = [
  { name="lanasain", email="lanasain@student.42antananarivo.mg" },
  { name="njrafano", email="njrafano@student.42antananarivo.mg" },
]

[tool.setuptools]
py-modules = ["mazegen.generator"]
```

## Building and installing the package

```bash
python3 -m build
```

This creates (it is also installed through `make install`):

```text
dist/
├── mazegen-1.1.0-py3-none-any.whl
└── mazegen-1.1.0.tar.gz
```

Installation, from anywhere, in a fresh virtual environment (no need for the
rest of this repository, `config.py` included):

```bash
python3 -m pip install dist/mazegen-1.1.0-py3-none-any.whl
```

then, in another project:

```python
from mazegen import MazeGenerator
```

The package must stay possible to rebuild from the source files, and it must
be available at the root of the repository:

```text
A-Maze-ing/
│
├── mlx-2.2-py3-none-any.whl
├── mazegen-1.1.0-py3-none-any.whl
├── pyproject.toml
├── mazegen/
│   ├── __init__.py
│   └── generator.py
│
└── README.md
```

---

# Output file format

Each cell of the maze is shown as **one hexadecimal digit**, where each bit stands for one wall:

| Bit | Direction |
| --- | --------- |
| `0` | North     |
| `1` | East      |
| `2` | South     |
| `3` | West      |

A bit set to `1` means the wall is closed; a bit set to `0` means the wall is open (example: `3 = 0011`, `A = 1010`).

The cells are written line by line. After one empty line, the file contains:

1. the coordinates of the entry;
2. the coordinates of the exit;
3. the shortest path between the entry and the exit, written with the letters `N E S W`.

---

# Graphic display

The MiniLibX display shows the walls, the entry, the exit, the path, and also the progress of the generation and of the solvers.

## Keyboard controls

| Key         | Action                                                                    |
| ----------- | --------------------------------------------------------------------------- |
| `R`         | Generates a new maze                                                     |
| `P`         | Shows/hides the solution step by step                                    |
| `F`         | Stops the animation that is running                                      |
| `B`         | Starts the solving animation (BFS or A*, depending on `ALGORITHM`)      |
| `D`         | Shows the solution right away                                            |
| `C`         | Changes the color of the walls                                           |
| `S`         | Saves                                                                     |
| `G`         | Plays the maze generation animation again                                |
| `Q` / `Esc` | Quits the program                                                        |