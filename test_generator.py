"""Sanity test for the maze generator + BFS solver pipeline.

Not part of the graded deliverable (see subject III.3): this script is
only meant to be run manually during development, to check that
generation, solving, and file I/O stay consistent with each other.
Run it with: python3 test_generator.py
"""

from a_maze_ing import save_maze
from config import ConfigError, MazeConfig
from mazegen.generator import MazeGenerator
from mazegen.solver import load_hex_grid, solve


def print_hex_maze(maze: MazeGenerator) -> None:
    """Prints a maze in hexadecimal format, one row per line.

    Args:
        maze: the generated maze to print.
    """
    for row in maze.grid:
        print("".join(f"{cell:X}" for cell in row))


def main(config_path: str = "config.txt") -> None:
    """Loads the config, generates the maze, solves it, and saves it.

    Args:
        config_path: path to the configuration file to use.
    """
    try:
        config = MazeConfig(config_path)
    except ConfigError as exc:
        print(f"Error: {exc}")
        return

    # 1. Generate the maze using the parameters read from the config file
    maze = MazeGenerator(config)
    maze.generate()

    print(
        f"entry={config.entry} exit={config.exit} "
        f"perfect={config.perfect}"
    )
    print_hex_maze(maze)

    # 2. Solve it (BFS -> shortest path) directly from the in-memory grid
    path = solve(maze.grid, config.entry, config.exit)
    if path is None:
        print(
            "Error: no path found between entry and exit "
            "(maze is not connected)"
        )
        return
    print("path:", "".join(path))

    # 3. Save grid + entry + exit + path to the output file
    save_maze(maze, config.entry, config.exit, path, config.output_file)

    # 4. Sanity check: reload the hex grid straight from the saved file
    #    and re-solve it, to prove the solver works independently of
    #    the in-memory MazeGenerator object (as required for reuse).
    reloaded_grid = load_hex_grid(config.output_file)
    reloaded_path = solve(reloaded_grid, config.entry, config.exit)
    print("path re-solved from file:", "".join(reloaded_path or []))
    assert reloaded_path == path, "solver mismatch between memory and file!"
    print("OK: in-memory and reloaded-from-file paths match.")


if __name__ == "__main__":
    main()
