from collections import Counter, defaultdict

from advent_utils import read_input, timer

InputData = list[int]


def get_parsed_input() -> InputData:
    input_raw = read_input(11)
    return list(map(int, input_raw.strip().split()))


def do_blinks(stone_counts: dict[int, int], *, n_blinks: int) -> int:
    if n_blinks < 0:
        raise ValueError("n_blinks must be >= 0")
    for _ in range(n_blinks):
        new_stone_counts: dict[int, int] = defaultdict(int)
        for number, count in stone_counts.items():
            if number == 0:
                new_stone_counts[1] += count
            elif (n_digits := len(number_str := str(number))) % 2 == 0:
                n_digits_each = n_digits // 2
                left = int(number_str[:n_digits_each])
                right = int(number_str[n_digits_each:])
                new_stone_counts[left] += count
                new_stone_counts[right] += count
            else:
                new_stone_counts[number * 2024] += count
        stone_counts = new_stone_counts
    return sum(stone_counts.values())


def main(input_parsed: InputData):
    stone_counts = Counter(input_parsed)
    n_stones_total1 = do_blinks(stone_counts, n_blinks=25)
    print(f"{n_stones_total1 = }")
    n_stones_total2 = do_blinks(stone_counts, n_blinks=75)
    print(f"{n_stones_total2 = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
