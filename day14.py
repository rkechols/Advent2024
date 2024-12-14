import functools
import re
import shutil
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

from advent_utils import Direction, Loc, read_input, timer

BotsState = dict[Loc, set[Direction]]

RENDERINGS_DIR = Path("data/day14-renderings")
shutil.rmtree(RENDERINGS_DIR, ignore_errors=True)
RENDERINGS_DIR.mkdir(parents=True, exist_ok=True)


def get_parsed_input() -> BotsState:
    input_raw = read_input(14)
    input_parsed = []
    for line in input_raw.strip().splitlines():
        px, py, vx, vy = map(int, re.fullmatch(r"p=(-?\d+),(-?\d+) v=(-?\d+),(-?\d+)", line).groups())
        input_parsed.append((Loc(px, py), Direction(vx, vy)))
    input_structured: BotsState = defaultdict(set)
    for loc, direction in input_parsed:
        input_structured[loc].add(direction)
    return input_structured


class Solver:
    def __init__(self, n_rows: int, n_cols: int, bots: BotsState):
        if n_rows <= 0 or n_cols <= 0:
            raise ValueError("grid dimensions must be positive numbers")
        if n_rows % 2 == 0 or n_cols % 2 == 0:
            raise ValueError("grid dimensions must both be odd numbers")
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.all_bots = bots
        self._state_history: set[str] = set()
        self._found_loop = False
        self.seconds_elapsed = 0
        self.save_rendering()

    def save_rendering(self):
        canvas = np.array([
            [
                len(self.all_bots[Loc(i, j)]) > 0
                for j in range(self.n_cols)
            ]
            for i in range(self.n_rows)
        ])
        image = Image.fromarray(canvas.transpose())
        image.save(RENDERINGS_DIR / f"{self.seconds_elapsed:09d}-seconds.png")

    def get_state_str(self) -> str:
        lines = []
        for loc, bots in sorted(self.all_bots.items()):
            if len(bots) == 0:
                continue
            loc_str = ",".join(map(str, loc))
            loc_bots = " ".join(",".join(map(str, bot)) for bot in sorted(bots))
            lines.append(f"{loc_str}|{loc_bots}")
        return "\n".join(lines)

    def simulate(self, n_seconds_stop: int | None):
        if self._found_loop:
            print(f"loop already found after {self.seconds_elapsed} seconds")
            return
        if n_seconds_stop is not None:
            if n_seconds_stop == self.seconds_elapsed:
                return
            elif n_seconds_stop < self.seconds_elapsed:
                raise ValueError("simulation has already run past that point; use a new Solver instance")
        while n_seconds_stop is None or self.seconds_elapsed < n_seconds_stop:
            # progress forward 1 second
            all_bots_new: BotsState = defaultdict(set)
            for loc, bots in self.all_bots.items():
                for bot_direction in bots:
                    bot_new_loc = loc.shift(bot_direction)
                    bot_new_loc = Loc(bot_new_loc.row % self.n_rows, bot_new_loc.col % self.n_cols)
                    all_bots_new[bot_new_loc].add(bot_direction)
            self.all_bots = all_bots_new
            self.seconds_elapsed += 1
            # check if we're in a loop
            state_str = self.get_state_str()
            if state_str in self._state_history:  # seen this state before!
                self._found_loop = True
                print(f"after {self.seconds_elapsed} seconds, the bots have started repeating formations")
                return
            # new state: save it
            self._state_history.add(state_str)
            self.save_rendering()

    def get_score(self) -> int:
        quadrant_line_rows = self.n_rows // 2
        quadrant_line_cols = self.n_cols // 2
        quadrant_counts = defaultdict(int)
        for loc, bots in self.all_bots.items():
            if loc.row == quadrant_line_rows:
                continue
            row_bool = loc.row < quadrant_line_rows
            if loc.col == quadrant_line_cols:
                continue
            col_bool = loc.col < quadrant_line_cols
            quadrant_counts[(row_bool, col_bool)] += len(bots)
        return functools.reduce(lambda a, b: a * b, quadrant_counts.values(), 1)


def main(bots: BotsState):
    # part 1
    solver = Solver(101, 103, bots)
    solver.simulate(n_seconds_stop=100)
    score = solver.get_score()
    print(f"{score = }")
    # part 2
    solver.simulate(n_seconds_stop=None)


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
