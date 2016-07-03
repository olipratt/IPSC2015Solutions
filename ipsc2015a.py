import logging

from collections import namedtuple
import sys
import time


log = logging.getLogger(__name__)


PUZZLE_1_INPUT_FILE = "problem2015a/a1.in"
PUZZLE_1_RESULT_FILE = "problem2015a/a1.out"
PUZZLE_2_INPUT_FILE = "problem2015a/a2.in"
PUZZLE_2_RESULT_FILE = "problem2015a/a2.out"


PuzzleSpec = namedtuple("PuzzleSpec", ["digits", "expected_result"])


class PuzzleReader(object):
    """Wrapper around the file defining the puzzle inputs."""

    def __init__(self, definition_file_path, result_file_path):
        self._handle = None
        self._result_handle = None
        self._num_tests = None
        self._end_of_file = False

        self._handle = open(definition_file_path)
        self._result_handle = open(result_file_path)

        # The file starts with a line containing the number of tests and
        # then a blank line.
        self._num_tests = int(self._handle.readline().strip())
        log.info("Number of tests: %s", self._num_tests)
        self._handle.readline()

    def read_next_puzzle(self):
        if self._end_of_file:
            return None

        next_line = self._handle.readline()
        if next_line == "":
            self._end_of_file = True
            return None

        digits = list(map(int, list(next_line.strip())))
        log.info("Next puzzle: %r", digits)

        self._handle.readline()

        expected_result = int(self._result_handle.readline().strip())

        return PuzzleSpec(digits, expected_result)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    overall_start_time = time.time()

    if len(sys.argv) == 1:
        input_file = PUZZLE_1_INPUT_FILE
        result_file = PUZZLE_1_RESULT_FILE
    else:
        input_file = PUZZLE_2_INPUT_FILE
        result_file = PUZZLE_2_RESULT_FILE

    puzzle_reader = PuzzleReader(input_file, result_file)

    while True:
        next_puzzle = puzzle_reader.read_next_puzzle()
        if next_puzzle is None:
            break

        digits = sorted(next_puzzle.digits, reverse=True)
        number_1 = digits.pop()
        number_2 = int(("").join(map(str, digits)))
        solution = number_1 + number_2

        log.info("Solution: %r", solution)

        assert solution == next_puzzle.expected_result, \
            "%r != %r" % (solution, next_puzzle.expected_result)

    log.info("Total run time: %.3fs", time.time() - overall_start_time)
