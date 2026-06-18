# LLM Connections Solver Challenge

Build an LLM-powered solver for [Connections](https://www.nytimes.com/games/connections): a board
of **16 words** that splits into **4 hidden groups of 4** by a shared theme.

```
PEPPERONI  CHEESE   PUG      BEAGLE
TUESDAY    MONDAY   POODLE   SATURN
MUSHROOM   MARS     CORGI    OLIVE
FRIDAY     VENUS    NEPTUNE  SUNDAY
```
<sub>(Dog breeds · Planets · Pizza toppings · Days of the week)</sub>

**Format:** ~1 hour solo coding, then ~1 hour pairing. AI-assisted coding is allowed. There's no
single right answer — aim for clean, reliable code and be ready to discuss tradeoffs.

## Setup

Uses [uv](https://docs.astral.sh/uv/). Run from the repo root:

```bash
uv sync                       # install deps + the `connections` command
cp .env.example .env          # add the Azure OpenAI values you were given
uv run pytest                 # verify the engine
uv run connections            # play the easy puzzle yourself
```

## Your task

Write a solver that reads a puzzle's board and works out the four groups. The engine is provided:

```python
from connections import load_puzzle

puzzle = load_puzzle("data/easy.json")   # tiers: easy, medium, hard, cryptic

puzzle.board            # the 16 words — solve from these
puzzle.remaining_words  # words not yet in a solved group
puzzle.guess([...])     # guess 4 words -> Guess(result=...)
puzzle.is_solved        # all four groups found?
puzzle.validate_all()   # True once solved
```

`guess(...)` returns `correct` (group solved), `one_away` (3 of 4 right — a mistake), or
`incorrect` (a mistake). You get four mistakes (`puzzle.max_mistakes`) before the game ends.

> **Don't peek:** the answer key is in `puzzle.groups` — use it only to check yourself, not while
> solving.

Start on `data/easy.json` and get a basic solve working — but **that's the warm-up, not the
bar.** Easy and medium often fall to a single well-prompted call; the interesting engineering is
what happens when the model is wrong. Push into the harder tiers (two puzzles each): `medium` adds
trap words, `hard` adds overlapping traps where only one full partition works, and `cryptic` uses
wordplay (hidden words, homophones, reversals) that defeats a naive prompt.

We're looking for how you turn an unreliable model into a reliable solver — candidate generation,
using the `guess` feedback (especially `one_away`) to recover, resolving conflicts between groups,
and clean, well-structured code. You won't necessarily finish every tier; be ready to explain how
you'd get there. Structure your code however you like.

## Talking to the model

All LLM calls go through `connections/llm.py` (Azure OpenAI, `gpt-4o` deployment by default):

```python
from connections.llm import complete, parse
from pydantic import BaseModel

text = complete("...")                    # free-form text

class Grouping(BaseModel):                 # structured output, guaranteed to match the schema
    category: str
    words: list[str]

grouping = parse("Group these words: ...", Grouping)
```

## Play in the terminal

```bash
uv run connections --tier hard            # type 4 words per guess; q to quit
```

## Layout

```
data/                 easy/medium/hard/cryptic puzzles (with answers)
src/connections/      installable package
  puzzle.py           ConnectionsPuzzle engine (board, guess, ...)
  types.py            Group, Guess, Level, Difficulty
  utils.py            load_puzzle / load_puzzles
  llm.py              Azure OpenAI wrapper (complete / parse)
  cli.py              the `connections` command
tests/                engine tests (run with `uv run pytest`)
```
