import logging

from collections import namedtuple
import bisect

log = logging.getLogger(__name__)

MemoEvent = namedtuple("MemoEvent", ["person_number", "importance", "tie"])
ReadEvent = namedtuple("ReadEvent", ["person_number", "multiplier"])
