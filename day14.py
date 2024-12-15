import functools
import re
import shutil
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

from advent_utils import read_input, timer

InputData = np.ndarray

RENDERINGS_DIR = Path("data/day14-renderings")
shutil.rmtree(RENDERINGS_DIR, ignore_errors=True)
RENDERINGS_DIR.mkdir(parents=True, exist_ok=True)


def get_parsed_input() -> InputData:
    input_raw = read_input(14)
    input_parsed = np.array([
        list(map(int, re.fullmatch(r"p=(-?\d+),(-?\d+) v=(-?\d+),(-?\d+)", line).groups()))
        for line in input_raw.strip().splitlines()
    ])
    return input_parsed


class Solver:
    def __init__(self, n_rows: int, n_cols: int, bots_data: InputData):
        if n_rows <= 0 or n_cols <= 0:
            raise ValueError("grid dimensions must be positive numbers")
        if n_rows % 2 == 0 or n_cols % 2 == 0:
            raise ValueError("grid dimensions must both be odd numbers")
        self.n_rows = n_rows
        self.n_cols = n_cols
        if len(bots_data.shape) != 2 or bots_data.shape[1] != 4:
            raise ValueError("bots array must be of shape (n, 4)")
        self.bot_locs = bots_data[:, :2]
        self.bot_directions = bots_data[:, 2:]
        self._state_history: set[str] = set()
        self._found_loop = False
        self.seconds_elapsed = 0
        self.save_rendering()

    def save_rendering(self):
        canvas = np.zeros((self.n_rows, self.n_cols), dtype=bool)
        for bot_loc in self.bot_locs:
            canvas[*bot_loc] = True
        image = Image.fromarray(canvas.transpose())
        image.save(RENDERINGS_DIR / f"{self.seconds_elapsed:09d}-seconds.png")

    def get_state_str(self) -> str:
        return "\n".join(" ".join(map(str, bot_loc)) for bot_loc in self.bot_locs)

    def simulate(self, n_seconds_stop: int | None):
        if self._found_loop:
            print(f"loop already found after {self.seconds_elapsed} seconds")
            return
        if n_seconds_stop is not None:
            if n_seconds_stop == self.seconds_elapsed:
                return
            elif n_seconds_stop < self.seconds_elapsed:
                raise ValueError("simulation has already run past that point; use a new Solver instance")
        position_mod = np.array([self.n_rows, self.n_cols])
        while n_seconds_stop is None or self.seconds_elapsed < n_seconds_stop:
            # progress forward 1 second
            self.bot_locs += self.bot_directions
            self.bot_locs %= position_mod
            self.seconds_elapsed += 1
            # check if we're in a loop
            state_str = self.get_state_str()
            if state_str in self._state_history:  # seen this state before!
                self._found_loop = True
                print(f"after {self.seconds_elapsed} iterations, the bots have started repeating formations")
                return
            # new state: save it
            self._state_history.add(state_str)
            self.save_rendering()

    def get_score(self) -> int:
        quadrant_line_rows = self.n_rows // 2
        quadrant_line_cols = self.n_cols // 2
        quadrant_counts = defaultdict(int)
        for row, col in self.bot_locs:
            if row == quadrant_line_rows:
                continue
            row_bool = row < quadrant_line_rows
            if col == quadrant_line_cols:
                continue
            col_bool = col < quadrant_line_cols
            quadrant_counts[(row_bool, col_bool)] += 1
        return functools.reduce(lambda a, b: a * b, quadrant_counts.values(), 1)


def main(input_parsed: InputData):
    # part 1
    solver = Solver(101, 103, input_parsed)
    solver.simulate(n_seconds_stop=100)
    score = solver.get_score()
    print(f"{score = }")
    # part 2
    solver.simulate(n_seconds_stop=None)


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
