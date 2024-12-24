import functools
import re
from collections import defaultdict
from enum import StrEnum
from typing import Literal, NamedTuple

from advent_utils import read_input, timer


class BitOperator(StrEnum):
    AND = "AND"
    OR = "OR"
    XOR = "XOR"

    def apply(self, a: bool, b: bool) -> bool:
        if self == BitOperator.AND:
            return a and b
        elif self == BitOperator.OR:
            return a or b
        elif self == BitOperator.XOR:
            return a != b
        else:
            raise ValueError(f"unknown bit operator: {self}")


class Rule(NamedTuple):
    a: str
    operator: BitOperator
    b: str
    out: str

    def has_predicate(self, a: str, operator: BitOperator, b: str) -> bool:
        return self.operator == operator and (self.a, self.b) in [(a, b), (b, a)]


InputData = tuple[dict[str, bool], list[Rule]]


def get_parsed_input() -> InputData:
    input_raw = read_input(24)
    initial_values_str, rules_str = input_raw.strip().split("\n\n")
    initial_values = {}
    for line in initial_values_str.strip().splitlines():
        sym, bool_str = re.fullmatch(r"([^:]+): ([01])", line).groups()
        initial_values[sym] = bool_str == "1"
    rules = []
    for line in rules_str.strip().splitlines():
        a, op, b, out = re.fullmatch(r"(\S+) (AND|OR|XOR) (\S+) -> (\S+)", line).groups()
        rules.append(Rule(a, BitOperator(op), b, out))
    n_bits_in = len(initial_values) // 2
    if sorted(initial_values.keys()) != ([f"x{i:02}" for i in range(n_bits_in)] + [f"y{i:02}" for i in range(n_bits_in)]):
        raise ValueError("Input should define initial values for equal numbers of x and y values")
    if sorted(rule.out for rule in rules if rule.out.startswith("z")) != [f"z{i:02}" for i in range(n_bits_in + 1)]:
        raise ValueError(f"Rule outputs should define {n_bits_in + 1} z values")
    return initial_values, rules


def run_system(input_parsed: InputData) -> int:
    initial_values, rules = input_parsed
    n_bits_in = len(initial_values) // 2
    # what Z-values do we need to fill?
    all_z_vars = {rule.out for rule in rules if rule.out.startswith("z")}
    # create a lookup for what rules depend on a given variable
    rules_lookup: dict[str, set[int]] = defaultdict(set)
    for i, rule in enumerate(rules):
        rules_lookup[rule.a].add(i)
        rules_lookup[rule.b].add(i)
    rules_lookup = dict(rules_lookup)  # no longer a defaultdict
    # let the information flow
    var_values = dict(initial_values)  # copy
    vars_to_follow = set(initial_values.keys())
    while not all_z_vars.issubset(set(var_values.keys())):  # while any z-var not determined
        rules_to_check = {
            rule_index
            for var_name in vars_to_follow
            for rule_index in rules_lookup.get(var_name, set())
        }
        vars_to_follow = set()
        for rule_index in rules_to_check:
            rule = rules[rule_index]
            if rule.out in var_values.keys():
                continue  # rule already did its computation
            try:
                a_val = var_values[rule.a]
                b_val = var_values[rule.b]
            except KeyError:
                continue  #  rule doesn't have both inputs yet
            out_val = rule.operator.apply(a_val, b_val)
            var_values[rule.out] = out_val
            vars_to_follow.add(rule.out)
    # calculate the actual answer
    z_int = get_val_from_bits("z", var_values, n_bits=(n_bits_in + 1))
    return z_int


def get_val_from_bits(name: Literal["x", "y", "z"], var_values: dict[str, bool], *, n_bits: int) -> int:
    bits = [
        var_values[f"{name}{i:02}"]
        for i in range(n_bits)
    ]
    binary_string = "".join("1" if bit else "0" for bit in reversed(bits))
    value_int = int(binary_string, 2)
    return value_int


def find_problem_wires(input_parsed: InputData, z_out: int) -> set[str]:
    initial_values, rules = input_parsed
    # compare given answer with real answer
    n_bits_in = len(initial_values) // 2
    x = get_val_from_bits("x", initial_values, n_bits=n_bits_in)
    y = get_val_from_bits("y", initial_values, n_bits=n_bits_in)
    expected = x + y
    wrong_bits_int = expected ^ z_out
    wrong_bits = [
        bit_str == "1"
        for bit_str in reversed(f"{wrong_bits_int:b}")
    ]
    try:
        first_wrong_bit = wrong_bits.index(True)
    except ValueError:
        return {  # write manual edits here
            "vdc", "z12",
            "z21", "nhn",
            "tvb", "khg",
            "gst", "z33",
        }
    print(f"{first_wrong_bit = }")
    # compare against standard addition algorithm
    rules_lookup: dict[str, set[int]] = defaultdict(set)
    for i, rule in enumerate(rules):
        rules_lookup[rule.a].add(i)
        rules_lookup[rule.b].add(i)
    rules_lookup = dict(rules_lookup)  # no longer a defaultdict
    carry_bit_slot_prev: str | None = None
    for i in range(n_bits_in):
        x_var = f"x{i:02}"
        y_var = f"y{i:02}"
        rule_pair = tuple(map(rules.__getitem__, rules_lookup[f"x{i:02}"]))
        if len(rule_pair) != 2:
            raise RuntimeError(f"IDK ({i = })")
        for rule1, rule2 in (rule_pair, rule_pair[::-1]):
            if rule1.has_predicate(x_var, BitOperator.XOR, y_var) and rule2.has_predicate(x_var, BitOperator.AND, y_var):
                this_bit_slot = rule1.out
                carry_bit_slot_here = rule2.out
                break
        else:
            raise RuntimeError(f"confused 1 ({i = })")
        if i == 0:
            if this_bit_slot != "z00":
                raise RuntimeError("problem with z00!")
            carry_bit_slot_prev = carry_bit_slot_here
            continue
        # else: not the first bit
        rule_pair_internal = tuple(map(rules.__getitem__, rules_lookup[this_bit_slot]))
        for rule1_internal, rule2_internal in (rule_pair_internal, rule_pair_internal[::-1]):
            if rule1_internal.has_predicate(this_bit_slot, BitOperator.XOR, carry_bit_slot_prev) and rule2_internal.has_predicate(this_bit_slot, BitOperator.AND, carry_bit_slot_prev):
                if rule1_internal.out != f"z{i:02}":
                    print(f"ERROR: bit {i = } had unexpected rule: {rule1_internal}")
                carry_rule, = tuple(map(rules.__getitem__, rules_lookup[carry_bit_slot_here]))
                if not carry_rule.has_predicate(carry_bit_slot_here, BitOperator.OR, rule2_internal.out):
                    raise RuntimeError(f"issue with carry rule at {i = }: {carry_rule}")
                carry_bit_slot_prev = carry_rule.out
                break
        else:
            raise RuntimeError(f"confused 2 ({i = })")
    raise RuntimeError("IDK (end of loop)")

def main(input_parsed: InputData):
    # part 1
    z_int = run_system(input_parsed)
    print(f"{z_int = }")
    # part 2
    problem_wires = find_problem_wires(input_parsed, z_int)
    problem_wires_str = ",".join(sorted(problem_wires))
    print(f"{problem_wires_str = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
