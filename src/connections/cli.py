"""
Play Connections in your terminal (the `connections` command).

You're shown the 16 jumbled words as a 4x4 grid and enter four words per guess. A
correct guess snaps those words up into the next solved row, coloured with that
group's colour (yellow / green / blue / purple).

    uv run connections                          # first easy puzzle
    uv run connections --tier hard              # a harder tier
    uv run connections --tier cryptic --index 1
"""
from pathlib import Path
from typing import List, Optional

import typer
from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from . import (
    ConnectionsPuzzle,
    Guess,
    GuessResult,
    InvalidGuessError,
    Level,
    load_puzzle,
)

console = Console()

# Puzzle data lives at the repo root, alongside the `src/` package.
DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# Each group's within-puzzle level maps to a fixed, unique colour.
PALETTE = {
    Level.BLUE: "blue",
    Level.PURPLE: "purple",
    Level.GREEN: "green",
    Level.YELLOW: "yellow",
}

QUIT_WORDS = {"q", "quit", "exit"}


def build_grid(puzzle: ConnectionsPuzzle) -> Table:
    """Render the board as a 4x4 grid: solved groups as coloured rows on top,
    the remaining jumbled words filling the rows below."""
    cell_width = max(len(w) for w in puzzle.board) + 2

    table = Table(show_header=False, box=box.HEAVY, padding=(0, 1))
    for _ in range(4):
        table.add_column(justify="center", min_width=cell_width)

    for group in puzzle.solved:
        table.add_row(*group.members, style=f"bold white on {PALETTE[group.level]}")

    remaining = puzzle.remaining_words
    for i in range(0, len(remaining), 4):
        table.add_row(*remaining[i : i + 4])

    return table


def render(puzzle: ConnectionsPuzzle, message: Optional[Text] = None) -> None:
    """Draw the screen: title, grid, mistake tracker, last message."""
    if console.is_terminal:
        console.clear()

    title = "Connections" + (f" — {puzzle.title}" if puzzle.title else "")
    console.print(Text(title, style="bold"), justify="center")
    console.print(Text(f"[{puzzle.difficulty.value}] {puzzle.id}", style="dim"), justify="center")
    console.print()
    console.print(build_grid(puzzle), justify="center")
    console.print()

    used, total = puzzle.mistakes, puzzle.max_mistakes
    dots = Text("Mistakes  ", style="dim")
    dots.append("●" * (total - used), style="green")
    dots.append("●" * used, style="red")
    console.print(dots, justify="center")

    if message is not None:
        console.print()
        console.print(message, justify="center")


def parse_guess(raw: str) -> List[str]:
    """Split a line like 'pug, beagle corgi poodle' into four upper-cased words."""
    return [w for w in raw.replace(",", " ").upper().split() if w]


def feedback_text(puzzle: ConnectionsPuzzle, guess: Guess) -> Text:
    """A coloured one-liner describing a guess's outcome."""
    if guess.result == GuessResult.CORRECT:
        colour = PALETTE[puzzle.find_group(guess.matched_category).level]
        return Text(f"✓ Correct — {guess.matched_category}!", style=f"bold {colour}")
    if guess.result == GuessResult.ONE_AWAY:
        return Text(f"So close — one away: {', '.join(guess.words)}", style="yellow")
    return Text(f"Not a group: {', '.join(guess.words)}", style="red")


def play(
    tier: str = typer.Option("easy", help="Puzzle tier: easy, medium, hard, or cryptic."),
    index: int = typer.Option(0, help="Which puzzle in the tier (0-based)."),
) -> None:
    """Play a Connections puzzle one guess at a time."""
    try:
        puzzle = load_puzzle(str(DATA_DIR / f"{tier}.json"), index)
    except (FileNotFoundError, IndexError) as e:
        console.print(f"[red]Could not load puzzle:[/red] {e}")
        raise typer.Exit(code=1)

    message: Optional[Text] = Text(
        "Enter four words (space or comma separated). Type 'q' to quit.", style="dim"
    )
    while not puzzle.is_over:
        render(puzzle, message)
        try:
            raw = console.input("\n[bold]Your guess > [/bold]")
        except (EOFError, KeyboardInterrupt):
            console.print("\nBye!")
            raise typer.Exit()

        if raw.strip().lower() in QUIT_WORDS:
            console.print("\nBye!")
            raise typer.Exit()

        words = parse_guess(raw)
        if len(words) != 4:
            message = Text(f"Enter exactly 4 words (got {len(words)}).", style="yellow")
            continue

        try:
            guess = puzzle.guess(words)
        except InvalidGuessError as e:
            message = Text(str(e), style="yellow")
            continue

        message = feedback_text(puzzle, guess)

    # Game over: reveal the answers if the player ran out of guesses.
    if puzzle.is_solved:
        outcome = Text(f"Solved in {puzzle.mistakes} mistake(s)! 🎉", style="bold green")
    else:
        puzzle.reveal_all()
        outcome = Text("Out of guesses — here's the solution.", style="bold red")
    render(puzzle, outcome)
    console.print()


def main() -> None:
    """Console-script entry point (``connections``)."""
    typer.run(play)


if __name__ == "__main__":
    main()
