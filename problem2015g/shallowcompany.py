import logging

from .events import MemoEvent, ReadEvent

log = logging.getLogger(__name__)


class MemoQueue(list):

    def expand(self, index, sublist):
        self[index:index + 1] = sublist

    def append(self, queued_memo):
        self.expand(len(self), [queued_memo])


class ShallowCompany(object):

    def __init__(self, num_employees, hierarchy_spec):
        self._num_employees = num_employees
        self._employees = [Employee(1)]

        for index, manager_number in enumerate(hierarchy_spec):
            employee_number = index + 2
            new_employee = Employee(employee_number)
            self._employees.append(new_employee)
            self._employees[manager_number - 1].add_report(new_employee)

        assert len(self._employees) == num_employees

    def get_employee(self, employee_number):
        return self._employees[employee_number - 1]

    def expand_memo(self, queued_memo):
        employee = self.get_employee(queued_memo.person_number)
        new_memos = employee.expand_memo(queued_memo)
        return new_memos

    def get_tie(self, memo_queue, employee_number):
        result = 0
        index = 0
        while result == 0:
            while index < len(memo_queue):
                queued_memo = memo_queue[index]
                if queued_memo.person_number <= employee_number:
                    memo_queue.expand(index, self.expand_memo(queued_memo))
                else:
                    index += 1
            else:
                result = self.get_employee(employee_number).tie

        return result

    def process_event_queue(self, event_queue):
        """ Handle a list of events and return the result of processing them.
        """
        memo_queue = MemoQueue()
        total = 0

        for index, next_event in enumerate(event_queue):
            log.debug("Processing event number: %r", index)
            log.debug("Events queued: %r", len(memo_queue))
            if isinstance(next_event, ReadEvent):
                total += (next_event.multiplier *
                          self.get_tie(memo_queue, next_event.person_number))
            else:
                memo_queue.append(next_event)

        return total


class Employee(object):

    def __init__(self, number):
        self._number = number
        self._reports = []
        self._tie = 1

    @property
    def number(self):
        return self._number

    @property
    def tie(self):
        return self._tie

    def add_report(self, report):
        self._reports.append(report)

    def expand_memo(self, queued_memo):
        self._tie = queued_memo.tie
        if queued_memo.importance == 0:
            return []
        else:
            return [MemoEvent(report.number,
                              queued_memo.importance - 1,
                              queued_memo.tie)
                    for report in self._reports]
