import itertools

import numpy as np
from tqdm import tqdm

from advent_utils import GridCardinalDirection, GridSolver, Loc, read_input, timer

InputData = tuple[np.ndarray, Loc, Loc]

WALL = "#"
EMPTY = "."
START = "S"
END = "E"


def get_parsed_input() -> InputData:
    input_raw = read_input(20)
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


class Solver(GridSolver):
    def __init__(self, grid: np.ndarray, start_loc: Loc, end_loc: Loc):
        if any(itertools.chain(grid[0, :], grid[-1, :], grid[:, 0], grid[:, -1])):
            raise ValueError("all grid edges should be walls")
        super().__init__(grid)
        if start_loc == end_loc:
            raise ValueError("`start_loc` and `end_loc` should not be equal")
        self.start_loc = start_loc
        self.end_loc = end_loc

    def get_full_path(self) -> list[Loc]:
        path = [self.start_loc]
        loc = self.start_loc
        while loc != self.end_loc:
            possible_moves = set()
            for direction in GridCardinalDirection.values():
                next_loc = loc.shift(direction)
                if self.grid[next_loc] and next_loc not in path[-2:]:
                    possible_moves.add(next_loc)
            if len(possible_moves) != 1:
                raise RuntimeError(f"number of possible moves from {loc} is not exactly 1")
            loc = next(iter(possible_moves))
            path.append(loc)
        return path

    def count_cheats(self, full_path: list[Loc], *, cheat_length: int, threshold: int = 100) -> int:
        full_path_lookup = {loc: i for i, loc in enumerate(full_path)}
        n_cheats_over_threshold = 0
        for i, loc in enumerate(tqdm(full_path[:-4])):  # no point searching for cheats from the last 4 spots
            # gather neighborhood of all nearby points
            neighborhood = {loc}
            to_search = {loc}
            for _ in range(cheat_length):
                to_search_next = set()
                for loc_to_search in to_search:
                    for direction in GridCardinalDirection.values():
                        loc_next = loc_to_search.shift(direction)
                        if loc_next not in neighborhood and self.is_loc_in_bounds(loc_next):
                            to_search_next.add(loc_next)
                neighborhood.update(to_search_next)
                to_search = to_search_next
            neighborhood.discard(loc)
            # check if any are on the path and constitute a worthy shortcut
            for loc_nearby in neighborhood:
                try:
                    i_nearby = full_path_lookup[loc_nearby]
                except KeyError:  # not on path
                    continue
                normal_distance = i_nearby - i
                shortcut_length = loc.manhattan_distance(loc_nearby)
                time_gained = normal_distance - shortcut_length
                if time_gained >= threshold:
                    n_cheats_over_threshold += 1
        return n_cheats_over_threshold


def main(input_parsed: InputData):
    grid, start_loc, end_loc = input_parsed
    solver = Solver(grid, start_loc, end_loc)
    full_path = solver.get_full_path()
    print(f"length of full path: {len(full_path)}")
    n_cheats1 = solver.count_cheats(full_path, cheat_length=2)
    print(f"{n_cheats1 = }")
    n_cheats2 = solver.count_cheats(full_path, cheat_length=20)
    print(f"{n_cheats2 = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
