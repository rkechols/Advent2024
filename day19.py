from functools import cache

from advent_utils import read_input, timer

InputData = tuple[set[str], list[str]]


def get_parsed_input() -> InputData:
    input_raw = read_input(19)
    towel_patterns_str, targets_str = input_raw.strip().split("\n\n")
    towel_patterns = {towel_pattern.strip() for towel_pattern in towel_patterns_str.split(",")}
    targets = [line.strip() for line in targets_str.splitlines()]
    return towel_patterns, targets


class Solver:
    def __init__(self, towel_patterns: set[str]):
        super().__init__()
        self.towel_patterns = towel_patterns
        self.towel_pattern_lengths = {len(towel) for towel in towel_patterns}

    @cache
    def is_target_possible(self, target: str) -> bool:
        target_len = len(target)
        if target_len == 0:
            return True
        for substring_len in self.towel_pattern_lengths:
            if substring_len > target_len:
                continue
            substring, target_remainder = target[:substring_len], target[substring_len:]
            if substring in self.towel_patterns and self.is_target_possible(target_remainder):
                return True
        return False

    @cache
    def count_combinations(self, target: str) -> int:
        target_len = len(target)
        if target_len == 0:
            return 1
        n_combinations = 0
        for substring_len in self.towel_pattern_lengths:
            if substring_len > target_len:
                continue
            substring, target_remainder = target[:substring_len], target[substring_len:]
            if substring in self.towel_patterns:
                n_combinations += self.count_combinations(target_remainder)
        return n_combinations


def main(input_parsed: InputData):
    towel_patterns, targets = input_parsed
    solver = Solver(towel_patterns)
    # part 1
    n_possible = sum(
        solver.is_target_possible(target)
        for target in targets
    )
    print(f"{n_possible = }")
    # part 2
    n_combinations = sum(
        solver.count_combinations(target)
        for target in targets
    )
    print(f"{n_combinations = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
