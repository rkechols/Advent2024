import dataclasses
import itertools
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


# part 2

# generalized:
#   00: (2, 4) -> b = a % 8 (take last 3 bits)
#   02: (1, x) -> b = b ^ x (modify 'b')
#   04: (7, 5) -> c = a << b (trim 'b' bits from 'a'; save as 'c')
#   { -- order here is flexible; we just need both (1, y) and (4, _) before (5, 5)
#     06: (1, y) -> b = b ^ y (modify 'b')
#     08: (4, _) -> b = b ^ c (where bits don't match)
#     10: (5, 5) -> print(b % 8)
#     12: (0, 3) -> a = a << 3 (trim 3 bits from a)
#   }
#   14: (3, 0) -> if a: goto 0
#   else: TERMINATE

# semantically:
# 1. look at the last few bits of `a` (up to 10, depending on the last 3 bits)
# 2. calculate a number in range [0, 7] to be printed
# 3. drop the last 3 bits of `a`
# 4. if `a` has any nonzero bits remaining, repeat; otherwise stop


def part2(program: list[int], check: bool = True) -> int:
    program_pairs = list(itertools.batched(program, 2, strict=True))
    assert len(program_pairs) == 8
    assert program_pairs[0] == (2, 4)
    assert program_pairs[1][0] == 1
    x = program_pairs[1][1]
    assert program_pairs[2] == (7, 5)
    assert program_pairs[7] == (3, 0)
    flexible_section = program_pairs[3:7]
    flexible_section.remove((0, 3))  # ValueError if not found
    assert flexible_section.pop(2) == (5, 5)
    assert (flexible_section[0][0], flexible_section[1][0]) in [(1, 4), (4, 1)]

    # work backwards from final `a` value, which is 0
    a_options = {0}
    for b_printed in reversed(program):
        a_options_new = set()
        for a_so_far in a_options:
            for a_tail in range(8):  # try all the options for the last 3 bits
                # what does it look like with these last 3 bits stuck back on the end?
                a_hypothetical = (a_so_far * 8) + a_tail
                if a_hypothetical == 0:  # `a` can never be 0 except at program termination
                    continue
                # calculate the number that goes to output
                b = a_hypothetical % 8
                b = b ^ x
                c = a_hypothetical // (2 ** b)
                for opcode, operand in flexible_section:
                    if opcode == 1:
                        b = b ^ operand
                    elif opcode == 4:
                        b = b ^ c
                    else:
                        raise ValueError(f"unexpected {opcode = } in flexible section")
                b = b % 8
                if b == b_printed:  # it matches the output we need
                    a_options_new.add(a_hypothetical)
        if len(a_options_new) == 0:
            raise ValueError("failed to find path")
        a_options = a_options_new

    if check:
        for modified_a in sorted(a_options):
            output = run((modified_a, 0, 0), program)
            if output != program:
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
    modified_a = part2(program)
    print(f"{modified_a = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
