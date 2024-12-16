import collections
import copy
import heapq
import itertools
from typing import NamedTuple

import numpy as np

from advent_utils import Direction, GridCardinalDirection, GridSolver, Loc, read_input, timer

InputData = tuple[np.ndarray, Loc, Loc]

WALL = "#"
EMPTY = "."
START = "S"
END = "E"

COST_MOVE = 1
COST_ROTATE = 1000


class ReindeerState(NamedTuple):
    loc: Loc
    direction: Direction


def get_parsed_input() -> InputData:
    input_raw = read_input(16)
    grid_symbols = np.array([list(line) for line in input_raw.strip().splitlines()])
    start_loc = None
    end_loc = None
    for i in range(grid_symbols.shape[0]):
        for j in range(grid_symbols.shape[1]):
            loc = Loc(i, j)
            symbol = grid_symbols[loc]
            if symbol == START:
                start_loc = loc
            elif symbol == END:
                end_loc = loc
    if start_loc is None or end_loc is None:
        raise ValueError("Failed to find start or end location")
    grid = np.array([[sym != WALL for sym in row] for row in grid_symbols])
    return grid, start_loc, end_loc


def get_move_options(current_cost: int, state: ReindeerState) -> list[tuple[int, ReindeerState]]:
    loc, direction = state
    return [
        (current_cost + COST_MOVE, ReindeerState(loc.shift(direction), direction)),
        (current_cost + COST_ROTATE, ReindeerState(loc, direction.rot_clockwise())),
        (current_cost + COST_ROTATE, ReindeerState(loc, direction.rot_counter_clockwise())),
    ]


class Solver(GridSolver):
    def __init__(self, grid: np.ndarray, start_loc: Loc, end_loc: Loc):
        if any(itertools.chain(grid[0, :], grid[-1, :], grid[:, 0], grid[:, -1])):
            raise ValueError("all grid edges should be walls")
        super().__init__(grid)
        if start_loc == end_loc:
            raise ValueError("`start_loc` and `end_loc` should not be equal")
        self.start_state = ReindeerState(start_loc, GridCardinalDirection.RIGHT.value)
        self.end_loc = end_loc

    def find_best_paths(self) -> tuple[int, set[Loc]]:
        best_score: int | None = None
        locs_on_any_best_path = set()

        cache: dict[ReindeerState, tuple[int, set[Loc]]] = {self.start_state: (0, {self.start_state.loc})}
        search_priority_queue = collections.deque([(0, self.start_state, {self.start_state.loc})])
        while len(search_priority_queue) > 0:
            cost, state, locs_visited = search_priority_queue.popleft()
            if best_score is not None and cost > best_score:
                continue
            if state.loc == self.end_loc:  # don't keep searching after arriving at the end
                continue
            for cost_new, state_new in get_move_options(cost, state):
                if not self.grid[state_new.loc]:  # wall
                    continue
                if best_score is not None and cost_new > best_score:
                    continue
                locs_visited_new = locs_visited | {state_new.loc}
                if state_new.loc == self.end_loc:
                    if best_score is None or cost_new < best_score:
                        best_score = cost_new
                        locs_on_any_best_path = locs_visited_new
                    elif cost_new == best_score:
                        locs_on_any_best_path |= locs_visited_new
                    continue
                cost_old, locs_visited_old = cache.get(state_new, (None, set()))
                if cost_old is None or cost_new < cost_old:  # never been here before, or this new way is strictly better
                    all_locs_on_path = copy.copy(locs_visited)
                elif cost_new == cost_old:  # tied
                    all_locs_on_path = locs_visited | locs_visited_old  # combine all paths to this score
                else:  # this new way is worse
                    continue
                all_locs_on_path.add(state_new.loc)
                # either this is our first time getting to this state, or the path getting here was cheaper than anything previous
                cache[state_new] = (cost_new, all_locs_on_path)
                search_priority_queue.append((cost_new, state_new, all_locs_on_path))  # put it in the queue to be further searched
        if best_score is None:
            raise ValueError("never found path to end loc")
        return best_score, locs_on_any_best_path


def main(input_parsed: InputData):
    grid, start_loc, end_loc = input_parsed
    solver = Solver(grid, start_loc, end_loc)
    min_score, locs_on_best_paths = solver.find_best_paths()
    print(f"{min_score = }")
    print(f"{len(locs_on_best_paths) = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
