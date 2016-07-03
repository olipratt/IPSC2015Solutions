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

import bisect

from .events import ReadEvent


log = logging.getLogger(__name__)


# The size of the gaps in the management line summaries. Ideally this would be
# dynamic based on the org size / depth.
SUMMARY_INTERVAL = 10000


class DeepCompany(object):
    """ Represents a hierarchy of employees. """

    def __init__(self, num_employees, hierarchy_spec):
        self._num_employees = num_employees
        self._employees = None

        self._init_employees_list()

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

        assert len(self._employees) == self._num_employees

        log.info("Number of leaves: %r", len(sorted_leaf_employee_numbers))

        for leaf_employee_number in sorted_leaf_employee_numbers:
            log.debug("Processing leaf_employee: %r", leaf_employee_number)
            leaf_employee = self.get_employee(leaf_employee_number)
            full_line = leaf_employee.build_line_summary()
            if full_line is None:
                continue
            manager = leaf_employee.manager
            full_line.pop()
            while manager.populate_line_summary(full_line):
                log.debug("Processing manager: %r", manager.number)
                manager = manager.manager
                full_line.pop()

        log.info("Completed setup")

    def _init_employees_list(self):
        """ Initialise the employee list with the root employee who is number
            one and has no manager.
        """
        root_employee = Employee(self, 1, None)
        root_employee.populate_line_summary([])
        self._employees = [root_employee]

    def get_employee(self, employee_number):
        return self._employees[employee_number - 1]

    def process_event_queue(self, event_queue):
        """ Handle a list of events and return the result of processing them.
        """
        total = 0
        read_queue = ReadEventQueue()

        while len(event_queue) > 0:
            log.debug("Events left: %r", len(event_queue))
            log.debug("Events queued: %r", len(read_queue))
            next_event = event_queue.pop()
            if isinstance(next_event, ReadEvent):
                read_queue.add_event(next_event)
            else:
                memo_event = next_event
                log.debug("Search depth: %r", memo_event.importance)
                for idx in read_queue.reverse_index_range():
                    # The list is sorted so once the update would only
                    # effect lower people in the company we're done.
                    if (memo_event.person_number >
                            read_queue[idx].person_number):
                        break

                    managee = self.get_employee(read_queue[idx].person_number)
                    if managee.in_management_line(memo_event.person_number,
                                                  memo_event.importance):
                        total += memo_event.tie * read_queue[idx].multiplier
                        read_queue.pop(idx)

        # Any remaining events use the employee's initial tie value of 1.
        for idx in read_queue.reverse_index_range():
            total += 1 * read_queue[idx].multiplier

        return total


class Employee(object):
    """ A single manager and/or managee. """

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

        full_line.reverse()
        assert full_line[0] == 1
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
            for index in range(0, len(full_line), SUMMARY_INTERVAL):
                employee_numbers.append(full_line[index])
                distance.append(len(full_line) - index)
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


class ReadEventQueue(object):
    """A queue of events requesting reading of an employee's tie."""

    def __init__(self):
        # The events are split across two lists to allow easy searching using
        # bisect. These lists must always be the same length.
        self._person_number_list = []
        self._multiplier_list = []

        self._iterator_index = 0

    def __len__(self):
        return len(self._person_number_list)

    def __getitem__(self, index):
        return ReadEvent(self._person_number_list[index],
                         self._multiplier_list[index])

    def add_event(self, read_event):
        # Either, this is a duplicate read event, so just add the
        # new multiplier to the existing stored one, or insert the
        # new read request into the list.
        index = bisect.bisect_left(self._person_number_list,
                                   read_event.person_number)
        if (index != len(self._person_number_list) and
                self._person_number_list[index] == read_event.person_number):
            self._multiplier_list[index] += read_event.multiplier
        else:
            self._person_number_list.insert(index, read_event.person_number)
            self._multiplier_list.insert(index, read_event.multiplier)

        assert len(self._person_number_list) == len(self._multiplier_list)

    def reverse_index_range(self):
        """Returns a range that can be used to iterate over the indexes of
           events in the queue in reverse, so that the current event can be
           safely popped from the queue without breaking the iteration. """
        return range(len(self) - 1, -1, -1)

    def pop(self, index):
        """Remove the event at the given index (without returning it). """
        self._person_number_list.pop(index)
        self._multiplier_list.pop(index)
