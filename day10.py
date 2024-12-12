import numpy as np

from advent_utils import GridCardinalDirection, GridSolver, Loc, read_input, timer

InputData = np.ndarray

START_ELEVATION = 0
END_ELEVATION = 9


def get_parsed_input() -> InputData:
    input_raw = read_input(10)
    input_parsed = np.array([
        list(map(int, line.strip()))
        for line in input_raw.strip().splitlines()
    ])
    return input_parsed


class Solver(GridSolver):
    def _find_trails_recursive(self, loc: Loc) -> tuple[set[Loc], int]:
        current_elevation = self.grid[loc]
        if current_elevation == END_ELEVATION:
            return {loc}, 1
        trail_ends = set()
        n_paths = 0
        next_elevation = current_elevation + 1
        for direction in GridCardinalDirection.values():
            next_loc = loc.shift(direction)
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
                loc = Loc(i, j)
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
