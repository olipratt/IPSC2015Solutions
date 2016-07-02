# Outline of Design
# -----------------
#
# - Build a company, with an array of employees indexable by employee number.
# - While building, track a list of leaf nodes - sorted by employee number,
#   so when a report is added, they are added in sorted position (which falls
#   out basically for free because they arrive in order), and their manager is
#   searched for and removed if present (array is sorted so search is cheap).
# - Calculate the management line for each leaf in turn, populate them with a
#   summary, of this line then pop the end off the line and populate the
#   summary for their manager, and so on.
#     - A possible optimisation here is to check if the manager has a summary,
#       and if so just defer to that.

import logging

import time
import bisect

log = logging.getLogger(__name__)


TEST_FILE = "g1.in"


# The size of the gaps in the management line summaries. Ideally this would be
# dynamic based on the org size / depth.
SUMMARY_INTERVAL = 1


class Company(object):
    def __init__(self, num_employees, hierarchy_spec):
        self._num_employees = num_employees

        root_employee = Employee(self, 1, None)
        root_employee.populate_line_summary([])
        self._employees = [root_employee]

        sorted_leaf_employee_numbers = []

        for index, manager_number in enumerate(hierarchy_spec):
            employee_number = index + 2
            log.debug("Processing employee: %r", employee_number)

            manager = self.get_employee(manager_number)

            new_employee = Employee(self, employee_number, manager)
            self._employees.append(new_employee)

            mgr_idx = bisect.bisect_left(sorted_leaf_employee_numbers,
                                         manager.number)
            if (mgr_idx != len(sorted_leaf_employee_numbers) and
                    sorted_leaf_employee_numbers[mgr_idx] == manager.number):
                sorted_leaf_employee_numbers.pop(mgr_idx)
            sorted_leaf_employee_numbers.append(new_employee.number)

        assert len(self._employees) == num_employees

        log.info("Number of leaves: %r", len(sorted_leaf_employee_numbers))

        for leaf_employee_number in sorted_leaf_employee_numbers:
            log.info("Processing leaf_employee: %r", leaf_employee_number)
            leaf_employee = self.get_employee(leaf_employee_number)
            full_line = leaf_employee.build_line_summary()
            if full_line is None:
                continue
            manager = leaf_employee.manager
            full_line.pop(0)
            while manager.populate_line_summary(full_line):
                log.debug("Processing manager: %r", manager.number)
                manager = manager.manager
                full_line.pop(0)

        log.info("Completed setup")

    def get_employee(self, employee_number):
        return self._employees[employee_number - 1]


class Employee(object):

    def __init__(self, company, number, manager):
        self._company = company
        self._number = number
        self._manager = manager
        self._line_summary = None

    @property
    def number(self):
        return self._number

    @property
    def manager(self):
        return self._manager

    @property
    def line_summary(self):
        return self._line_summary

    def build_full_line(self):
        full_line = []
        manager = self._manager
        while manager is not None:
            full_line.append(manager.number)
            manager = manager.manager

        assert full_line[-1] == 1
        return full_line

    def populate_line_summary(self, full_line):
        if self._line_summary is not None:
            return False

        num_entries = len(full_line) / SUMMARY_INTERVAL
        if num_entries <= 1:
            self._line_summary = ([], [])
        else:
            employee_numbers = []
            distance = []
            for index in range(len(full_line) - 1,
                               -1,
                               -SUMMARY_INTERVAL):
                employee_numbers.append(full_line[index])
                distance.append(index + 1)
            self._line_summary = (employee_numbers, distance)

        return True

    def build_line_summary(self):
        if self._manager.line_summary is not None:
            return None

        full_line = self.build_full_line()

        self.populate_line_summary(full_line)

        return full_line

    def in_management_line(self, manager, max_distance):
        log.debug("Checking if %r is within %r of %r",
                  self._number, max_distance, manager)
        if manager > self._number:
            return False
        if manager == self._number:
            return True
        if max_distance == 0:
            return False

        # Jump to the closest place in the line using the summary.
        managee = self
        if managee._line_summary is None:
            managee = managee.manager
            max_distance -= 1

        log.debug("Looking in %r for %r", managee._line_summary[0], manager)
        start_manager_idx = bisect.bisect_left(managee._line_summary[0],
                                               manager)
        log.debug("Found closest index of %r", start_manager_idx)

        if start_manager_idx != len(managee._line_summary[0]):
            log.debug("This is a better start position")
            max_distance -= managee._line_summary[1][start_manager_idx]
            if max_distance < 0:
                log.debug("Distance is too great")
                return False
            managee = self._company.get_employee(
                managee._line_summary[0][start_manager_idx])

        log.debug("Checking if %r is within %r of %r",
                  managee._number, max_distance, manager)
        if manager == managee._number:
            return True

        while max_distance > 0:
            next_manager = managee.manager
            if next_manager is None:
                return False

            if manager > next_manager.number:
                return False
            if next_manager.number == manager:
                return True

            managee = next_manager
            max_distance -= 1

        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    with open(TEST_FILE) as handle:
        num_tests = int(handle.readline().strip())
        log.info("Number of tests: %s", num_tests)
        handle.readline()

        end_of_file = False

        while not end_of_file:
            iter_start_time = time.time()
            n, c, q = map(int, handle.readline().strip().split(" "))
            log.info("num employees, num_ties, num_events: %r, %r, %r",
                     n, c, q)

            hierarchy_spec = map(int, handle.readline().strip().split(" "))

            company = Company(n, hierarchy_spec)
            hierarchy_spec = None
            event_queue = []
            event_no = 1

            next_line = handle.readline().strip()
            while next_line != "":
                # log.debug("Processing event: %r", event_no)
                # log.debug("Current queue: %r", memo_queue)
                person_number, importance, tie = map(int, next_line.split(" "))
                if tie == 0:
                    assert importance == 0
                    event_queue.append((person_number, event_no))
                else:
                    event_queue.append((person_number, importance, tie))

                next_line = handle.readline()
                if next_line == "":
                    end_of_file = True
                next_line = next_line.strip()
                event_no += 1

            log.info("Prep time: %r", time.time() - iter_start_time)
            iter_start_time = time.time()

            total = 0
            read_queue = []

            while len(event_queue) > 0:
                log.info("Events left: %r", len(event_queue))
                log.info("Events queued: %r", len(read_queue))
                if len(event_queue[-1]) == 2:
                    read_queue.append(event_queue.pop())
                else:
                    memo_event = event_queue.pop()
                    # log.debug("Search depth: %r", memo_event[1])
                    new_read_queue = []
                    for read_event in read_queue:
                        managee = company.get_employee(read_event[0])
                        if managee.in_management_line(memo_event[0],
                                                      memo_event[1]):
                            # if company.in_management_line(memo_event[0],
                            #                               read_event[0],
                            #                               memo_event[1]):
                            total += memo_event[2] * read_event[1]
                        else:
                            new_read_queue.append(read_event)

                    read_queue = new_read_queue

            for read_event in read_queue:
                total += 1 * read_event[1]

            log.info("Calculation time: %r", time.time() - iter_start_time)
            log.info("Solution: %r", total % (10**9 + 7))
