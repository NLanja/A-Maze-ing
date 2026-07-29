"""Configuration file parser for the A-Maze-ing project.

Reads a KEY=VALUE configuration file describing maze generation
parameters, validates it, and exposes the result as a MazeConfig object.
"""

from dataclasses import dataclass
from typing import Optional, Any


class ConfigError(Exception):
    """Raised when the configuration file is missing, malformed or invalid."""


REQUIRED_KEYS = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}


@dataclass
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
        algorithm: optional solving algorithm name ("bfs" by default).
            Not validated here on purpose (see note in parse_config)
            to avoid a circular import with mazegen.solver, which
            itself imports mazegen.generator, which imports this
            module. Unknown names are rejected later by
            mazegen.solver.solve(), which raises ValueError.
    """

    def __init__(self, path: str) -> None:
        """Parses and validates a maze configuration file."""
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
    """Parses and validates a maze configuration file.

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
        key = key.strip().upper()  # Normalize to uppercase (case-insensitive)
        value = value.strip()
        if not key:
            raise ConfigError(f"{path}:{line_no}: empty key")
        raw[key] = value

    missing = REQUIRED_KEYS - raw.keys()
    if missing:
        raise ConfigError(
            f"{path}: missing mandatory key(s): {', '.join(sorted(missing))}"
        )

    width = _parse_positive_int(raw["WIDTH"], "WIDTH")
    height = _parse_positive_int(raw["HEIGHT"], "HEIGHT")
    entry = _parse_coordinates(raw["ENTRY"], "ENTRY")
    exit_ = _parse_coordinates(raw["EXIT"], "EXIT")
    output_file = raw["OUTPUT_FILE"]
    if not output_file:
        raise ConfigError("OUTPUT_FILE cannot be empty")
    perfect = _parse_bool(raw["PERFECT"], "PERFECT")

    seed: Optional[int] = None
    if raw.get("SEED", ""):
        try:
            seed = int(raw["SEED"])
        except ValueError as exc:
            raise ConfigError(
                f"SEED must be an integer, got '{raw['SEED']}'"
            ) from exc

    # Optional: which shortest-path algorithm to use ("bfs" or
    # "astar"). Not validated against mazegen.solver.ALGORITHMS here
    # to avoid a circular import (see MazeConfig docstring); an
    # unknown name is instead rejected by solve() when actually used.
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
    """Parses a strictly positive integer value."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ConfigError(f"{key} must be an integer, got '{value}'") from exc
    if parsed <= 0:
        raise ConfigError(f"{key} must be a positive integer, got {parsed}")
    return parsed


def _parse_coordinates(value: str, key: str) -> tuple[int, int]:
    """Parses an 'x,y' coordinate pair."""
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
    """Parses a boolean-like value (True/False, 1/0, yes/no)."""
    normalized = value.strip().lower()
    if normalized in ("true", "1", "yes"):
        return True
    if normalized in ("false", "0", "no"):
        return False
    raise ConfigError(f"{key} must be a boolean (True/False), got '{value}'")


def _validate_bounds(
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_: tuple[int, int],
) -> None:
    """Ensures entry/exit are inside the grid and distinct."""
    for name, (x, y) in (("ENTRY", entry), ("EXIT", exit_)):
        if x >= width or y >= height:
            raise ConfigError(
                f"{name}={x},{y} is out of maze bounds ({width}x{height})"
            )
    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must be different cells")
