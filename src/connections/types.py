from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class Difficulty(str, Enum):
    """The problem-set tier a puzzle belongs to."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    CRYPTIC = "cryptic"


class Level(str, Enum):
    """A group's within-puzzle difficulty (NYT colour convention)."""

    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"


class GuessResult(str, Enum):
    CORRECT = "correct"        # all four belong to the same group
    ONE_AWAY = "one_away"      # exactly three belong to the same group
    INCORRECT = "incorrect"    # otherwise


class Group(BaseModel):
    """One hidden group: its four ``members`` and the ``category`` that joins them."""

    category: str
    level: Level
    members: List[str] = Field(min_length=4, max_length=4)

    @field_validator("members")
    @classmethod
    def _normalise(cls, members: List[str]) -> List[str]:
        members = [m.strip().upper() for m in members]
        if len(set(members)) != len(members):
            raise ValueError(f"Group has duplicate words: {members}")
        return members

    def as_set(self) -> frozenset:
        return frozenset(self.members)


class Guess(BaseModel):
    """A guess and its outcome, kept in the puzzle's history."""

    words: List[str]
    result: GuessResult
    matched_category: Optional[str] = None
