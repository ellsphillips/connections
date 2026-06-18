# Interviewer notes

> Internal — not for the candidate. A full reference solution lives on the **`solution`** branch
> (`git switch solution`): a working LLM solver, `connections --auto` to watch it play, and the
> puzzle generator. Don't hand that branch out.

## What this challenge tests

Turning an **unreliable LLM into a reliable solver**. The model proposes groupings; the engine is
ground truth. The signal is in the loop, not the first prompt:

- **LLM integration** — sensible prompts, structured output (`llm.parse`) over brittle string parsing.
- **Closing the loop** — using `guess` feedback (`correct` / `one_away` / `incorrect`) to recover,
  especially acting on `one_away` (three of four are right — swap one).
- **Constraint handling** — four disjoint groups of four; resolving words that fit multiple groups.
- **Judgement** — guessing the most-confident group first to protect the 4-mistake budget.
- **Code quality & communication** — clean structure, and being able to explain tradeoffs.

## Difficulty profile (reference solver, gpt-4o, naive propose→verify loop)

| Tier | Result |
|------|--------|
| easy | solved, 0 mistakes |
| medium | solved, 0–1 mistakes |
| hard | one solved cleanly, one failed |
| cryptic | one failed, one scraped through |

So easy/medium are near-trivial (often a single call) — **don't read much into a candidate solving
them.** `hard` rewards conflict resolution; `cryptic` (hidden words, homophones, reversals) defeats
naive prompting and is the real stretch / discussion driver. Not finishing every tier is expected.

## What good looks like

- Builds a loop, not a one-shot: re-prompts (or re-plans) after a wrong/`one_away` guess.
- Uses structured output and validates the model's groups in code before guessing.
- Has a strategy for traps (confidence ordering, verifying intersections, narrowing as words clear).
- For cryptic: recognises it's wordplay and adapts the prompt (e.g. asks the model to reason about
  each word's properties first).
- Discusses cost/latency, retries, and how they'd evaluate the solver.

## Red flags

- One prompt, paste the answer, no use of feedback.
- Reads `puzzle.groups` (the answer key) in the solver.
- Brittle hand-parsing of model text instead of structured output.
- Raising `max_mistakes` to brute-force via the `guess` oracle rather than improving the model use.

## Pairing-hour directions

- Extend a working easy/medium solver to `hard`, then `cryptic`.
- Improve reliability: self-consistency (sample N proposals, keep recurring groups), a two-stage
  wordplay prompt, or re-proposing after every solved group.
- "How would you evaluate this solver?" / "Where would it break in production?"
