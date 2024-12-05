import numpy as np

from advent_utils import read_input, timer

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
    input_parsed = np.array([list(row) for row in input_raw.strip().split("\n")])
    return input_parsed


def is_block_target2(block: np.ndarray) -> bool:
    if block.shape != TARGET_2.shape:
        raise ValueError("block shape should match target shape")
    return np.all(block[TARGET_2_RELEVANT_COORDINATES] == TARGET_2_RELEVANT_VALUES).item()


class Solver:
    def __init__(self, grid: np.ndarray):
        super().__init__()
        self.grid = grid
        if len(self.grid.shape) != 2:
            raise ValueError("grid must be 2-dimensional")

    @property
    def n_rows(self) -> int:
        return self.grid.shape[0]

    @property
    def n_cols(self) -> int:
        return self.grid.shape[1]


    def is_word_target1(self, start_loc: tuple[int, int], direction: tuple[int, int]) -> bool:
        start_loc_np = np.array(start_loc)
        direction_np = np.array(direction)
        for i, target_letter in enumerate(TARGET_1):
            loc = tuple(start_loc_np + (i * direction_np))
            if not (0 <= loc[0] < self.n_rows and 0 <= loc[1] < self.n_cols):
                return False  # out of bounds
            if self.grid[loc] != target_letter:
                return False
        return True

    def part1(self) -> int:
        count = 0
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                loc = (i, j)
                for i_shift in (-1, 0 , 1):
                    for j_shift in (-1, 0, 1):
                        direction = (i_shift, j_shift)
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
