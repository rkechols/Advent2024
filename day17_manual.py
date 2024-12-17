from advent_utils import timer

PROGRAM = [2, 4, 1, 7, 7, 5, 1, 7, 4, 6, 0, 3, 5, 5, 3, 0]

# for i, (a, b) in enumerate(itertools.pairwise(program)):
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


def part_2() -> int:
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
        print(f"{a_options = }")
    return min(a_options)


def main():
    a_smallest = part_2()
    print(f"{a_smallest = }")


if __name__ == "__main__":
    with timer():
        main()

