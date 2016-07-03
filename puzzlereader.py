import logging

from collections import namedtuple

from events import ReadEvent, MemoEvent

log = logging.getLogger(__name__)


PuzzleSpec = namedtuple("PuzzleSpec", ["num_employees",
                                       "hierarchy_spec",
                                       "event_queue",
                                       "expected_result"])


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

        n, c, q = map(int, self._handle.readline().strip().split(" "))
        log.info("num employees, num_ties, num_events: %r, %r, %r", n, c, q)

        hierarchy_spec = map(int, self._handle.readline().strip().split(" "))

        event_queue = []
        event_no = 1

        next_line = self._handle.readline().strip()
        while next_line != "":
            log.debug("Processing event: %r", event_no)
            person_number, importance, tie = map(int, next_line.split(" "))
            if tie == 0:
                assert importance == 0
                event_queue.append(ReadEvent(person_number, event_no))
            else:
                event_queue.append(MemoEvent(person_number,
                                             importance,
                                             tie))

            next_line = self._handle.readline()
            if next_line == "":
                self._end_of_file = True
            next_line = next_line.strip()
            event_no += 1

        assert len(event_queue) == q

        expected_result = int(self._result_handle.readline().strip())

        return PuzzleSpec(n, hierarchy_spec, event_queue, expected_result)
