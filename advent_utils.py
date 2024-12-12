import sys
import time
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import NamedTuple, Self

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


class Direction(Enum):
    UP = (-1, 0)
    RIGHT = (0, 1)
    DOWN = (1, 0)
    LEFT = (0, -1)

    def perpendiculars(self) -> tuple[Self, Self]:
        a, b = self.value
        return Direction((b, a)), Direction((-b, -a))


class Loc(NamedTuple):
    row: int
    col: int

    def shift(self, direction: Direction) -> Self:
        return Loc(self.row + direction.value[0], self.col + direction.value[1])
