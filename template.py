from advent_utils import read_input


InputData = str


def get_parsed_input() -> InputData:
    input_raw = read_input(1)
    return input_raw


def main(input_parsed: InputData):
    print("Hello from advent2024!")


if __name__ == "__main__":
    main(get_parsed_input())
