import sys
import time
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import NamedTuple, Self, TypeVar

import numpy as np

DATA_DIR = Path(__file__).parent / "data"


def read_input(day: int) -> str:
    with open(DATA_DIR / f"day{day:02}.txt", encoding="utf-8") as f:
        return f.read()


@contextmanager
def timer():
    time_start = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - time_start
        print(f"[{duration:.3f} seconds]", file=sys.stderr)


_Tup = TypeVar("_Tup", bound=tuple)


def scale_tuple(tup: _Tup, scale: int) -> _Tup:
    return tup.__class__(x * scale for x in tup)


class Direction(NamedTuple):
    row_shift: int
    col_shift: int

    def __mul__(self, scale: int) -> Self:
        return Direction(self.row_shift * scale, self.col_shift * scale)

    def rot_clockwise(self) -> Self:
        return Direction(self.col_shift, -self.row_shift)

    def rot_counter_clockwise(self) -> Self:
        return Direction(-self.col_shift, self.row_shift)

    def perpendiculars(self) -> Self:
        return Direction(self.col_shift, self.row_shift), Direction(-self.col_shift, -self.row_shift)


class GridCardinalDirection(Enum):
    UP = Direction(-1, 0)
    RIGHT = Direction(0, 1)
    DOWN = Direction(1, 0)
    LEFT = Direction(0, -1)

    @classmethod
    def values(cls) -> list[Direction]:
        return [e.value for e in cls]


class Loc(NamedTuple):
    row: int
    col: int

    def shift(self, direction: Direction) -> Self:
        return Loc(self.row + direction.row_shift, self.col + direction.col_shift)


class GridSolver:
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
        return 0 <= loc.row < self.n_rows and 0 <= loc.col < self.n_cols
