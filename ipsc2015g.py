import logging

import time

from puzzlereader import PuzzleReader
from deepcompany import DeepCompany

log = logging.getLogger(__name__)


TEST_FILE = "g1.in"
RESULT_FILE = "g1.out"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    puzzle_reader = PuzzleReader(TEST_FILE, RESULT_FILE)

    while True:
        next_puzzle = puzzle_reader.read_next_puzzle()
        if next_puzzle is None:
            break

        iter_start_time = time.time()
        company = DeepCompany(next_puzzle.num_employees,
                              next_puzzle.hierarchy_spec)

        log.info("Prep time: %r", time.time() - iter_start_time)
        iter_start_time = time.time()

        total = company.process_event_queue(next_puzzle.event_queue)
        solution = total % (10**9 + 7)

        log.info("Calculation time: %r", time.time() - iter_start_time)
        log.info("Solution: %r", solution)

        assert solution == next_puzzle.expected_result
