import collections
import copy
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
        lowest_cost: int | None = None
        locs_on_any_best_path = set()

        cache: dict[ReindeerState, tuple[int, set[Loc]]] = {}
        search_queue = collections.deque([(0, self.start_state, {self.start_state.loc})])
        while len(search_queue) > 0:
            cost, state, locs_visited = search_queue.popleft()

            # if the current cost is higher than our best full solution so far, following this path further is pointless
            if lowest_cost is not None and cost > lowest_cost:
                continue

            if state.loc == self.end_loc:  # found a way to the end!
                if lowest_cost is None or cost < lowest_cost:  # strictly better than anything we had before; forget previous stuff
                    lowest_cost = cost
                    locs_on_any_best_path = copy.copy(locs_visited)
                elif cost == lowest_cost:  # tied with before; merge data
                    locs_on_any_best_path |= locs_visited
                # else: this is no improvement; just keep our previous solution
                continue  # no need to keep searching past the end

            if not self.grid[state.loc]:  # wall
                continue

            # is this the cheapest way to get to this state? (that we've seen so far)
            cost_old, locs_visited_old = cache.get(state, (None, set()))
            if cost_old is None or cost < cost_old:  # strictly better than anything we had before; forget previous stuff
                pass
            elif cost == cost_old:  # tied with before; merge data
                locs_visited.update(locs_visited_old)
            else:  # this new way is worse than what we've seen before
                continue
            cache[state] = (cost, locs_visited)

            # add adjacent states to the queue to be processed
            for cost_new, state_new in get_move_options(cost, state):
                locs_visited_new = locs_visited | {state_new.loc}
                search_queue.append((cost_new, state_new, locs_visited_new))

        if lowest_cost is None:
            raise ValueError("never found path to end loc")
        return lowest_cost, locs_on_any_best_path


def main(input_parsed: InputData):
    grid, start_loc, end_loc = input_parsed
    solver = Solver(grid, start_loc, end_loc)
    min_score, locs_on_best_paths = solver.find_best_paths()
    print(f"{min_score = }")
    print(f"{len(locs_on_best_paths) = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
