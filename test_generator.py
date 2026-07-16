"""
Simple maze generator + solver test.
"""

from config import ConfigError, parse_config
from mazegen.generator import MazeGenerator
from mazegen.solver import load_hex_grid, solve


def save_hex_maze(
    maze: MazeGenerator,
    entry: tuple[int, int],
    exit_: tuple[int, int],
    path: list[str],
    filename: str = "output_maze.txt",
) -> None:
    """
    Save a maze to a file: hex grid, blank line, entry, exit, path.

    Matches the output file format required by the subject (IV.5).

    Args:
        maze: MazeGenerator object
        entry: (x, y) entry coordinates
        exit_: (x, y) exit coordinates
        path: shortest path as a list of 'N'/'E'/'S'/'W' letters
        filename: Output file name
    """
    with open(filename, "w") as f:
        for row in maze.grid:
            hex_row = ''.join(f'{cell:X}' for cell in row)
            f.write(hex_row + '\n')
        f.write('\n')
        f.write(f'{entry[0]},{entry[1]}\n')
        f.write(f'{exit_[0]},{exit_[1]}\n')
        f.write(''.join(path) + '\n')


def print_hex_maze(maze: MazeGenerator) -> None:
    """
    Print a maze in hexadecimal format.

    Args:
        maze: MazeGenerator object
    """
    for row in maze.grid:
        hex_row = ''.join(f'{cell:X}' for cell in row)
        print(hex_row)


# ============================================
# MAIN PROGRAM
# ============================================

def main() -> None:
    """Load the config, generate the maze, solve it, and save it."""
    try:
        cfg = parse_config("config.txt")
    except ConfigError as exc:
        print(f"Error: {exc}")
        return

    # 1. Generate the maze using the parameters read from config.txt
    maze = MazeGenerator(width=cfg.width, height=cfg.height, seed=cfg.seed)
    maze.generate()

    print(f"entry={cfg.entry} exit={cfg.exit} perfect={cfg.perfect}")
    print_hex_maze(maze)

    # 2. Solve it (BFS -> shortest path) directly from the in-memory grid
    path = solve(maze.grid, cfg.entry, cfg.exit)
    if path is None:
        print("Error: no path found between entry and exit "
              "(maze is not connected)")
        return
    print("path:", ''.join(path))

    # 3. Save grid + entry + exit + path to the output file
    save_hex_maze(maze, cfg.entry, cfg.exit, path, cfg.output_file)

    # 4. Sanity check: reload the hex grid straight from the saved file
    #    and re-solve it, to prove the solver works independently of
    #    the in-memory MazeGenerator object (as required for reuse).
    reloaded_grid = load_hex_grid(cfg.output_file)
    reloaded_path = solve(reloaded_grid, cfg.entry, cfg.exit)
    print("path re-solved from file:", ''.join(reloaded_path or []))
    assert reloaded_path == path, "solver mismatch between memory and file!"


if __name__ == "__main__":
    main()
