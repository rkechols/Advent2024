import itertools
from typing import Any

import numpy as np

from advent_utils import Direction, GridCardinalDirection, GridSolver, Loc, read_input, timer

InputData = tuple[np.ndarray, list[GridCardinalDirection]]

WALL = "#"
BOX = "O"
EMPTY = "."
BOT = "@"

DIRECTIONS = {
    "^": GridCardinalDirection.UP,
    ">": GridCardinalDirection.RIGHT,
    "v": GridCardinalDirection.DOWN,
    "<": GridCardinalDirection.LEFT,
}


def get_parsed_input() -> InputData:
    input_raw = read_input(15)
    grid_str, directions_str = input_raw.strip().split("\n\n")
    grid = np.array([list(line) for line in grid_str.strip().splitlines()])
    directions = [
        direction
        for char in directions_str
        if (direction := DIRECTIONS.get(char))
    ]
    return grid, directions


class _Solver(GridSolver):
    def __init__(self, grid: np.ndarray):
        if {*grid[0, :], *grid[-1, :], *grid[:, 0], *grid[:, -1]} != {WALL}:
            raise ValueError("grid border must be completely walls!")
        super().__init__(grid)
        self.bot_loc = self._find_bot()

    def _find_bot(self) -> Loc:
        for i in range(1, self.n_rows - 1):
            for j in range(1, self.n_cols - 1):
                if self.grid[i, j] == BOT:
                    return Loc(i, j)
        raise ValueError("bot not found!")


class Solver1(_Solver):
    def __init__(self, grid: np.ndarray):
        super().__init__(grid.copy())  # since we modify in-place

    def move_bot(self, directions: list[GridCardinalDirection]):
        for direction_ in directions:
            direction = direction_.value
            bot_next = self.bot_loc.shift(direction)
            cursor = bot_next
            while (cursor_val := self.grid[cursor]) not in (EMPTY, WALL):
                cursor = cursor.shift(direction)
            if cursor_val == WALL:
                continue  # no action
            # cursor_val must be EMPTY
            self.grid[cursor] = BOX
            self.grid[bot_next] = BOT
            self.grid[self.bot_loc] = EMPTY
            self.bot_loc = bot_next

    def get_gps_sum(self) -> int:
        total = 0
        for i in range(1, self.n_rows - 1):
            for j in range(1, self.n_cols - 1):
                if self.grid[i, j] == BOX:
                    total += (100 * i) + j
        return total


BOX_LEFT = "["
BOX_RIGHT = "]"


EXPANSIONS = {
    WALL: (WALL, WALL),
    BOX: (BOX_LEFT, BOX_RIGHT),
    EMPTY: (EMPTY, EMPTY),
    BOT: (BOT, EMPTY),
}

DIRECTION_OF_OTHER_BOX_HALF = {
    BOX_LEFT: GridCardinalDirection.RIGHT.value,
    BOX_RIGHT: GridCardinalDirection.LEFT.value,
}


class CannotMove(Exception):
    """raised when an attempted move is not possible"""


def update_special(to_update: dict[Any, Any], new_values: dict[Any, Any]):
    # TODO: get around this weirdness by doing BFS with sets, not DFS
    for k, v in new_values.items():
        if v == EMPTY:
            to_update.setdefault(k, v)
        else:
            to_update[k] = v


class Solver2(_Solver):
    def __init__(self, grid: np.ndarray):
        super().__init__(np.array([
            list(itertools.chain(*(EXPANSIONS[sym] for sym in row)))
            for row in grid
        ]))

    def _move_helper(self, loc_target: Loc, direction: Direction) -> dict[Loc, str]:
        this_symbol = self.grid[loc_target]
        if this_symbol == WALL:
            raise CannotMove
        if this_symbol == EMPTY:
            return {}
        if this_symbol not in (BOX_LEFT, BOX_RIGHT):
            raise ValueError("we goofed")
        if direction in (GridCardinalDirection.LEFT.value, GridCardinalDirection.RIGHT.value):
            # pushing the box length-wise; no special treatment
            loc_target_next = loc_target.shift(direction)
            overwrites = self._move_helper(loc_target_next, direction)
            update_special(overwrites, {
                loc_target_next: this_symbol,
                loc_target: EMPTY,
            })
            return overwrites
        else:
            # pushing the box on its wide side
            loc_target_next = loc_target.shift(direction)
            loc_target2 = loc_target.shift(DIRECTION_OF_OTHER_BOX_HALF[this_symbol])
            loc_target2_next = loc_target2.shift(direction)
            overwrites = {}
            update_special(overwrites, self._move_helper(loc_target_next, direction))
            if self.grid[loc_target_next] != this_symbol:
                # only needed if the place we're pushing is NOT another box lined up with the current one
                update_special(overwrites, self._move_helper(loc_target2_next, direction))
            update_special(overwrites, {
                loc_target_next: this_symbol,
                loc_target2_next: self.grid[loc_target2],
                loc_target: EMPTY,
                loc_target2: EMPTY,
            })
            return overwrites

    def move_bot(self, directions: list[GridCardinalDirection]):
        for direction_ in directions:
            direction = direction_.value
            bot_next = self.bot_loc.shift(direction)
            # figure out what all would move
            try:
                overwrites = self._move_helper(bot_next, direction)
            except CannotMove:  # nope
                continue
            update_special(overwrites, {
                bot_next: BOT,
                self.bot_loc: EMPTY,
            })
            # actually move everything
            for loc, symbol in overwrites.items():
                self.grid[loc] = symbol
            self.bot_loc = bot_next

    def get_gps_sum(self) -> int:
        total = 0
        for i in range(1, self.n_rows - 1):
            for j in range(2, self.n_cols - 2):
                if self.grid[i, j] == BOX_LEFT:
                    total += (100 * i) + j
        return total


def main(input_parsed: InputData):
    grid, directions = input_parsed
    # part 1
    solver1 = Solver1(grid)
    solver1.move_bot(directions)
    gps_sum1 = solver1.get_gps_sum()
    print(f"{gps_sum1 = }")
    # part 2
    solver2 = Solver2(grid)
    solver2.move_bot(directions)
    gps_sum2 = solver2.get_gps_sum()
    print(f"{gps_sum2 = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
