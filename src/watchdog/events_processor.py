from __future__ import annotations

import os.path
from typing import Callable, NamedTuple

from watchdog.utils.platform import PLATFORM_WINDOWS, get_platform_name


def process_windows_case_renaming(events: list) -> list:
    """`events` is of type list[winapi.WinAPINativeEvent]."""
    from watchdog.observers import winapi

    basename = os.path.basename
    idx, events_count = 0, len(events)
    while idx < events_count - 1:
        event1, event2 = events[idx], events[idx + 1]
        if (
            event1.is_removed
            and event2.is_added
            and basename(event1.src_path).lower() == basename(event2.src_path).lower()
        ):
            event1.action = winapi.FILE_ACTION_RENAMED_OLD_NAME
            event2.action = winapi.FILE_ACTION_RENAMED_NEW_NAME
    return events


class Processor(NamedTuple):
    platform: str
    priority: int
    handler: Callable[[list], list]


class EventsProcessorManager:
    """"""

    def __init__(self, *, populate: bool = True) -> None:
        """"""
        self.processors: list[Processor] = []
        self.current_platform = get_platform_name()

        if populate:
            self.add(PLATFORM_WINDOWS, process_windows_case_renaming)

    def add(self, platform: str, handler: Callable, *, priority: int = 0) -> None:
        """"""
        self.processors.append(Processor(platform, priority, handler))

    def remove(self, handler: Callable) -> None:
        """"""
        for processor in self.processors.copy():
            if processor.handler == handler:
                self.processors.remove(processor)
                break

    def process(self, events: list) -> list:
        """"""
        for processor in sorted(self.processors):
            if processor.platform in {"all", self.current_platform}:
                events = processor.handler(events)
        return events
