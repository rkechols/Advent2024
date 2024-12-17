import dataclasses
import re
from typing import Self

from advent_utils import read_input, timer

InputData = tuple[tuple[int, int, int], list[int]]


def get_parsed_input() -> InputData:
    input_raw = read_input(17)
    registers_str, program_str = input_raw.strip().split("\n\n")
    a, b, c = map(int, re.findall(r"Register [ABC]: (\d+)", registers_str))
    program = list(map(int, program_str.removeprefix("Program: ").split(",")))
    return (a, b, c), program


@dataclasses.dataclass
class Registers:
    a: int
    b: int
    c: int

    @classmethod
    def from_tuple(cls, tup: tuple[int, int, int]) -> Self:
        a, b, c = tup
        return cls(a=a, b=b, c=c)

    def get_combo_operand(self, operand: int) -> int:
        if 0 <= operand <= 3:
            return operand
        elif operand == 4:
            return self.a
        elif operand == 5:
            return self.b
        elif operand == 6:
            return self.c
        else:
            raise ValueError(f"invalid operand: {operand}")


# part 1


def run(registers_tup: tuple[int, int, int], program: list[int]) -> list[int]:
    registers = Registers.from_tuple(registers_tup)
    ptr = 0
    output = []
    while True:
        # check halting status / get next input
        try:
            opcode = program[ptr]
            operand = program[ptr + 1]
        except IndexError:
            break
        # do the thing
        ptr_next = ptr + 2
        if opcode == 0:  # adv
            registers.a = int(registers.a / (2 ** registers.get_combo_operand(operand)))
        elif opcode == 1:  # bxl
            registers.b = registers.b ^ operand
        elif opcode == 2:  # bst
            registers.b = registers.get_combo_operand(operand) % 8
        elif opcode == 3:  # jnz
            if registers.a != 0:
                ptr_next = operand
        elif opcode == 4:  # bxc
            registers.b = registers.b ^ registers.c
        elif opcode == 5:  # out
            output.append(registers.get_combo_operand(operand) % 8)
        elif opcode == 6:  # bdv
            registers.b = int(registers.a / (2 ** registers.get_combo_operand(operand)))
        elif opcode == 7:  # cdv
            registers.c = int(registers.a / (2 ** registers.get_combo_operand(operand)))
        else:
            raise ValueError(f"invalid opcode: {opcode}")
        # advance to next instruction
        ptr = ptr_next
    return output


# part 2 (NOTE: part 2 code is specifically written for my input)


PROGRAM = [2, 4, 1, 7, 7, 5, 1, 7, 4, 6, 0, 3, 5, 5, 3, 0]

# import itertools
# for i, (a, b) in enumerate(itertools.pairwise(PROGRAM)):
#     print(f"{i:>02}: {a, b}")

# instructions read from all cursor positions:
#   00: (2, 4) -> b = a % 8 (take last 3 bits)
#   01: (4, 1) -> b = b ^ c (where bits don't match)
#   02: (1, 7) -> b = b ^ 7 (invert last 3 bits)
#   03: (7, 7) -> INVALID
#   04: (7, 5) -> c = a << b (trim 'b' bits from 'a'; save as 'c')
#   05: (5, 1) -> print(1)
#   06: (1, 7) -> b = b ^ 7 (invert last 3 bits)
#   07: (7, 4) -> c = a << a (trim 'a' bits from 'a')
#   08: (4, 6) -> b = b ^ c (where bits don't match)
#   09: (6, 0) -> b = a (trim no bits; just copy)
#   10: (0, 3) -> a = a << 3 (trim 3 bits from a)
#   11: (3, 5) -> if a: goto 5
#   12: (5, 5) -> print(b % 8)
#   13: (5, 3) -> print(3)
#   14: (3, 0) -> if a: goto 0
#   else: TERMINATE

# instructions we can actually get to:
#   00: (2, 4) -> b = a % 8 (take last 3 bits)
#   02: (1, 7) -> b = b ^ 7 (invert 'b')
#   04: (7, 5) -> c = a << b (trim 'b' bits from 'a'; save as 'c')
#   06: (1, 7) -> b = b ^ 7 (invert 'b')
#   08: (4, 6) -> b = b ^ c (where bits don't match)
#   10: (0, 3) -> a = a << 3 (trim 3 bits from a)
#   12: (5, 5) -> print(b % 8)
#   14: (3, 0) -> if a: goto 0
#   else: TERMINATE

# semantically:
# 1. look at the last few bits of `a` (up to 10, depending on the last 3 bits)
# 2. calculate a number in range [0, 7] to be printed
# 3. drop the last 3 bits of `a`
# 4. if `a` has any nonzero bits remaining, repeat; otherwise stop


def part2(check: bool = True) -> int:
    # work backwards from final `a` value, which is 0
    a_options = {0}
    for b_printed in reversed(PROGRAM):
        a_options_new = set()
        for a_so_far in a_options:
            for a_tail in range(8):  # try all the options for the last 3 bits
                # what does it look like with these last 3 bits stuck back on the end?
                a_hypothetical = (a_so_far * 8) + a_tail
                if a_hypothetical == 0:  # `a` can never be 0 except at program termination
                    continue
                # calculate the number that goes to output
                b = a_hypothetical % 8
                c = a_hypothetical // (2 ** (b ^ 7))
                b = (b ^ c) % 8
                if b == b_printed:  # it matches the output we need
                    a_options_new.add(a_hypothetical)
        if len(a_options_new) == 0:
            raise ValueError("failed to find path")
        a_options = a_options_new

    if check:
        for modified_a in sorted(a_options):
            output = run((modified_a, 0, 0), PROGRAM)
            if output != PROGRAM:
                print(f"ERROR: mistaken answer found: {modified_a = }")
                a_options.discard(modified_a)

    return min(a_options)


# run both parts together


def main(input_parsed: InputData):
    registers_tup, program = input_parsed
    # part 1
    output = run(registers_tup, program)
    print("output:", ",".join(str(o) for o in output))
    # part 2
    modified_a = part2()
    print(f"{modified_a = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
