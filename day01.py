from collections import Counter
from typing import cast

from advent_utils import read_input, timer

InputData = list[tuple[int, int]]


def get_parsed_input() -> InputData:
    input_raw = read_input(1)
    data = [
        cast(tuple[int, int], tuple(map(int, line.split())))
        for line in input_raw.strip().splitlines()
    ]
    return data


def main(input_parsed: InputData):
    # part 1
    list1, list2 = map(sorted, zip(*input_parsed))
    total_diff = sum(abs(a - b) for a, b in zip(list1, list2))
    print(f"{total_diff = }")
    # part 2
    counter = Counter(list2)
    total_similarity = sum(
        a * counter.get(a, 0)
        for a in list1
    )
    print(f"{total_similarity = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
