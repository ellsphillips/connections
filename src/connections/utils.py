"""Load puzzles from the ``data/<tier>.json`` files (each a JSON array of puzzles)."""
import json
from typing import List

from .puzzle import ConnectionsPuzzle


def load_puzzles(file_path: str) -> List[ConnectionsPuzzle]:
    """Load every puzzle from a tier file (e.g. ``data/easy.json``)."""
    with open(file_path, "r") as f:
        data = json.load(f)
    return [ConnectionsPuzzle.model_validate(puzzle) for puzzle in data]


def load_puzzle(file_path: str, index: int = 0) -> ConnectionsPuzzle:
    """Load a single puzzle from a tier file (the first one by default)."""
    puzzles = load_puzzles(file_path)
    if not 0 <= index < len(puzzles):
        raise IndexError(
            f"{file_path} has {len(puzzles)} puzzle(s); no puzzle at index {index}"
        )
    return puzzles[index]
