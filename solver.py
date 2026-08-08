"""
Sudoku Solver — Constraint Satisfaction Problem (CSP) formulation
===================================================================

Author: Anil Kumar Javisetty

Sudoku is modeled here as a classic CSP:

    Variables   : the 81 cells of the 9x9 grid
    Domains     : {1..9} for empty cells, a fixed singleton for
                  cells that are already filled in the puzzle
    Constraints : all-different across every row, every column,
                  and every 3x3 box (27 all-different constraints
                  in total)

The solver combines three standard CSP techniques:

    1. Backtracking search        — depth-first search over variable
                                     assignments, undoing a choice
                                     whenever it leads to a dead end.
    2. Minimum Remaining Values   — at every step, assign the empty
       (MRV) heuristic              cell with the fewest legal values
                                     left. This fails fast and prunes
                                     the search tree aggressively.
    3. Forward checking           — whenever a cell is assigned,
                                     immediately remove that value
                                     from the domains of every peer
                                     (same row/col/box). If a peer's
                                     domain becomes empty, backtrack
                                     right away instead of discovering
                                     the conflict later.

Run this file directly to solve a sample puzzle and see solver stats
(cells assigned, backtracks made, and time taken).
"""

from __future__ import annotations
import time
import copy
from typing import Optional


GRID_SIZE = 9
BOX_SIZE = 3


