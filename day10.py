from functools import cache

import numpy as np

from advent_utils import read_input, timer

InputData = np.ndarray

Loc = tuple[int, int]

START_ELEVATION = 0
END_ELEVATION = 9

DIRECTIONS = [
    (-1, 0),  # up
    (0, 1),  # right
    (1, 0),  # down
    (0, -1),  # left
]


def get_parsed_input() -> InputData:
    input_raw = read_input(10)
    input_parsed = np.array([
        list(map(int, line.strip()))
        for line in input_raw.strip().splitlines()
    ])
    return input_parsed


class Solver:
    def __init__(self, grid: np.ndarray):
        super().__init__()
        if len(grid.shape) != 2:
            raise ValueError("grid must be 2-dimensional")
        self.grid = grid

    @property
    def n_rows(self) -> int:
        return self.grid.shape[0]

    @property
    def n_cols(self) -> int:
        return self.grid.shape[1]

    def is_loc_in_bounds(self, loc: Loc) -> bool:
        return 0 <= loc[0] < self.n_rows and 0 <= loc[1] < self.n_cols

    @cache
    def _find_trails_recursive(self, loc: Loc) -> tuple[set[Loc], int]:
        current_elevation = self.grid[loc]
        if current_elevation == END_ELEVATION:
            return {loc}, 1
        trail_ends = set()
        n_paths = 0
        next_elevation = current_elevation + 1
        for direction in DIRECTIONS:
            next_loc = (loc[0] + direction[0], loc[1] + direction[1])
            if self.is_loc_in_bounds(next_loc) and self.grid[next_loc] == next_elevation:
                new_trail_ends, n_paths_new = self._find_trails_recursive(next_loc)
                trail_ends.update(new_trail_ends)
                n_paths += n_paths_new
        return trail_ends, n_paths

    def solve(self) -> tuple[int, int]:
        trailhead_sum1 = 0
        trailhead_sum2 = 0
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                loc = (i, j)
                if self.grid[loc] == START_ELEVATION:
                    trail_ends, n_paths = self._find_trails_recursive(loc)
                    trailhead_sum1 += len(trail_ends)
                    trailhead_sum2 += n_paths
        return trailhead_sum1, trailhead_sum2


def main(input_parsed: InputData):
    trailhead_sum1, trailhead_sum2 = Solver(input_parsed).solve()
    print(f"{trailhead_sum1 = }")
    print(f"{trailhead_sum2 = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
