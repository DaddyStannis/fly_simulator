import time
import math
from typing import Callable, Any
from abc import ABC


Callback = Callable[[], None]


class Observable(ABC):
    def __init__(self):
        self.observers: dict[Any, list[Callback]] = {}

    def attach(self, cb: Callback, event: Any):
        if event not in self.observers:
            self.observers[event] = []
        self.observers[event].append(cb)

    def detach(self, cb, event):
        if event in self.observers:
            self.observers[event].remove(cb)

    def notify(self, event: Any):
        if event in self.observers:
            callbacks = self.observers[event]
            for cb in callbacks:
                cb()


def call_until(interval_secs: int, duration_secs: int, cb: Callback):
    start_timestamp = time.time()
    while start_timestamp + duration_secs >= time.time():
        time.sleep(interval_secs)
        cb()


def segment_length(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
