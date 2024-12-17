import concurrent.futures as futures
import dataclasses
import math
import os
import re
from typing import Self

from advent_utils import read_input, timer

InputData = tuple[tuple[int, int, int], list[int]]


def get_parsed_input() -> InputData:
    input_raw = read_input(17)
    registers_str, instructions_str = input_raw.strip().split("\n\n")
    a, b, c = map(int, re.findall(r"Register [ABC]: (\d+)", registers_str))
    instructions = list(map(int, instructions_str.removeprefix("Program: ").split(",")))
    return (a, b, c), instructions


@dataclasses.dataclass
class Registers:
    a: int
    b: int
    c: int

    @classmethod
    def from_tuple(cls, tup: tuple[int, int, int]) -> Self:
        a, b, c = tup
        return cls(a=a, b=b, c=c)

    def get_combo_operand(self, operand: int) -> int:
        if 0 <= operand <= 3:
            return operand
        elif operand == 4:
            return self.a
        elif operand == 5:
            return self.b
        elif operand == 6:
            return self.c
        else:
            raise ValueError(f"invalid operand: {operand}")

    def __str__(self) -> str:
        return f"({self.a},{self.b},{self.c})"


class HaltProgram(StopIteration):
    """raised when the program should stop"""


class InfiniteLoopError(Exception):
    """raised when we hit an infinite loop"""


class Runner:
    __slots__ = ["registers", "instructions", "ptr", "output", "states_seen"]

    def __init__(self, input_parsed: InputData):
        super().__init__()
        registers_tup, instructions = input_parsed
        self.registers = Registers.from_tuple(registers_tup)
        self.instructions = instructions
        self.ptr = 0
        self.output = []
        self.states_seen = set()

    def _run_one_step(self):
        # check halting status / get next input
        try:
            opcode = self.instructions[self.ptr]
            operand = self.instructions[self.ptr + 1]
        except IndexError:
            raise HaltProgram
        # check for infinite loop
        state_str = f"{self.registers}:{self.ptr}"
        if state_str in self.states_seen:
            raise InfiniteLoopError
        self.states_seen.add(state_str)
        # do the thing
        ptr_next = self.ptr + 2
        if opcode == 0:  # adv
            self.registers.a = int(self.registers.a / (2 ** self.registers.get_combo_operand(operand)))
        elif opcode == 1:  # bxl
            self.registers.b = self.registers.b ^ operand
        elif opcode == 2:  # bst
            self.registers.b = self.registers.get_combo_operand(operand) % 8
        elif opcode == 3:  # jnz
            if self.registers.a != 0:
                ptr_next = operand
        elif opcode == 4:  # bxc
            self.registers.b = self.registers.b ^ self.registers.c
        elif opcode == 5:  # out
            self.output.append(self.registers.get_combo_operand(operand) % 8)
        elif opcode == 6:  # bdv
            self.registers.b = int(self.registers.a / (2 ** self.registers.get_combo_operand(operand)))
        elif opcode == 7:  # cdv
            self.registers.c = int(self.registers.a / (2 ** self.registers.get_combo_operand(operand)))
        else:
            raise ValueError(f"invalid opcode: {opcode}")
        # advance to next instruction
        self.ptr = ptr_next

    def run(self) -> list[int]:
        # just execute the program
        try:
            while True:
                self._run_one_step()
        except HaltProgram:
            return self.output

    def run_returns_instructions(self) -> bool:
        n_expected = len(self.instructions)
        try:
            while True:
                self._run_one_step()
                n_out = len(self.output)
                if n_out > n_expected:
                    return False  # our output has grown too long
                if n_out > 0 and self.output[-1] != self.instructions[n_out - 1]:
                    return False  # our most recent output doesn't match the corresponding expected value
        except HaltProgram:
            return self.output == self.instructions


def try_range(input_parsed: InputData, a_start: int, a_end: int) -> int | None:
    for a in range(a_start, a_end):
        runner = Runner(input_parsed)
        runner.registers.a = a
        try:
            if runner.run_returns_instructions():
                return a
        except InfiniteLoopError:
            continue
    return None


def try_range_threads(input_parsed: InputData, a_start: int, a_end: int) -> int | None:
    print(f"try_range_threads({a_start=}, {a_end=})")
    with futures.ThreadPoolExecutor() as thread_executor:
        thread_chunk_size = math.ceil((a_end - a_start) / thread_executor._max_workers)
        futures_ = [
            thread_executor.submit(try_range, input_parsed, a_start_inner, min(a_end, a_start_inner + thread_chunk_size))
            for a_start_inner in range(a_start, a_end, thread_chunk_size)
        ]
        for future in futures.as_completed(futures_):
            answer = future.result()
            if answer is not None:
                return answer
    return None


def part_2(input_parsed: InputData, process_chunk_size: int = 3_000_000) -> int:
    with futures.ProcessPoolExecutor() as process_executor:
        a_start = 1
        while True:
            pending_futures = []
            for _ in range(os.cpu_count() - 2):
                pending_futures.append(process_executor.submit(try_range_threads, input_parsed, a_start, a_start + process_chunk_size))
                a_start += process_chunk_size
            for future_ in pending_futures:
                answer = future_.result()
                if answer is not None:
                    return answer
                pending_futures.append(process_executor.submit(try_range_threads, input_parsed, a_start, a_start + process_chunk_size))
                a_start += process_chunk_size


def main(input_parsed: InputData):
    output = Runner(input_parsed).run()
    print("output:", ",".join(str(o) for o in output))
    modified_a = part_2(input_parsed)
    print(f"{modified_a = }")


if __name__ == "__main__":
    with timer():
        main(get_parsed_input())
