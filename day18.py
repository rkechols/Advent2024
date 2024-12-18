from typing import Iterable

import numpy as np

from advent_utils import GridCardinalDirection, GridSolver, Loc, read_input, timer

InputData = list[Loc]


def get_parsed_input() -> InputData:
    input_raw = read_input(18)
    input_parsed = [
        Loc(*map(int, reversed(line.strip().split(","))))
        for line in input_raw.strip().splitlines()
    ]
    return input_parsed


class Solver(GridSolver):
    def __init__(self):
        super().__init__(np.ones((71, 71), dtype=bool))
        self.start_loc = Loc(0, 0)
        self.end_loc = Loc(self.n_rows - 1, self.n_cols - 1)

    def place_corruption(self, corruption_loc: Loc):
        self.grid[corruption_loc] = False

    def place_corruptions(self, corruptions: Iterable[Loc]):
        for corruption_loc in corruptions:
            self.place_corruption(corruption_loc)

    def solve_min_distance(self) -> int | None:
        if self.start_loc == self.end_loc:
            return 0
        all_visited = set()
        to_search = {self.start_loc}
        n_steps = 0
        while len(to_search) > 0:
            n_steps += 1
            to_search_next = set()
            for loc in to_search:
                all_visited.add(loc)
                for direction in GridCardinalDirection.values():
                    next_loc = loc.shift(direction)
                    if next_loc == self.end_loc:
                        return n_steps
                    if self.is_loc_in_bounds(next_loc) and self.grid[next_loc] and next_loc not in all_visited:
                        to_search_next.add(next_loc)
            to_search = to_search_next
        return None


def find_first_total_blocker(corruption_order: InputData) -> Loc:
    lower = 0
    upper = len(corruption_order)
    while (search_width := upper - lower) > 1:
        target = lower + (search_width // 2)
        solver = Solver()
        solver.place_corruptions(corruption_order[:target])
        if solver.solve_min_distance() is None:  # no path; too high
            upper = target
        else:  # yes path; too low
            lower = target

    final_solver = Solver()
    final_solver.place_corruptions(corruption_order[:lower])
    if final_solver.solve_min_distance() is None:
        raise RuntimeError("algorithm error: supposed answer is not actually the first total blocker")
    final_solver.place_corruption(corruption_order[lower])
    if final_solver.solve_min_distance() is not None:
        raise ValueError("algorithm error: supposed answer is not actually a total blocker")
    return corruption_order[lower]


def main(input_parsed: InputData):
    # part 1
    solver = Solver()
    solver.place_corruptions(input_parsed[:1024])
    min_distance = solver.solve_min_distance()
    print(f"{min_distance = }")
    # part 2
    corruption_loc  = find_first_total_blocker(input_parsed)
    print(f"first totally-blocking corruption: {corruption_loc.col},{corruption_loc.row}")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
