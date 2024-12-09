import numpy as np

from advent_utils import read_input, timer

InputData = list[int]


def get_parsed_input() -> InputData:
    input_raw = read_input(9)
    input_parsed = [int(c) for c in input_raw.strip()]
    if len(input_parsed) % 2 == 0:
        print("WARNING: input is an even length (disk spec ends with a gap)")
    return input_parsed


def disk_spec_to_disk(disk_spec: InputData) -> np.ndarray:
    n_blocks_needed = sum(disk_spec)
    print(f"{n_blocks_needed = }")
    disk = np.empty(n_blocks_needed, dtype=np.object_)
    disk_pointer = 0
    for i, block_count in enumerate(disk_spec):
        if i % 2 == 0:  # file
            to_write = i // 2  # file_id
        else:  # space
            to_write = None
        disk[disk_pointer:(disk_pointer + block_count)] = to_write
        disk_pointer += block_count
    assert disk_pointer == n_blocks_needed, "did not fill disk as expected"
    return disk


def compact_disk1(disk: np.ndarray):
    """modifies `disk` in-place, using algorithm for part 1"""
    if len(disk.shape) != 1:
        raise ValueError("disk must be a 1-dimensional array")
    next_empty = 0
    last_filled = disk.shape[0] - 1
    while True:
        while next_empty < last_filled and disk[next_empty] is not None:
            next_empty += 1
        while last_filled > next_empty and disk[last_filled] is None:
            last_filled -= 1
        if next_empty >= last_filled:
            break
        disk[next_empty] = disk[last_filled]
        disk[last_filled] = None


def compact_disk2(disk: np.ndarray, *, highest_file_id: int):
    """modifies `disk` in-place, using algorithm for part 2"""
    if len(disk.shape) != 1:
        raise ValueError("disk must be a 1-dimensional array")
    disk_len = disk.shape[0]
    # iterate through disk from end to start, handling each file ID in reverse order
    cursor = disk_len - 1
    for file_id in range(highest_file_id, -1, -1):
        # find the next file block
        while cursor >= 0:
            if disk[cursor] == file_id:
                break
            cursor -= 1
        else:
            print(f"WARNING: never found file with ID {file_id}")
            break
        # find the bounds of the file block
        file_end = cursor + 1
        while (prev := cursor - 1) >= 0 and disk[prev] == file_id:
            cursor = prev
        file_start = cursor
        file_size = file_end - file_start
        cursor = prev  # setup for next iteration of loop
        # look for the first empty space that can fit the file (only to the left of its current position)
        cursor_empty = 0
        while True:
            # find the next empty spot
            while cursor_empty < file_start:
                if disk[cursor_empty] is None:
                    break
                cursor_empty += 1
            else:  # no more empty spots to the left of the file in question
                break
            empty_start = cursor_empty
            # count how big it is
            while cursor_empty < disk_len and disk[cursor_empty] is None:
                cursor_empty += 1
            empty_end = cursor_empty
            empty_len = empty_end - empty_start
            # if it fits, move it
            if empty_len >= file_size:
                disk[empty_start:(empty_start + file_size)] = file_id
                disk[file_start:file_end] = None
                break


def get_checksum(disk: np.ndarray) -> int:
    if len(disk.shape) != 1:
        raise ValueError("disk must be a 1-dimensional array")
    return sum(
        i * file_id
        for i, file_id in enumerate(disk)
        if file_id is not None
    )


def main(input_parsed: InputData):
    disk = disk_spec_to_disk(input_parsed)
    # part 1
    disk1 = disk.copy()
    compact_disk1(disk1)  # in-place
    checksum1 = get_checksum(disk1)
    print(f"{checksum1 = }")
    # part 2
    disk2 = disk.copy()
    compact_disk2(disk2, highest_file_id=(len(input_parsed) // 2))  # in-place
    checksum2 = get_checksum(disk2)
    print(f"{checksum2 = }")
    # too big: 19931653800089


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
