import itertools
from collections import defaultdict

import numpy as np

from advent_utils import Loc, read_input, timer

InputData = tuple[dict[str, set[Loc]], tuple[int, int]]

EMTPY = "."


def get_parsed_input() -> InputData:
    input_raw = read_input(8)
    grid = np.array([
        list(line.strip())
        for line in input_raw.strip().splitlines()
    ])
    input_parsed = defaultdict(set)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            loc = Loc(i, j)
            symbol = grid[loc]
            if symbol != EMTPY:
                input_parsed[symbol].add(loc)
    return input_parsed, grid.shape


class Solver:
    def __init__(self, n_rows: int, n_cols: int, *, any_distance: bool):
        super().__init__()
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.any_distance = any_distance

    def in_bounds(self, loc: Loc | np.ndarray) -> bool:
        return 0 <= loc[0] < self.n_rows and 0 <= loc[1] < self.n_cols

    def get_antinodes(self, antenna_1: Loc, antenna_2: Loc) -> set[Loc]:
        a1 = np.array(antenna_1)
        a2 = np.array(antenna_2)
        vec = a2 - a1  # from a1 to a2
        if self.any_distance:  # part 2
            to_return = {antenna_1, antenna_2}
            antinode = a2 + vec
            while self.in_bounds(antinode):
                to_return.add(Loc(*antinode))
                antinode += vec
            antinode = a1 - vec
            while self.in_bounds(antinode):
                to_return.add(Loc(*antinode))
                antinode -= vec
            return to_return
        else:  # part 1
            to_return = set()
            for antinode in [a2 + vec, a1 - vec]:
                if self.in_bounds(antinode):
                    to_return.add(Loc(*antinode))
            return to_return

    def solve(self, all_antenna_locs: dict[str, set[Loc]]) -> dict[Loc, set[str]]:
        all_antinodes: dict[Loc, set[str]] = defaultdict(set)
        for symbol, antenna_locs in all_antenna_locs.items():
            for antenna_1, antenna_2 in itertools.combinations(antenna_locs, r=2):
                antinodes = self.get_antinodes(antenna_1, antenna_2)
                for antinode in antinodes:
                    all_antinodes[antinode].add(symbol)
        return all_antinodes


def main(input_parsed: InputData):
    all_antenna_locs, (n_rows, n_cols) = input_parsed
    all_antinodes1 = Solver(n_rows, n_cols, any_distance=False).solve(all_antenna_locs)
    print(f"{len(all_antinodes1) = }")
    all_antinodes2 = Solver(n_rows, n_cols, any_distance=True).solve(all_antenna_locs)
    print(f"{len(all_antinodes2) = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
