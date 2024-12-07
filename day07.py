from advent_utils import read_input, timer

Operands = list[int]
InputData = list[tuple[int, Operands]]


def get_parsed_input() -> InputData:
    input_raw = read_input(7)
    input_parsed = []
    for line in input_raw.strip().splitlines():
        target_str, operands_str = line.split(":")
        operands = list(map(int, operands_str.strip().split()))
        if len(operands) < 2:
            print("WARNING! found a sequence of operands with no space for any operators")
        if not all(operand >= 1 for operand in operands):
            print("WARNING! found an operand that is less than 1")
        input_parsed.append((int(target_str), operands))
    return input_parsed


def concat(a: int, b: int) -> int:
    return int(str(a) + str(b))


class Solver:
    def __init__(self, target: int, *, use_concat: bool):
        super().__init__()
        self.target = target
        self.use_concat = use_concat

    def _get_bounds(self, operands: Operands) -> tuple[int, int]:
        smallest = largest = operands[0]
        for operand in operands[1:]:
            smallest_options = [smallest * operand, smallest + operand]
            largest_options = [largest * operand, largest + operand]
            if self.use_concat:
                smallest_options.append(concat(smallest, operand))
                largest_options.append(concat(largest, operand))
            smallest = min(smallest_options)
            largest = max(largest_options)
        return smallest, largest

    def _is_equality_possible_recursive(self, operands: Operands, *, total_so_far: int) -> bool:
        if total_so_far > self.target:
            return False
        if len(operands) == 0:
            return self.target == total_so_far
        this_operand = operands[0]
        remaining_operands = operands[1:]
        if self._is_equality_possible_recursive(remaining_operands, total_so_far=(total_so_far * this_operand)):
            return True
        if self._is_equality_possible_recursive(remaining_operands, total_so_far=(total_so_far + this_operand)):
            return True
        if self.use_concat and self._is_equality_possible_recursive(remaining_operands, total_so_far=concat(total_so_far, this_operand)):
            return True
        # nope
        return False

    def is_equality_possible(self, operands: Operands) -> bool:
        smallest, largest = self._get_bounds(operands)
        if smallest > self.target or largest < self.target:
            return False
        if self.target == smallest or self.target == largest:
            return True
        return self._is_equality_possible_recursive(operands[1:], total_so_far=operands[0])


def main(input_parsed: InputData):
    # part 1
    solvable_sum1 = sum(
        target
        for target, operands in input_parsed
        if Solver(target, use_concat=False).is_equality_possible(operands)
    )
    print(f"{solvable_sum1 = }")
    # part 2
    solvable_sum2 = sum(
        target
        for target, operands in input_parsed
        if Solver(target, use_concat=True).is_equality_possible(operands)
    )
    print(f"{solvable_sum2 = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
