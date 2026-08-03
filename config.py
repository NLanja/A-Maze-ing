"""Configuration file parser for the A-Maze-ing project.

Reads a KEY=VALUE configuration file describing maze generation
parameters, validates it, and exposes the result as a MazeConfig object.
"""

from typing import Optional, Any


class ConfigError(Exception):
    """Raised when the configuration file is missing, malformed or invalid."""


REQUIRED_KEYS = {"WIDTH", "HEIGHT", "ENTRY", "EXIT"}


class MazeConfig:
    """Holds validated maze generation parameters.

    Attributes:
        width: maze width, number of cells.
        height: maze height, number of cells.
        entry: (x, y) entry coordinates.
        exit: (x, y) exit coordinates.
        output_file: path of the file where the maze will be written.
        perfect: whether the maze must be a perfect maze.
        seed: optional RNG seed for reproducibility.
        algorithm: Optional solving algorithm name (defaults to "bfs"). Unknown
                    values are validated later by `mazegen.solver.solve()`.
    """

    def __init__(self, path: str) -> None:
        """Parse and validates a maze configuration file."""
        config_dict = parse_config(path)
        self.width: int = config_dict["width"]
        self.height: int = config_dict["height"]
        self.entry: tuple[int, int] = config_dict["entry"]
        self.exit: tuple[int, int] = config_dict["exit"]
        self.output_file: str = config_dict["output_file"]
        self.perfect: bool = config_dict["perfect"]
        self.seed: Optional[int] = config_dict["seed"]
        self.algorithm: str = config_dict["algorithm"]


def parse_config(path: str) -> dict[str, Any]:
    """Parse and validates a maze configuration file.

    Args:
        path: path to the configuration file.

    Returns:
        A validated MazeConfig instance.

    Raises:
        ConfigError: if the file is missing, malformed, or contains
            invalid or incoherent values.
    """
    raw: dict[str, str] = {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as exc:
        raise ConfigError(f"Cannot open config file '{path}': {exc}") from exc

    for line_no, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigError(
                f"{path}:{line_no}:"
                f"invalid syntax (expected KEY=VALUE): '{line}'"
            )
        key, _, value = line.partition("=")
        key = key.strip().upper()
        value = value.strip()

        if not key:
            raise ConfigError(f"{path}:{line_no}: empty key")

        if key in raw:
            raise ConfigError(
                f"{path}:{line_no}: duplicate key '{key}'"
            )
        raw[key] = value

    missing = REQUIRED_KEYS - raw.keys()
    if missing:
        raise ConfigError(
            f"{path}: missing mandatory key(s): {', '.join(sorted(missing))}"
        )

    width = _parse_positive_int(raw["WIDTH"], "WIDTH")
    height = _parse_positive_int(raw["HEIGHT"], "HEIGHT")
    if width > 75:
        raise ConfigError("Maximum width is 75.")

    if height > 35:
        raise ConfigError("Maximum height is 35.")

    entry = _parse_coordinates(raw["ENTRY"], "ENTRY")
    exit_ = _parse_coordinates(raw["EXIT"], "EXIT")
    output_file = raw.get("OUTPUT_FILE", "maze.txt").strip()
    if not output_file:
        output_file = "maze.txt"
    perfect = _parse_bool(raw.get("PERFECT", "True"), "PERFECT")

    seed: Optional[int] = None
    if raw.get("SEED", ""):
        try:
            seed = int(raw["SEED"])
        except ValueError as exc:
            raise ConfigError(
                f"SEED must be an integer, got '{raw['SEED']}'"
            ) from exc

    algorithm = raw.get("ALGORITHM", "bfs").strip().lower() or "bfs"

    try:
        _validate_bounds(width, height, entry, exit_)
    except ConfigError as exc:
        print(f"Config validation error: {exc}  ")
        exit(1)

    res: dict[str, Any] = {
        "width": width,
        "height": height,
        "entry": entry,
        "exit": exit_,
        "output_file": output_file,
        "perfect": perfect,
        "seed": seed,
        "algorithm": algorithm,
    }
    return res


def _parse_positive_int(value: str, key: str) -> int:
    """Parse a string into a strictly positive integer.

    Args:
        value: The string value to parse.
        key: The configuration key associated with the value. Used in
            error messages.

    Returns:
        The parsed strictly positive integer.

    Raises:
        ConfigError: If ``value`` cannot be converted to an integer or if
            the parsed integer is less than or equal to zero.
    """
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ConfigError(f"{key} must be an integer, got '{value}'") from exc
    if parsed <= 0:
        raise ConfigError(f"{key} must be a positive integer, got {parsed}")
    return parsed


def _parse_coordinates(value: str, key: str) -> tuple[int, int]:
    """Parse a string into a pair of non-negative coordinates.

    The expected format is ``"x,y"``, where both ``x`` and ``y`` are
    non-negative integers.

    Args:
        value: The coordinate string to parse.
        key: The configuration key associated with the value. Used in
            error messages.

    Returns:
        A tuple ``(x, y)`` containing the parsed coordinates.

    Raises:
        ConfigError: If ``value`` is not in the expected ``"x,y"`` format,
            if either coordinate is not an integer, or if either coordinate
            is negative.
    """
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(f"{key} must be in 'x,y' format, got '{value}'")
    try:
        x, y = int(parts[0].strip()), int(parts[1].strip())
    except ValueError as exc:
        raise ConfigError(
            f"{key} coordinates must be integers, got '{value}'"
        ) from exc
    if x < 0 or y < 0:
        raise ConfigError(
            f"{key} coordinates must be non-negative, got '{value}'")
    return x, y


def _parse_bool(value: str, key: str) -> bool:
    """Parse a string into a boolean value.

    Only accepts ``"true"`` and ``"false"`` values.
    Matching is case-insensitive and ignores leading/trailing whitespace.

    Args:
        value: The string value to parse.
        key: The configuration key associated with the value.

    Returns:
        The parsed boolean value.

    Raises:
        ConfigError: If ``value`` is not ``"true"`` or ``"false"``.
    """
    normalized = value.strip().lower()

    if normalized == "true":
        return True
    if normalized == "false":
        return False

    raise ConfigError(f"{key} must be True or False, got '{value}'")


def _validate_bounds(
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_: tuple[int, int],
) -> None:
    """Validate that the entry and exit coordinates are within the grid.

    Ensures that both the entry and exit coordinates lie inside the maze
    boundaries and that they do not refer to the same cell.

    Args:
        width: The width of the maze.
        height: The height of the maze.
        entry: The entry cell coordinates as ``(x, y)``.
        exit_: The exit cell coordinates as ``(x, y)``.

    Raises:
        ConfigError: If either coordinate lies outside the maze bounds or
            if the entry and exit coordinates are identical.
    """
    for name, (x, y) in (("ENTRY", entry), ("EXIT", exit_)):
        if x >= width or y >= height:
            raise ConfigError(
                f"{name}={x},{y} is out of maze bounds ({width}x{height})"
            )
    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must be different cells")
