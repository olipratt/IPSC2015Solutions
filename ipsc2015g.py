import logging

import time
import sys

from problem2015g.puzzlereader import PuzzleReader
from problem2015g.company import create_company_model

log = logging.getLogger(__name__)


PUZZLE_1_INPUT_FILE = "problem2015g/g1.in"
PUZZLE_1_RESULT_FILE = "problem2015g/g1.out"
PUZZLE_2_INPUT_FILE = "problem2015g/g2.in"
PUZZLE_2_RESULT_FILE = "problem2015g/g2.out"


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

        iter_start_time = time.time()
        company = create_company_model(next_puzzle.num_employees,
                                       next_puzzle.hierarchy_spec)

        log.info("Prep time: %.3fs", time.time() - iter_start_time)
        iter_start_time = time.time()

        total = company.process_event_queue(next_puzzle.event_queue)
        solution = total % (10**9 + 7)

        log.info("Calculation time: %.3fs", time.time() - iter_start_time)
        log.info("Solution: %r", solution)

        assert solution == next_puzzle.expected_result, \
            "%r != %r" % (solution, next_puzzle.expected_result)

    log.info("Total run time: %.3fs", time.time() - overall_start_time)
