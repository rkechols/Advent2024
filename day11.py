from tqdm import tqdm

from advent_utils import read_input, timer

InputData = list[int]


def get_parsed_input() -> InputData:
    input_raw = read_input(11)
    return list(map(int, input_raw.strip().split()))


def do_blinks(number: int, *, n_blinks: int) -> int:
    if n_blinks < 0:
        raise ValueError("n_blinks must be >= 0")
    if n_blinks == 0:
        return 1
    blinks_remaining = n_blinks - 1
    if number == 0:
        return do_blinks(1, n_blinks=blinks_remaining)
    number_str = str(number)
    if (n_digits := len(number_str)) % 2 == 0:
        n_digits_each = n_digits // 2
        left = do_blinks(int(number_str[:n_digits_each]), n_blinks=blinks_remaining)
        right = do_blinks(int(number_str[n_digits_each:]), n_blinks=blinks_remaining)
        return left + right
    # else
    return do_blinks(number * 2024, n_blinks=blinks_remaining)


def main(input_parsed: InputData):
    n_stones_total1 = sum(
        do_blinks(number, n_blinks=25)
        for number in input_parsed
    )
    print(f"{n_stones_total1 = }")
    n_stones_total2 = sum(
        do_blinks(number, n_blinks=75)
        for number in tqdm(input_parsed)
    )
    print(f"{n_stones_total2 = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
