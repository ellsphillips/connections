from typing import List, Optional

from pydantic import BaseModel, Field, model_validator

from .exceptions import GameOverError, InvalidGuessError, InvalidPuzzleError
from .types import Difficulty, Group, Guess, GuessResult


class ConnectionsPuzzle(BaseModel):
    """16 words that partition into 4 hidden groups of 4.

    Solve from ``board`` + ``guess(...)``. The answer key is in ``groups`` — don't
    read it while solving; it's only there so you can check yourself.
    """

    id: str
    difficulty: Difficulty
    title: Optional[str] = None
    board: List[str] = Field(min_length=16, max_length=16)
    groups: List[Group] = Field(min_length=4, max_length=4)
    max_mistakes: int = 4  # NYT allows four; raise it to let a solver keep guessing.

    # Mutable game state.
    solved_categories: List[str] = Field(default_factory=list)
    mistakes: int = 0
    guesses: List[Guess] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_puzzle(self) -> "ConnectionsPuzzle":
        """Require 4 groups of 4 distinct words, with the board being exactly those 16."""
        members = [w for group in self.groups for w in group.members]
        self.board = [w.strip().upper() for w in self.board]
        if len(set(members)) != 16:
            raise InvalidPuzzleError(f"Puzzle '{self.id}' needs 16 distinct words")
        if set(self.board) != set(members):
            raise InvalidPuzzleError(f"Puzzle '{self.id}' board must be exactly the group words")
        return self

    @property
    def solved(self) -> List[Group]:
        """Groups correctly guessed so far."""
        return [self.find_group(c) for c in self.solved_categories]

    @property
    def remaining_words(self) -> List[str]:
        """Board words not yet in a solved group (board order)."""
        done = {w for group in self.solved for w in group.members}
        return [w for w in self.board if w not in done]

    @property
    def mistakes_remaining(self) -> int:
        return self.max_mistakes - self.mistakes

    @property
    def is_solved(self) -> bool:
        return len(self.solved_categories) == 4

    @property
    def is_failed(self) -> bool:
        return self.mistakes >= self.max_mistakes

    @property
    def is_over(self) -> bool:
        return self.is_solved or self.is_failed

    def find_group(self, category: str) -> Group:
        for group in self.groups:
            if group.category == category:
                return group
        raise InvalidPuzzleError(f"No group with category '{category}'")

    def guess(self, words: List[str]) -> Guess:
        """Guess four words form a group.

        Returns a :class:`Guess` whose result is ``CORRECT`` (exact group — marked
        solved), ``ONE_AWAY`` (three of four share a group — a mistake), or
        ``INCORRECT`` (a mistake). Raises :class:`InvalidGuessError` for malformed
        guesses and :class:`GameOverError` once the puzzle is over.
        """
        if self.is_over:
            raise GameOverError("The puzzle is already over")

        words = [w.strip().upper() for w in words]
        if len(words) != 4:
            raise InvalidGuessError(f"A guess must be 4 words, got {len(words)}")
        if len(set(words)) != 4:
            raise InvalidGuessError(f"A guess must be 4 distinct words: {words}")
        unknown = [w for w in words if w not in self.board]
        if unknown:
            raise InvalidGuessError(f"Words not on the board: {unknown}")
        solved = [w for w in words if w not in self.remaining_words]
        if solved:
            raise InvalidGuessError(f"Words already solved: {solved}")

        # The best overlap against any unsolved group decides the outcome.
        guessed = set(words)
        best_overlap, best_group = 0, None
        for group in self.groups:
            if group.category in self.solved_categories:
                continue
            overlap = len(guessed & group.as_set())
            if overlap > best_overlap:
                best_overlap, best_group = overlap, group

        if best_overlap == 4:
            self.solved_categories.append(best_group.category)
            guess = Guess(words=words, result=GuessResult.CORRECT, matched_category=best_group.category)
        else:
            self.mistakes += 1
            result = GuessResult.ONE_AWAY if best_overlap == 3 else GuessResult.INCORRECT
            guess = Guess(words=words, result=result)

        self.guesses.append(guess)
        return guess

    def reveal_group(self, category: str) -> None:
        """Mark a group solved without it counting as a guess/mistake."""
        self.find_group(category)
        if category not in self.solved_categories:
            self.solved_categories.append(category)

    def reveal_all(self) -> None:
        for group in self.groups:
            self.reveal_group(group.category)

    def undo(self) -> None:
        """Undo the most recent guess."""
        if not self.guesses:
            raise GameOverError("No guesses to undo")
        last = self.guesses.pop()
        if last.result == GuessResult.CORRECT:
            self.solved_categories.remove(last.matched_category)
        else:
            self.mistakes = max(0, self.mistakes - 1)

    def reset(self) -> None:
        """Reset to the initial, unsolved state."""
        self.solved_categories = []
        self.mistakes = 0
        self.guesses = []

    def validate_all(self) -> bool:
        """True once all four groups are solved."""
        return self.is_solved
