"""
Getting-started script for the Connections challenge.

Run with:  uv run python main.py

It walks through the puzzle engine's API (the part we provide) and finishes with
a quick check that your Azure OpenAI credentials work. Your job is to write the *solver* —
the code that reads the board and works out the four groups by calling
``puzzle.guess(...)``. See the README for the task.
"""
from src.connections import load_puzzle
from src.connections.llm import hello_world

# Load the first easy puzzle. The answer key lives in `puzzle.groups`, but a
# solver shouldn't read it — solve using `puzzle.board` + `puzzle.guess(...)`.
puzzle = load_puzzle("data/easy.json")

print("--- The board (16 words to group into 4) ---")
print(puzzle.board)

print("\n--- Pretty-printed puzzle ---")
print(puzzle)

print("\n--- An incorrect guess (no group shares 3 of these) ---")
result = puzzle.guess(["POODLE", "MARS", "CHEESE", "MONDAY"])
print(f"result: {result.result.value}  (mistakes: {puzzle.mistakes}/{puzzle.max_mistakes})")

print("\n--- A 'one away' guess (3 of 4 correct) ---")
result = puzzle.guess(["MARS", "VENUS", "SATURN", "MONDAY"])
print(f"result: {result.result.value}  (mistakes: {puzzle.mistakes}/{puzzle.max_mistakes})")

print("\n--- Undo that guess ---")
puzzle.undo()
print(f"mistakes after undo: {puzzle.mistakes}/{puzzle.max_mistakes}")

print("\n--- A correct guess ---")
result = puzzle.guess(["POODLE", "BEAGLE", "PUG", "CORGI"])
print(f"result: {result.result.value}  (matched: {result.matched_category})")
print(puzzle)

print("\n--- Reveal the rest (for checking — costs no guesses) ---")
puzzle.reveal_all()
print(f"solved? {puzzle.validate_all()}")
print(puzzle)

print("\n--- Reset back to the start ---")
puzzle.reset()
print(f"remaining words: {len(puzzle.remaining_words)}  ·  solved: {len(puzzle.solved)}")

print("\n--- LLM hello world ---")
try:
    print(hello_world())
except Exception as e:  # noqa: BLE001 — surface any setup issue plainly
    print(f"(LLM call skipped: {type(e).__name__}: {e})")
    print("Set the Azure OpenAI values in .env to enable the model — see .env.example.")
