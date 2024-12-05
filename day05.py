import functools
from collections import defaultdict
from typing import Literal, cast

from advent_utils import read_input

Rule = tuple[str, str]
Seq = list[str]
InputData = tuple[list[Rule], list[Seq]]


def get_parsed_input() -> InputData:
    input_raw = read_input(5)
    rules_str, sequences_str = input_raw.split("\n\n")
    rules = cast(list[Rule], [
        tuple(rule_str.split("|"))
        for rule_str in rules_str.strip().split("\n")
    ])
    sequences = [
        sequence_str.split(",")
        for sequence_str in sequences_str.strip().split("\n")
    ]
    return rules, sequences


class RulesIndex:
    def __init__(self, rules: list[Rule]):
        super().__init__()
        self._rule_lookup: dict[str, set[Rule]] = defaultdict(set)
        for rule in rules:
            self._rule_lookup[rule[0]].add(rule)
            self._rule_lookup[rule[1]].add(rule)

    def comparator(self, a: str, b: str) -> Literal[-1, 0, 1]:
        relevant_rules = self._rule_lookup[a] & self._rule_lookup[b]
        n_rules = len(relevant_rules)
        if n_rules < 1:
            return 0  # no rules -> equal standing
        elif n_rules == 1:
            rule = next(iter(relevant_rules))
            if rule == (a, b):
                return -1
            elif rule == (b, a):
                return 1
            else:
                raise ValueError(f"confused! {a = } ; {b = } ; {rule = }")
        else:  # more than 1 rule
            raise ValueError(f"confused! {a = } ; {b = } ; {relevant_rules = }")


def main(input_parsed: InputData):
    rules, sequences = input_parsed
    print(f"{len(rules) = }")
    print(f"{len(sequences) = }")
    seq_lengths = {len(seq) for seq in sequences}
    print('"All sequences are odd-length":', all(seq_len % 2 == 1 for seq_len in seq_lengths))
    print()

    rules_index = RulesIndex(rules)
    sorting_key = functools.cmp_to_key(rules_index.comparator)

    total_already_sorted = 0
    total_needed_sorting = 0
    for sequence in sequences:
        sequence_sorted = sorted(sequence, key=sorting_key)
        middle_number = int(sequence_sorted[len(sequence_sorted) // 2])
        if sequence == sequence_sorted:
            total_already_sorted += middle_number
        else:
            total_needed_sorting += middle_number
    print(f"{total_already_sorted = }")
    print(f"{total_needed_sorting = }")


if __name__ == "__main__":
    main(get_parsed_input())
