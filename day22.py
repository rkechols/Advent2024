import itertools
from collections import defaultdict

from advent_utils import read_input, timer

InputData = list[int]

Trigger = tuple[int, ...]
TRIGGER_LEN = 4


def get_parsed_input() -> InputData:
    input_raw = read_input(22)
    return list(map(int, input_raw.strip().splitlines()))


def mix_and_prune(a: int, b: int) -> int:
    return (a ^ b) % 16777216


def step(secret: int) -> int:
    secret = mix_and_prune(secret, secret * 64)
    secret = mix_and_prune(secret, secret // 32)
    secret = mix_and_prune(secret, secret * 2048)
    return secret


def make_sequence(secret: int, *, n: int) -> list[int]:
    return [secret] + [
        secret := step(secret)
        for _ in range(n)
    ]


def find_best_sale(sequences: list[list[int]]) -> int:
    last_digits = [
        [secret % 10 for secret in seq]
        for seq in sequences
    ]
    diff_seqs = [
        [b - a for a, b in itertools.pairwise(lasts)]
        for lasts in last_digits
    ]
    possible_sales = []
    for values, diffs in zip(last_digits, diff_seqs):
        these_sales: dict[Trigger, int] = {}
        for i in range(len(diffs) - (TRIGGER_LEN - 1)):
            trigger = tuple(diffs[i:(i + TRIGGER_LEN)])
            value = values[i + TRIGGER_LEN]
            these_sales.setdefault(trigger, value)
        possible_sales.append(these_sales)
    totals_per_trigger: dict[Trigger, int] = defaultdict(int)
    for seq_sales in possible_sales:
        for trigger, value in seq_sales.items():
            totals_per_trigger[trigger] += value
    # print("# of unique triggers:", len(totals_per_trigger))
    return max(totals_per_trigger.values())


def main(input_parsed: InputData):
    sequences = [
        make_sequence(secret, n=2000)
        for secret in input_parsed
    ]
    total1 = sum(
        seq[-1]
        for seq in sequences
    )
    print(f"{total1 = }")
    best_sale_value = find_best_sale(sequences)
    print(f"{best_sale_value = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
