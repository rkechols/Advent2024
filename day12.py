import dataclasses
from typing import NamedTuple

import numpy as np

from advent_utils import Direction, GridCardinalDirection, GridSolver, Loc, read_input, timer

InputData = np.ndarray


def get_parsed_input() -> InputData:
    input_raw = read_input(12)
    grid = np.array([
        list(line.strip())
        for line in input_raw.strip().splitlines()
    ])
    return grid


class Fence(NamedTuple):
    loc: Loc
    direction: Direction


@dataclasses.dataclass
class Region:
    area: set[Loc]
    perimeter: set[Fence]

    def get_region_cost(self, *, bulk_discount: bool) -> int:
        if not bulk_discount:
            return len(self.area) * len(self.perimeter)
        n_sides = 0
        all_counted_fences = set()
        for fence_initial in self.perimeter:
            if fence_initial in all_counted_fences:
                continue
            this_side = {fence_initial}
            fences_to_check = {fence_initial}
            while len(fences_to_check) > 0:
                fences_to_check_next = set()
                for fence_to_check in fences_to_check:
                    for shift_direction in fence_to_check.direction.perpendiculars():
                        adjacent_loc_inline = fence_to_check.loc.shift(shift_direction)
                        if (adjacent_fence_inline := Fence(adjacent_loc_inline, fence_to_check.direction)) in self.perimeter:
                            if adjacent_fence_inline not in this_side:
                                fences_to_check_next.add(adjacent_fence_inline)
                            this_side.add(adjacent_fence_inline)
                fences_to_check = fences_to_check_next
            all_counted_fences.update(this_side)
            n_sides += 1
        return len(self.area) * n_sides


class RegionFinder(GridSolver):
    def find_regions(self) -> list[Region]:
        to_return = []
        all_searched_locs = set()
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                region_start_loc = Loc(i, j)
                if region_start_loc in all_searched_locs:
                    continue
                this_symbol = self.grid[region_start_loc]
                area = set()
                perimeter = set()
                to_search = {region_start_loc}
                while len(to_search) > 0:
                    to_search_new = set()
                    for loc in to_search:
                        if loc in area:  # already analyzed this one
                            continue
                        area.add(loc)
                        for direction in GridCardinalDirection.values():
                            adjacent_loc = loc.shift(direction)
                            if self.is_loc_in_bounds(adjacent_loc):
                                if self.grid[adjacent_loc] == this_symbol:
                                    to_search_new.add(adjacent_loc)
                                else:
                                    perimeter.add(Fence(loc, direction))
                            else:
                                perimeter.add(Fence(loc, direction))
                    to_search = to_search_new
                to_return.append(Region(area, perimeter))
                all_searched_locs.update(area)
        return to_return


def main(input_parsed: InputData):
    regions = RegionFinder(input_parsed).find_regions()
    cost1 = sum(region.get_region_cost(bulk_discount=False) for region in regions)
    print(f"{cost1 = }")
    cost2 = sum(region.get_region_cost(bulk_discount=True) for region in regions)
    print(f"{cost2 = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
