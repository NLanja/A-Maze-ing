#!/usr/bin/env python3
"""MLX display test."""

from mazegen.generator import MazeGenerator
from mazegen.display import MlxDisplay
from config import MazeConfig


def main() -> None:
    # Generate a maze
    config = MazeConfig("config.txt")
    maze = MazeGenerator(config)
    maze.generate()
    # Entry and exit
    entry = config.entry
    exit_pos = config.exit

    # Check 42 pattern
    if maze.pattern_placed:
        print("✅ 42 pattern placed")

    else:
        print("⚠️ 42 pattern omitted (maze too small)")

    print(f"✅ Maze {maze.width}x{maze.height} generated")

    # Display with MLX
    print("🖥️ Opening MLX window...")
    display = MlxDisplay(maze, cell_size=35, entry=entry, exit_pos=exit_pos)
    display.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
