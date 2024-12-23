import itertools
from collections import defaultdict
from typing import cast

from advent_utils import read_input, timer

InputData = list[tuple[str, str]]


def get_parsed_input() -> InputData:
    input_raw = read_input(23)
    input_parsed = [
        cast(tuple[str, str], tuple(line.strip().split("-")))
        for line in input_raw.strip().splitlines()
    ]
    return input_parsed


def main(input_parsed: InputData):
    # restructure input
    graph: dict[str, set[str]] = defaultdict(set)
    for a, b in input_parsed:
        if a == b:
            print(f"WARNING: self-loop! {a} -> {b}")
        graph[a].add(b)
        graph[b].add(a)
    graph = dict(graph)  # not a defaultdict anymore
    # part 1
    components: set[tuple[str, ...]] = set()
    for node_a, neighbors in graph.items():
        for node_b, node_c in itertools.combinations(neighbors, 2):
            if node_b in graph[node_c]:
                components.add(tuple(sorted([node_a, node_b, node_c])))
    n_with_t = sum(
        any(elem.startswith("t") for elem in component)
        for component in components
    )
    print(f"{n_with_t = }")
    # part 2
    biggest_component = set(next(iter(components)))
    for component_ in components:
        component = set(component_)
        if component.issubset(biggest_component):
            continue
        elem1 = next(iter(component))
        for neighbor in graph[elem1]:
            if neighbor in component:
                continue
            if component.issubset(graph[neighbor]):
                component.add(neighbor)
        if len(component) > len(biggest_component):
            biggest_component = component
    password = ",".join(sorted(biggest_component))
    print(f"{password = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
