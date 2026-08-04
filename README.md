*This project was made as part of the 42 school course, by lanasain and njrafano.*

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

The maximum size supported is **70 × 35 cells**, and a `SEED` lets you create the same maze again.

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
| `WIDTH`       | Width of the maze (max **70**)        | `WIDTH=25`               |
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

# 6. Contribution

The project was made by a team of two: **lanasain** and **njrafano**.

| Member       | Contributions                                                                                                                        |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| **lanasain** | Parsing and checking of the configuration, BFS, A*, A* heuristic, animation of the DFS generation, putting all parts together        |
| **njrafano** | Maze generation with DFS, maze structure, MiniLibX, graphic display, animation of the solvers                                        |


# The `mazegen` package

The maze generator is built as **one single class**, in an independent module. It can be reused in another project, separately from the MLX display.

## Structure

```text
mazegen/
└── generator.py
```

Main class: `MazeGenerator`. The structure it creates does not have to be the same as the format of the output file.

## Creating and customizing the generator

```python
from mazegen.generator import MazeGenerator

generator = MazeGenerator(
    width=50,
    height=30,
    seed=123
)

maze = generator.generate()
```

`width` and `height` set the size (max 70 × 35), and `seed` makes the generation repeatable.

## `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mazegen"
version = "1.0"
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
├── mazegen-1.0-py3-none-any.whl
└── mazegen-1.0.tar.gz
```

Installation:

```bash
python3 -m pip install dist/mazegen-1.0-py3-none-any.whl
```

then, in another project:

```python
from mazegen.generator import MazeGenerator
```

The package must stay possible to rebuild from the source files, and it must be available at the root of the repository:

```text
A-Maze-ing/
│
├── mlx-2.2-py3-none-any.whl
├── pyproject.toml
├── mazegen/
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