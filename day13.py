import math
import re

import numpy as np

from advent_utils import read_input, timer

InputData = list[tuple[np.ndarray, np.ndarray]]

RE_BUTTON_DEF = re.compile(r"Button [AB]: X\+(\d+), Y\+(\d+)")

COST_VEC = np.array([3, 1])


def get_parsed_input() -> InputData:
    input_raw = read_input(13)
    machine_blocks = input_raw.strip().split("\n\n")
    to_return = []
    for machine_block in machine_blocks:
        button_a_line, button_b_line, prize_line = machine_block.strip().splitlines()
        ax, ay = map(int, RE_BUTTON_DEF.fullmatch(button_a_line).groups())
        bx, by = map(int, RE_BUTTON_DEF.fullmatch(button_b_line).groups())
        prize_x, prize_y = map(int, re.fullmatch(r"Prize: X=(\d+), Y=(\d+)", prize_line).groups())
        to_return.append((np.array([[ax, bx], [ay, by]]), np.array([prize_x, prize_y])))
    return to_return


def are_collinear(vec1: np.ndarray, vec2: np.ndarray) -> bool:
    return abs(np.dot(vec1, vec1) * np.dot(vec2, vec2)) == abs(np.dot(vec1, vec2) ** 2)


class NotIntegerSolvable(Exception):
    """raised if a matrix equation is not solvable with integers"""


def mat_solve_ints(mat: np.ndarray) -> tuple[int, int]:
    if mat.shape != (2, 3):
        raise ValueError("unexpected matrix equation shape")
    mat = mat.copy()  # so we're not editing in-place
    # eliminate bottom left
    left_upper, left_lower = mat[:, 0]
    lcm1 = math.lcm(left_upper, left_lower)
    mat[1, :] *= (lcm1 // left_lower)
    mat[1, :] -= (mat[0, :] * (lcm1 // left_upper))
    # eliminate bottom right
    right_upper, right_lower = mat[:, 1]
    lcm2 = math.lcm(right_upper, right_lower)
    mat[0, :] *= (lcm2 // right_upper)
    mat[0, :] -= (mat[1, :] * (lcm2 // right_lower))
    # double check eliminations
    if mat[1, 0] != 0 or mat[0, 1] != 0:
        raise RuntimeError("we goofed")
    # do division on the top row, if stuff is properly divisible
    left_upper, _, vec_upper = mat[0, :]
    a_count, mod = divmod(vec_upper, left_upper)
    if mod != 0:
        raise NotIntegerSolvable
    # do division on the bottom row, if stuff is properly divisible
    _, right_lower, vec_lower = mat[1, :]
    b_count, mod = divmod(vec_lower, right_lower)
    if mod != 0:
        raise NotIntegerSolvable
    # answer is indeed integers
    return a_count, b_count


def solve(input_parsed: InputData, *, button_press_limit: int | None = None, vec_shift: int = 0):
    total_cost = 0
    n_not_solvable = 0
    for i, (mat, vec) in enumerate(input_parsed, start=1):
        if mat.shape != (2, 2) or vec.shape != (2,):
            raise ValueError("unexpected numpy array shape")
        # check if the 'a' and 'b' vectors are collinear (infinite solutions, if we weren't restricted to integers)
        a_vec = mat[:, 0]
        b_vec = mat[:, 1]
        if are_collinear(a_vec, b_vec):
            print(f"WARNING: COLLINEAR ({i})")
        vec += vec_shift
        mat_equation = np.concat([mat, np.expand_dims(vec, axis=1)], axis=1)
        try:
            button_counts = mat_solve_ints(mat_equation)
        except NotIntegerSolvable:
            n_not_solvable += 1
            continue  # not solvable
        if button_press_limit is not None and any(count > button_press_limit for count in button_counts):
            print(f"WARNING: button press count over limit ({i})")
            continue
        this_cost = np.dot(button_counts, COST_VEC).item()
        total_cost += this_cost
    print(f"({n_not_solvable} of {len(input_parsed)} not solvable)")
    return total_cost


def main(input_parsed: InputData):
    # part 1
    total_cost1 = solve(input_parsed, button_press_limit=100)
    print(f"{total_cost1 = }")
    # part 2
    print("-" * 32)
    total_cost2 = solve(input_parsed, vec_shift=10000000000000)
    print(f"{total_cost2 = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
