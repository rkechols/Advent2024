import numpy as np

from advent_utils import Direction, GridSolver, Loc, read_input, timer

InputData = np.ndarray

TARGET_1 = "XMAS"

TARGET_2 = np.array([
    ["M", None, "M"],
    [None, "A", None],
    ["S", None, "S"],
])
TARGET_2_RELEVANT_COORDINATES = TARGET_2.nonzero()
TARGET_2_RELEVANT_VALUES = TARGET_2[TARGET_2_RELEVANT_COORDINATES]


def get_parsed_input() -> InputData:
    input_raw = read_input(4)
    input_parsed = np.array([list(row) for row in input_raw.strip().splitlines()])
    return input_parsed


def is_block_target2(block: np.ndarray) -> bool:
    if block.shape != TARGET_2.shape:
        raise ValueError("block shape should match target shape")
    return np.all(block[TARGET_2_RELEVANT_COORDINATES] == TARGET_2_RELEVANT_VALUES).item()


class Solver(GridSolver):

    def is_word_target1(self, start_loc: Loc, direction: Direction) -> bool:
        for i, target_letter in enumerate(TARGET_1):
            loc = start_loc.shift(direction * i)
            if not self.is_loc_in_bounds(loc):
                return False  # out of bounds
            if self.grid[loc] != target_letter:
                return False
        return True

    def part1(self) -> int:
        count = 0
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                loc = Loc(i, j)
                for i_shift in (-1, 0 , 1):
                    for j_shift in (-1, 0, 1):
                        direction = Direction(i_shift, j_shift)
                        if direction == (0, 0):
                            continue
                        if self.is_word_target1(loc, direction):
                            count += 1
        return count

    def part2(self) -> int:
        count = 0
        for i in range(self.n_rows - (TARGET_2.shape[0] - 1)):
            for j in range(self.n_cols - (TARGET_2.shape[1] - 1)):
                block = self.grid[i:(i + TARGET_2.shape[0]), j:(j + TARGET_2.shape[1])]
                for rotation_count in range(4):
                    block_rotated = np.rot90(block, rotation_count)
                    if is_block_target2(block_rotated):
                        count += 1
        return count


def main(input_parsed: InputData):
    solver = Solver(input_parsed)
    # part 1
    count1 = solver.part1()
    print(f"{count1 = }")
    # part 2
    count2 = solver.part2()
    print(f"{count2 = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
