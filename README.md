# Sudoku Solver — Constraint Satisfaction Problem (CSP)

A from-scratch Sudoku solver built around the classic AI formulation of Sudoku as a Constraint Satisfaction Problem, rather than a brute-force grid search.

Live demo: included on my portfolio — enter or generate a puzzle and watch the solver fill it in.

## Problem formulation

| CSP element | Sudoku |
|---|---|
| Variables | the 81 grid cells |
| Domains | {1..9} for each empty cell |
| Constraints | all-different across every row, column, and 3x3 box (27 constraints total) |

## Algorithm

The solver combines three standard CSP techniques instead of plain brute-force backtracking:

1. Backtracking search — depth-first search over cell assignments, undoing a choice as soon as it leads to a dead end.
2. Minimum Remaining Values (MRV) heuristic — at every step, the solver assigns the empty cell with the fewest legal values left, rather than scanning left-to-right. This fails fast and cuts the search tree down aggressively.
3. Forward checking — the moment a cell is assigned, that value is removed from the domains of every peer (same row/column/box). If a peer's domain empties out, the solver backtracks immediately instead of discovering the conflict several moves later.

Together, MRV + forward checking is what takes this from "technically works" to "solves in milliseconds" — see benchmark below.

## Results

| Puzzle | Assignments | Backtracks | Time |
|---|---|---|---|
| Easy (46 clues) | 51 | 0 | ~1.3 ms |
| Arto Inkala's "World's Hardest Sudoku" (21 clues) | 13,810 | 13,750 | ~168 ms |

## Run it yourself

python3 solver.py

This solves the bundled sample puzzle and prints the board plus solver stats (assignments, backtracks, time taken).

## Use it on your own puzzle

from solver import SudokuCSP

puzzle = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    # ... 9 rows total, 0 = empty cell
]

csp = SudokuCSP(puzzle)
if csp.solve():
    print(csp.puzzle)  # solved in place

## Why this design

A naive backtracking solver (try 1-9 in the next blank cell, left to right) works but explores a much larger search tree. Framing the puzzle explicitly as variables/domains/constraints makes it possible to bolt on MRV and forward checking cleanly — the same techniques general-purpose CSP solvers (scheduling, planning, resource allocation) use in practice.

## Tech

- Pure Python, no external dependencies
- solver.py — the CSP engine
- Browser demo (on my portfolio) — the same MRV + forward-checking algorithm re-implemented in JavaScript, with the search animated so you can watch the solver work.

---
Built by Anil Kumar Javisetty
