import logging

from collections import namedtuple
import bisect

log = logging.getLogger(__name__)

MemoEvent = namedtuple("MemoEvent", ["person_number", "importance", "tie"])
ReadEvent = namedtuple("ReadEvent", ["person_number", "multiplier"])


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
