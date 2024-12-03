import re

from advent_utils import read_input


InputData = str


def get_parsed_input() -> InputData:
    input_raw = read_input(3)
    return input_raw


def main(input_parsed: InputData):
    # part 1
    total1 = 0
    for match in re.finditer(r"mul\((\d{1,3}),(\d{1,3})\)", input_parsed):
        a, b = map(int, match.groups())
        total1 += a * b
    print(f"{total1 = }")
    # part 2
    total2 = 0
    active = True
    for match in re.finditer(r"mul\((\d{1,3}),(\d{1,3})\)|do(?:n't)?\(\)", input_parsed):
        match_string = match.group(0)
        if match_string == "do()":
            active = True
        elif match_string == "don't()":
            active = False
        elif active:
            a, b = map(int, match.groups())
            total2 += a * b
    print(f"{total2 = }")


if __name__ == "__main__":
    main(get_parsed_input())
