#!/usr/bin/env python3
"""A-Maze-ing main program.

Reads a configuration file, generates a maze, computes the shortest
path between the entry and the exit, writes the result to the
configured output file, and displays the maze graphically (MLX).

Usage:
    python3 a_maze_ing.py <config_file>
"""

import sys
from typing import NoReturn
from config import ConfigError, MazeConfig
from mazegen import MazeGenerator
from solver import solve


def error_exit(message: str) -> NoReturn:
    """Prints a clear error message to stderr and exits with code 1.

    Args:
        message: human-readable description of the error.
    """
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def save_maze(
    maze: MazeGenerator,
    entry: tuple[int, int],
    exit_: tuple[int, int],
    path: list[str],
    filename: str,
) -> None:
    """Writes the maze to a file using the hexadecimal wall format.

    Format (see subject IV.5): one hex digit per cell (row by row),
    then a blank line, then entry coordinates, exit coordinates and
    the shortest path as a string of N/E/S/W letters.

    Args:
        maze: the generated maze.
        entry: (x, y) entry coordinates.
        exit_: (x, y) exit coordinates.
        path: shortest path from entry to exit as N/E/S/W letters.
        filename: path of the output file to write.

    Raises:
        OSError: if the file cannot be written.
    """
    with open(filename, "w", encoding="utf-8") as f:
        for row in maze.grid:
            f.write("".join(f"{cell:X}" for cell in row) + "\n")
        f.write("\n")
        f.write(f"{entry[0]},{entry[1]}\n")
        f.write(f"{exit_[0]},{exit_[1]}\n")
        f.write("".join(path) + "\n")


def display_maze(maze: MazeGenerator, config: MazeConfig) -> None:
    """Displays the maze graphically using MLX.

    Falls back gracefully (prints a warning, does not crash) if MLX
    cannot be imported or initialized (e.g. no display/GPU available).
    The maze file has already been saved at this point either way.

    Args:
        maze: the generated maze to display.
        config: the parsed configuration (for entry/exit coordinates).
    """
    try:
        from display import MlxDisplay
    except ImportError as exc:
        print(f"Warning: display unavailable ({exc}). Maze file was saved.")
        return

    try:
        display = MlxDisplay(
            maze,
            cell_size=25,
            entry=config.entry,
            exit_pos=config.exit,
            output_file=config.output_file,
        )
        display.run()
    except Exception as exc:
        print(
            f"Warning: could not open graphical display ({exc}). "
            "Maze file was still generated and saved."
        )


def print_hex_maze(maze: MazeGenerator) -> None:
    """Prints a maze in hexadecimal format, one row per line.

    Args:
        maze: the generated maze to print.
    """
    for row in maze.grid:
        print("".join(f"{cell:X}" for cell in row))


def main() -> None:
    """Generate, solve, and display a maze from a configuration file.

    Exits with an error message if the configuration is invalid, maze
    generation fails, or no solution path exists.
    """
    if len(sys.argv) != 2:
        error_exit(f"usage: python3 {sys.argv[0]} <config_file>")

    config_path = sys.argv[1]

    try:
        config = MazeConfig(config_path)
    except ConfigError as exc:
        error_exit(str(exc))

    try:
        maze = MazeGenerator(config)
        maze.generate()
    except Exception as exc:
        error_exit(f"maze generation failed: {exc}")

    if not maze.pattern_placed:
        print(
            "Warning: '42' pattern omitted, maze is too small "
            f"({config.width}x{config.height})."
        )

    try:
        path = solve(maze.grid, config.entry, config.exit, config.algorithm)
    except ValueError as exc:
        error_exit(str(exc))
    if path is None:
        error_exit("no path found between entry and exit (maze not connected)")

    print(f"Shortest path ({len(path)} steps): {''.join(path)}")

    display_maze(maze, config)


if __name__ == "__main__":
    main()
