import itertools

from advent_utils import read_input, timer

SAFE_DIFFS_UP = {1, 2, 3}
SAFE_DIFFS_DOWN = {-1, -2, -3}


InputData = list[list[int]]


def get_parsed_input() -> InputData:
    input_raw = read_input(2)
    data = [
        list(map(int, line.strip().split()))
        for line in input_raw.strip().split("\n")
    ]
    return data


def sequence_is_safe(sequence: list[int]) -> bool:
    diffs = {
        a - b
        for a, b in itertools.pairwise(sequence)
    }
    return diffs.issubset(SAFE_DIFFS_UP) or diffs.issubset(SAFE_DIFFS_DOWN)


def main(input_parsed: InputData):
    # part 1
    safe_count1 = 0
    for row in input_parsed:
        if sequence_is_safe(row):
            safe_count1 += 1
    print(f"{safe_count1 = }")
    # part 2
    safe_count2 = 0
    for row in input_parsed:
        if sequence_is_safe(row):
            safe_count2 += 1
            continue
        for i_to_skip in range(len(row)):
            if sequence_is_safe(row[:i_to_skip] + row[(i_to_skip + 1):]):
                safe_count2 += 1
                break
    print(f"{safe_count2 = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
