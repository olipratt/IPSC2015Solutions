import logging

from collections import Counter
from math import sqrt

from .deepcompany import DeepCompany
from .shallowcompany import ShallowCompany


log = logging.getLogger(__name__)


class DepthMeasureCompany(object):
    def __init__(self, num_employees, hierarchy_spec):
        self._num_employees = num_employees
        self._employees = [DepthMeasureEmployee(1, None)]
        self._depth_counter = Counter()

        for index, manager_number in enumerate(hierarchy_spec):
            employee_number = index + 2
            manager = self.get_employee(manager_number)
            new_employee = DepthMeasureEmployee(employee_number, manager)
            self._employees.append(new_employee)
            self._depth_counter[new_employee.depth] += 1

        assert len(self._employees) == num_employees

    def get_employee(self, employee_number):
        return self._employees[employee_number - 1]

    def get_average_depth(self):
        return (sum(depth * count
                    for depth, count in self._depth_counter.items()) /
                sum(self._depth_counter.values()))


class DepthMeasureEmployee(object):
    def __init__(self, number, manager):
        self._number = number
        self._manager = manager
        if self._manager is None:
            self._depth = 0
        else:
            self._depth = self._manager.depth + 1

    @property
    def depth(self):
        return self._depth


def create_company_model(num_emloyees, hierarchy_spec):
    depth_measure_company = DepthMeasureCompany(num_emloyees, hierarchy_spec)
    average_depth = depth_measure_company.get_average_depth()
    log.info("Average depth: %r", average_depth)

    if average_depth > sqrt(num_emloyees):
        log.info("Using Deep Company model")
        return DeepCompany(num_emloyees, hierarchy_spec)
    else:
        log.info("Using Shallow Company model")
        return ShallowCompany(num_emloyees, hierarchy_spec)
