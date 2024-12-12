from concurrent.futures import as_completed as futures_as_completed
from concurrent.futures.thread import ThreadPoolExecutor

import numpy as np

from advent_utils import Direction, GridCardinalDirection, GridSolver, Loc, read_input, timer

InputData = tuple[np.ndarray, Loc]

START_MARKER = "^"
WALL = "#"
OPEN = "."


def get_parsed_input() -> InputData:
    input_raw = read_input(6)
    input_lines = input_raw.strip().splitlines()
    grid = np.array([
        [char != WALL for char in line]
        for line in input_lines
    ])
    for i, line in enumerate(input_lines):
        for j, char in enumerate(line):
            if char == START_MARKER:
                start_loc = Loc(i, j)
                return grid, start_loc
    else:
        raise ValueError(f"start marker {START_MARKER!r} not found")


class OffGrid(Exception):
    """raised when the guard goes off the grid"""


class InfiniteLoop(Exception):
    """raised when the guard stays on the grid infinitely"""


class GuardSim(GridSolver):
    def __init__(self, grid: np.ndarray, start_loc: Loc):
        if grid.dtype != np.bool:
            raise TypeError("grid must contain booleans")
        super().__init__(grid)
        self.start_loc = start_loc
        self.current_loc = self.start_loc
        self.current_direction: Direction = GridCardinalDirection.UP.value

    def turn_right(self):
        self.current_direction = self.current_direction.rot_clockwise()

    def step_forward(self) -> bool:
        next_loc = self.current_loc.shift(self.current_direction)
        if not self.is_loc_in_bounds(next_loc):
            raise OffGrid
        if self.grid[next_loc]:  # can step forward
            self.current_loc = next_loc
            return True
        else:  # wall
            return False

    def walk(self) -> set[Loc]:
        history: set[tuple[Loc, Direction]] = set()
        history.add((self.current_loc, self.current_direction))
        while True:
            try:
                could_step = self.step_forward()
            except OffGrid:
                return {loc for loc, _ in history}
            if not could_step:  # hit a wall
                self.turn_right()
            new_history_entry = (self.current_loc, self.current_direction)
            if new_history_entry in history:  # doomed to repeat itself, as they say
                raise InfiniteLoop
            history.add(new_history_entry)


def is_infinite_loop(grid: np.ndarray, start_loc: Loc, *, loc_modification: Loc) -> bool:
    grid_modified = grid.copy()
    grid_modified[loc_modification] = False  # place an obstacle
    modified_guard_sim = GuardSim(grid_modified, start_loc)
    try:
        modified_guard_sim.walk()
    except InfiniteLoop:
        return True
    else:
        return False


def main(input_parsed: InputData, *, use_threads: bool = True):
    grid, start_loc = input_parsed
    # part 1
    initial_guard_sim = GuardSim(grid, start_loc)
    locs_visited = initial_guard_sim.walk()
    print(f"{len(locs_visited) = }")
    # part 2
    print(f"{use_threads = }")
    locs_to_modify = locs_visited - {start_loc}
    if use_threads:
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(is_infinite_loop, grid, start_loc, loc_modification=loc_modification)
                for loc_modification in locs_to_modify
            ]
            infinite_loops_count = sum(
                future.result()
                for future in futures_as_completed(futures)
            )
    else:
        infinite_loops_count = sum(
            is_infinite_loop(grid, start_loc, loc_modification=loc_modification)
            for loc_modification in locs_to_modify
        )
    print(f"{infinite_loops_count = }")


if __name__ == "__main__":
    from argparse import ArgumentParser
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--no-threads", action="store_true")
    args = arg_parser.parse_args()
    with timer():
        main(get_parsed_input(), use_threads=(not args.no_threads))
