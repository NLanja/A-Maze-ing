"""
Simple maze generator test.
"""

from mazegen.generator import MazeGenerator


def save_hex_maze(maze, filename="output_maze.txt"):
    """
    Save a maze to a file in hexadecimal format.

    Args:
        maze: MazeGenerator object
        filename: Output file name
    """
    with open(filename, "w") as f:
        for row in maze.grid:
            # Convert each cell to hex (0-F) and join
            hex_row = ''.join(f'{cell:X}' for cell in row)
            f.write(hex_row + '\n')


def print_hex_maze(maze):
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

def main():
    """Generate and display a maze."""

    # Create maze (20x15)
    maze = MazeGenerator(width=3, height=3)
    maze.generate()

    # Display in hex
    print_hex_maze(maze)

    # Save to file
    save_hex_maze(maze)


if __name__ == "__main__":
    main()