class SudokuCSP:
    """A Sudoku puzzle represented and solved as a CSP."""

    def __init__(self, puzzle: list[list[int]]):
        """
        puzzle: 9x9 list of lists, 0 represents an empty cell.
        """
        self.puzzle = puzzle
        self.domains: dict[tuple[int, int], set[int]] = {}
        self.assignments = 0
        self.backtracks = 0
        self._init_domains()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    def _init_domains(self) -> None:
        """Build the initial domain for every cell, respecting the
        constraints already implied by the given clues."""
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                value = self.puzzle[r][c]
                if value != 0:
                    self.domains[(r, c)] = {value}
                else:
                    self.domains[(r, c)] = set(range(1, 10))

        # Propagate the fixed clues once up front so the search
        # starts from a already-pruned domain set.
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.puzzle[r][c] != 0:
                    self._forward_check((r, c), self.puzzle[r][c])

    @staticmethod
    def _peers(cell: tuple[int, int]) -> set[tuple[int, int]]:
        """All cells that share a row, column, or box with `cell`
        (i.e. every cell an all-different constraint links it to)."""
        r, c = cell
        peers = set()
        for i in range(GRID_SIZE):
            peers.add((r, i))
            peers.add((i, c))
        box_r, box_c = (r // BOX_SIZE) * BOX_SIZE, (c // BOX_SIZE) * BOX_SIZE
        for i in range(box_r, box_r + BOX_SIZE):
            for j in range(box_c, box_c + BOX_SIZE):
                peers.add((i, j))
        peers.discard(cell)
        return peers

    # ------------------------------------------------------------------
    # Constraint propagation
    # ------------------------------------------------------------------
    def _forward_check(self, cell: tuple[int, int], value: int) -> list[tuple[int, int]]:
        """Remove `value` from the domain of every peer of `cell`.
        Returns the list of peers that were actually changed, so the
        caller can undo this exact pruning on backtrack."""
        pruned = []
        for peer in self._peers(cell):
            if value in self.domains[peer]:
                self.domains[peer].discard(value)
                pruned.append(peer)
                # if this empties a peer's domain, `solve()` notices
                # via the length check right after calling us and
                # backtracks immediately instead of recursing deeper
        return pruned

    def _undo_forward_check(self, pruned: list[tuple[int, int]], value: int) -> None:
        for peer in pruned:
            self.domains[peer].add(value)

    # ------------------------------------------------------------------
    # MRV heuristic
    # ------------------------------------------------------------------
    def _select_unassigned_cell(self) -> Optional[tuple[int, int]]:
        """Pick the empty cell with the smallest domain (Minimum
        Remaining Values). Ties broken by earliest row/col."""
        best_cell = None
        best_size = 10
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.puzzle[r][c] == 0:
                    size = len(self.domains[(r, c)])
                    if size < best_size:
                        best_size = size
                        best_cell = (r, c)
                        if best_size == 1:
                            return best_cell
        return best_cell

    # ------------------------------------------------------------------
    # Backtracking search
    # ------------------------------------------------------------------
    def solve(self) -> bool:
        """Solve in place. Returns True if a solution was found."""
        cell = self._select_unassigned_cell()
        if cell is None:
            return True  # every cell filled -> solved

        r, c = cell
        # copy so we can try each candidate value cleanly
        for value in sorted(self.domains[cell]):
            if not self._is_consistent(cell, value):
                continue

            self.puzzle[r][c] = value
            self.assignments += 1
            old_domain = self.domains[cell]
            self.domains[cell] = {value}
            pruned = self._forward_check(cell, value)

            # if forward checking wiped out any peer's domain, this
            # branch is a dead end -> prune immediately
            if all(len(self.domains[p]) > 0 for p in pruned) and self.solve():
                return True

            # undo and try the next candidate
            self._undo_forward_check(pruned, value)
            self.domains[cell] = old_domain
            self.puzzle[r][c] = 0
            self.backtracks += 1

        return False

    def _is_consistent(self, cell: tuple[int, int], value: int) -> bool:
        r, c = cell
        for i in range(GRID_SIZE):
            if self.puzzle[r][i] == value or self.puzzle[i][c] == value:
                return False
        box_r, box_c = (r // BOX_SIZE) * BOX_SIZE, (c // BOX_SIZE) * BOX_SIZE
        for i in range(box_r, box_r + BOX_SIZE):
            for j in range(box_c, box_c + BOX_SIZE):
                if self.puzzle[i][j] == value:
                    return False
        return True


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------
def print_grid(grid: list[list[int]]) -> None:
    for r in range(GRID_SIZE):
        if r % BOX_SIZE == 0 and r != 0:
            print("-" * 21)
        row = []
        for c in range(GRID_SIZE):
            if c % BOX_SIZE == 0 and c != 0:
                row.append("|")
            row.append(str(grid[r][c]) if grid[r][c] != 0 else ".")
        print(" ".join(row))


def is_valid_solution(grid: list[list[int]]) -> bool:
    for i in range(GRID_SIZE):
        row = [v for v in grid[i] if v != 0]
        col = [grid[r][i] for r in range(GRID_SIZE) if grid[r][i] != 0]
        if len(set(row)) != len(row) or len(set(col)) != len(col):
            return False
    for br in range(0, GRID_SIZE, BOX_SIZE):
        for bc in range(0, GRID_SIZE, BOX_SIZE):
            box = [
                grid[r][c]
                for r in range(br, br + BOX_SIZE)
                for c in range(bc, bc + BOX_SIZE)
                if grid[r][c] != 0
            ]
            if len(set(box)) != len(box):
                return False
    return True


# --------------------------------------------------------------------
# Demo
# --------------------------------------------------------------------
SAMPLE_PUZZLE = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

if __name__ == "__main__":
    puzzle = copy.deepcopy(SAMPLE_PUZZLE)

    print("Puzzle:")
    print_grid(puzzle)
    print()

    csp = SudokuCSP(puzzle)
    start = time.perf_counter()
    solved = csp.solve()
    elapsed = time.perf_counter() - start

    print("Solved!" if solved else "No solution found.")
    print_grid(csp.puzzle)
    print()
    print(f"Valid solution : {is_valid_solution(csp.puzzle)}")
    print(f"Assignments    : {csp.assignments}")
    print(f"Backtracks     : {csp.backtracks}")
    print(f"Time taken     : {elapsed*1000:.2f} ms")
