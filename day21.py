import itertools
import re
from functools import cache
from typing import Iterable, cast

import numpy as np

from advent_utils import GridCardinalDirection, Loc, read_input, timer

InputData = list[str]
KeypadSymbol = str | GridCardinalDirection


def get_parsed_input() -> InputData:
    input_raw = read_input(21)
    return input_raw.splitlines()


def _create_keypad_lookup(keypad: np.ndarray) -> dict[KeypadSymbol, Loc]:
    n_rows, n_cols = keypad.shape
    return {
        sym: loc
        for i in range(n_rows)
        for j in range(n_cols)
        if (sym := cast(KeypadSymbol, keypad[loc := Loc(i, j)])) is not None
    }


NUMERIC_KEYPAD = np.array([
    ["7", "8", "9"],
    ["4", "5", "6"],
    ["1", "2", "3"],
    [None, "0", "A"],
])
NUMERIC_KEYPAD_START = Loc(3, 2)

DIRECTIONAL_KEYPAD = np.array([
    [None, GridCardinalDirection.UP, "A"],
    [GridCardinalDirection.LEFT, GridCardinalDirection.DOWN, GridCardinalDirection.RIGHT],
])
DIRECTIONAL_KEYPAD_START = Loc(0, 2)


class Pathfinder:
    # this class is stateless so we can take full advantage of caching on `shortest_paths`
    def __init__(self, keypad: np.ndarray, start_loc: Loc):
        super().__init__()
        if len(keypad.shape) != 2:
            raise ValueError("Keypad must be 2-dimensional")
        self.keypad = keypad
        self._keypad_lookup = _create_keypad_lookup(keypad)
        self.start_loc = start_loc

    def is_loc_in_bounds(self, loc: Loc) -> bool:
        n_rows, n_cols = self.keypad.shape
        return (0 <= loc.row < n_rows) and (0 <= loc.col < n_cols) and (self.keypad[loc] is not None)

    def loc_of_symbol(self, sym: KeypadSymbol) -> Loc:
        try:
            return self._keypad_lookup[sym]
        except KeyError:
            raise RuntimeError(f"Symbol {sym} not found on this keypad: {self.keypad}")

    @cache
    def path_stays_in_bounds(self, start_loc: Loc, path: tuple[GridCardinalDirection, ...]) -> bool:
        if not self.is_loc_in_bounds(start_loc):
            return False
        loc = start_loc
        for direction in path:
            loc = loc.shift(direction.value)
            if not self.is_loc_in_bounds(loc):
                return False
        return True

    @cache
    def shortest_paths(self, loc_start: Loc, loc_end: Loc) -> set[tuple[GridCardinalDirection, ...]]:
        if not self.is_loc_in_bounds(loc_start) or not self.is_loc_in_bounds(loc_end):
            raise ValueError("loc_start and loc_end must both be in-bounds")
        if loc_start == loc_end:
            return {tuple()}
        row_shift = loc_end.row - loc_start.row
        col_shift = loc_end.col - loc_start.col
        # base cases
        if row_shift == 0:
            if col_shift > 0:
                return {(GridCardinalDirection.RIGHT,) * col_shift}
            elif col_shift < 0:
                return {(GridCardinalDirection.LEFT,) * abs(col_shift)}
            else:
                raise ValueError("goof")
        if col_shift == 0:
            if row_shift > 0:
                return {(GridCardinalDirection.DOWN,) * row_shift}
            elif row_shift < 0:
                return {(GridCardinalDirection.UP,) * abs(row_shift)}
            else:
                raise ValueError("goof")
        # more complex movement
        row_direction = GridCardinalDirection.DOWN if row_shift > 0 else GridCardinalDirection.UP
        col_direction = GridCardinalDirection.RIGHT if col_shift > 0 else GridCardinalDirection.LEFT
        all_paths = set(itertools.permutations(([row_direction] * abs(row_shift)) + ([col_direction] * abs(col_shift))))
        paths_n_turns = {
            path: sum(a != b for a, b in itertools.pairwise(path))
            for path in all_paths
        }
        min_turns = min(paths_n_turns.values())
        reasonable_paths = {
            path
            for path, n_turns in paths_n_turns.items()
            if n_turns <= min_turns and self.path_stays_in_bounds(loc_start, path)
        }
        return reasonable_paths


PATHFINDER_NUMERIC = Pathfinder(NUMERIC_KEYPAD, NUMERIC_KEYPAD_START)
PATHFINDER_DIRECTIONAL = Pathfinder(DIRECTIONAL_KEYPAD, DIRECTIONAL_KEYPAD_START)


def all_possible_sequences(sequence_of_segment_options: list[set[tuple[KeypadSymbol, ...]]]) -> Iterable[tuple[KeypadSymbol, ...]]:
    n_segments = len(sequence_of_segment_options)
    if n_segments == 0:
        return
    if n_segments == 1:
        yield from sequence_of_segment_options[0]
        return
    these_options, *remaining_segments_options = sequence_of_segment_options
    for segment in these_options:
        for sequence_remainder_option in all_possible_sequences(remaining_segments_options):
            yield segment + sequence_remainder_option


class RobotSystem:
    def __init__(self, n_robots: int):
        super().__init__()
        if n_robots < 1:
            raise ValueError("n_robots must be >= 1")
        self.pathfinders = [PATHFINDER_NUMERIC] + ([PATHFINDER_DIRECTIONAL] * (n_robots - 1))

    def min_presses_for_code(self, code: tuple[str]) -> int:
        best_sequences: set[tuple[KeypadSymbol, ...]] = {code}
        for pathfinder in self.pathfinders:
            best_sequences_new = set()
            best_length: int | None = None
            for sequence in best_sequences:
                sequence_locs = [pathfinder.start_loc] + [pathfinder.loc_of_symbol(sym) for sym in sequence]
                sequence_of_segment_options = [
                    {
                        cast(tuple[GridCardinalDirection, ...], path + ("A",))
                        for path in pathfinder.shortest_paths(loc_a, loc_b)
                    }
                    for loc_a, loc_b in itertools.pairwise(sequence_locs)
                ]
                for sequence_option in all_possible_sequences(sequence_of_segment_options):
                    new_length = len(sequence_option)
                    if best_length is None or new_length < best_length:
                        best_length = new_length
                        best_sequences_new = {sequence_option}
                    elif new_length == best_length:
                        best_sequences_new.add(sequence_option)
                    # else: too long; ignore it
            best_sequences = best_sequences_new
        return min(len(s) for s in best_sequences)


def solve(codes: InputData, *, n_robots: int) -> int:
    total = 0
    robots = RobotSystem(n_robots=n_robots)  # TODO: should this be initialized inside the loop?
    for code in codes:
        min_presses = robots.min_presses_for_code(tuple(code))
        code_num = int(re.match(r"\d+", code).group())
        total += min_presses * code_num
    return total


def main(input_parsed: InputData):
    score1 = solve(input_parsed, n_robots=3)
    print(f"{score1 = }")
    score2 = solve(input_parsed, n_robots=26)
    print(f"{score2 = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
