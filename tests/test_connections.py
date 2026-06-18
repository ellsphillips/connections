import pytest

from connections import (
    ConnectionsPuzzle,
    GameOverError,
    Group,
    GuessResult,
    InvalidGuessError,
    InvalidPuzzleError,
    Level,
    load_puzzle,
    load_puzzles,
)


@pytest.fixture
def groups():
    return [
        Group(category="Dog breeds", level=Level.YELLOW, members=["POODLE", "BEAGLE", "PUG", "CORGI"]),
        Group(category="Planets", level=Level.GREEN, members=["MARS", "VENUS", "SATURN", "NEPTUNE"]),
        Group(category="Pizza toppings", level=Level.BLUE, members=["CHEESE", "MUSHROOM", "PEPPERONI", "OLIVE"]),
        Group(category="Days of the week", level=Level.PURPLE, members=["MONDAY", "FRIDAY", "SUNDAY", "TUESDAY"]),
    ]


@pytest.fixture
def board(groups):
    return [w for group in groups for w in group.members]


@pytest.fixture
def puzzle(groups, board):
    return ConnectionsPuzzle(id="test-1", difficulty="easy", board=board, groups=groups)


class TestConstruction:
    def test_basics(self, puzzle):
        assert len(puzzle.board) == 16
        assert len(puzzle.groups) == 4
        assert puzzle.remaining_words == puzzle.board
        assert not puzzle.is_solved
        assert puzzle.mistakes_remaining == 4

    def test_members_are_uppercased(self):
        group = Group(category="x", level=Level.YELLOW, members=["a", "b", "c", "d"])
        assert group.members == ["A", "B", "C", "D"]

    def test_board_must_match_groups(self, groups):
        bad_board = [w for group in groups for w in group.members]
        bad_board[0] = "WRONGWORD"
        with pytest.raises(InvalidPuzzleError):
            ConnectionsPuzzle(id="bad", difficulty="easy", board=bad_board, groups=groups)

    def test_duplicate_word_across_groups_rejected(self, board):
        dupe_groups = [
            Group(category="a", level=Level.YELLOW, members=["DUP", "B", "C", "D"]),
            Group(category="b", level=Level.GREEN, members=["DUP", "F", "G", "H"]),
            Group(category="c", level=Level.BLUE, members=["I", "J", "K", "L"]),
            Group(category="d", level=Level.PURPLE, members=["M", "N", "O", "P"]),
        ]
        with pytest.raises(InvalidPuzzleError):
            ConnectionsPuzzle(
                id="bad",
                difficulty="easy",
                board=["DUP", "B", "C", "D", "DUP", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"],
                groups=dupe_groups,
            )


class TestGuessing:
    def test_correct_guess(self, puzzle):
        result = puzzle.guess(["POODLE", "BEAGLE", "PUG", "CORGI"])
        assert result.result == GuessResult.CORRECT
        assert result.matched_category == "Dog breeds"
        assert puzzle.mistakes == 0
        assert "Dog breeds" in puzzle.solved_categories
        # Solved words leave the board.
        assert "POODLE" not in puzzle.remaining_words
        assert len(puzzle.remaining_words) == 12

    def test_correct_guess_is_case_insensitive_and_order_independent(self, puzzle):
        result = puzzle.guess(["corgi", "pug", "beagle", "poodle"])
        assert result.result == GuessResult.CORRECT

    def test_one_away(self, puzzle):
        result = puzzle.guess(["MARS", "VENUS", "SATURN", "MONDAY"])
        assert result.result == GuessResult.ONE_AWAY
        assert puzzle.mistakes == 1

    def test_incorrect(self, puzzle):
        result = puzzle.guess(["POODLE", "MARS", "CHEESE", "MONDAY"])
        assert result.result == GuessResult.INCORRECT
        assert puzzle.mistakes == 1

    def test_wrong_size_rejected(self, puzzle):
        with pytest.raises(InvalidGuessError):
            puzzle.guess(["POODLE", "BEAGLE", "PUG"])

    def test_duplicate_words_rejected(self, puzzle):
        with pytest.raises(InvalidGuessError):
            puzzle.guess(["POODLE", "POODLE", "PUG", "CORGI"])

    def test_unknown_word_rejected(self, puzzle):
        with pytest.raises(InvalidGuessError):
            puzzle.guess(["POODLE", "BEAGLE", "PUG", "NOTONBOARD"])

    def test_already_solved_word_rejected(self, puzzle):
        puzzle.guess(["POODLE", "BEAGLE", "PUG", "CORGI"])
        with pytest.raises(InvalidGuessError):
            puzzle.guess(["POODLE", "MARS", "VENUS", "SATURN"])


class TestEndStates:
    def test_solving_all_groups(self, puzzle):
        puzzle.guess(["POODLE", "BEAGLE", "PUG", "CORGI"])
        puzzle.guess(["MARS", "VENUS", "SATURN", "NEPTUNE"])
        puzzle.guess(["CHEESE", "MUSHROOM", "PEPPERONI", "OLIVE"])
        puzzle.guess(["MONDAY", "FRIDAY", "SUNDAY", "TUESDAY"])
        assert puzzle.is_solved
        assert puzzle.validate_all()
        assert not puzzle.remaining_words

    def test_running_out_of_guesses(self, puzzle):
        wrong_guesses = [
            ["POODLE", "MARS", "CHEESE", "MONDAY"],
            ["BEAGLE", "VENUS", "MUSHROOM", "FRIDAY"],
            ["PUG", "SATURN", "PEPPERONI", "SUNDAY"],
            ["CORGI", "NEPTUNE", "OLIVE", "TUESDAY"],
        ]
        for g in wrong_guesses:
            puzzle.guess(g)
        assert puzzle.is_failed
        assert puzzle.is_over
        with pytest.raises(GameOverError):
            puzzle.guess(["POODLE", "BEAGLE", "PUG", "CORGI"])


class TestHistory:
    def test_undo_correct_guess(self, puzzle):
        puzzle.guess(["POODLE", "BEAGLE", "PUG", "CORGI"])
        assert len(puzzle.solved) == 1
        puzzle.undo()
        assert len(puzzle.solved) == 0
        assert "POODLE" in puzzle.remaining_words

    def test_undo_wrong_guess(self, puzzle):
        puzzle.guess(["POODLE", "MARS", "CHEESE", "MONDAY"])
        assert puzzle.mistakes == 1
        puzzle.undo()
        assert puzzle.mistakes == 0

    def test_undo_with_no_history_raises(self, puzzle):
        with pytest.raises(GameOverError):
            puzzle.undo()

    def test_reset(self, puzzle):
        puzzle.guess(["POODLE", "BEAGLE", "PUG", "CORGI"])
        puzzle.guess(["MARS", "MONDAY", "CHEESE", "OLIVE"])
        puzzle.reset()
        assert puzzle.mistakes == 0
        assert not puzzle.solved_categories
        assert not puzzle.guesses
        assert puzzle.remaining_words == puzzle.board


class TestReveal:
    def test_reveal_group(self, puzzle):
        puzzle.reveal_group("Planets")
        assert "Planets" in puzzle.solved_categories
        assert puzzle.mistakes == 0  # revealing is free

    def test_reveal_all(self, puzzle):
        puzzle.reveal_all()
        assert puzzle.is_solved
        assert puzzle.mistakes == 0


class TestDataFiles:
    @pytest.mark.parametrize("tier", ["easy", "medium", "hard", "cryptic"])
    def test_every_puzzle_loads_and_is_consistent(self, tier):
        puzzles = load_puzzles(f"data/{tier}.json")
        assert puzzles, f"{tier} has no puzzles"
        for p in puzzles:
            # Construction already validated the puzzle; sanity-check solvability
            # by revealing every group via the answer key.
            for group in p.groups:
                assert p.guess(list(group.members)).result == GuessResult.CORRECT
            assert p.validate_all()

    def test_load_single_puzzle_by_index(self):
        first = load_puzzle("data/easy.json", index=0)
        assert first.id == "easy-1"
        with pytest.raises(IndexError):
            load_puzzle("data/easy.json", index=99)


@pytest.mark.skip(reason="Your task: write a solver, then wire it up here and remove the skip.")
class TestSolver:
    """Placeholder for the solver you'll build. Import your solver below, run it
    against each puzzle, and assert it solves them."""

    @pytest.mark.parametrize("tier", ["easy", "medium", "hard", "cryptic"])
    def test_solver_completes_puzzles(self, tier):
        # from your_solver import solve   # <- your solver
        for puzzle in load_puzzles(f"data/{tier}.json"):
            solve(puzzle)  # noqa: F821 — wire up your own solver
            assert puzzle.validate_all()
