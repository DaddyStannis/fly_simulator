from typing import Callable, Any
from abc import ABC


Callback = Callable[[], None]


class Observable(ABC):
    observers: dict[Any, list[Callback]] = {}

    def attach(self, cb: Callback, event: Any):
        if event not in self.observers:
            self.observers[event] = []
        self.observers[event].append(cb)

    def detach(self, cb, event):
        if event in self.observers:
            self.observers[event].remove(cb)

    def notify(self, event: Any):
        for e, callbacks in self.observers.items():
            if event == e:
                for cb in callbacks:
                    cb()
