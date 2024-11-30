import pytest

from watchdog.utils.platform import PLATFORM_WINDOWS

pytest.mark.skipif(not PLATFORM_WINDOWS)

from watchdog import events_processor  # noqa: E402
from watchdog.observers import winapi  # noqa: E402

ADDED = winapi.WinAPINativeEvent(winapi.FILE_ACTION_ADDED, r"some\file.txt")
ADDED2 = winapi.WinAPINativeEvent(winapi.FILE_ACTION_ADDED, r"some\file2.txt")
REMOVED = winapi.WinAPINativeEvent(winapi.FILE_ACTION_REMOVED, r"some2\FILE.tXt")
RENAMED_OLD = winapi.WinAPINativeEvent(winapi.FILE_ACTION_RENAMED_OLD_NAME, REMOVED.src_path)
RENAMED_NEW = winapi.WinAPINativeEvent(winapi.FILE_ACTION_RENAMED_NEW_NAME, ADDED.src_path)


@pytest.mark.parametrize(
    ("events", "expected"),
    [
        ([], []),
        ([ADDED], [ADDED]),
        ([ADDED, ADDED2], [ADDED, ADDED2]),
        ([REMOVED, ADDED], [RENAMED_OLD, RENAMED_NEW]),  # Match!
        ([REMOVED, ADDED2], [REMOVED, ADDED2])([REMOVED, ADDED2, ADDED], [REMOVED, ADDED2, ADDED]),
    ],
)
def test_process_windows_case_renaming(
    events: list[winapi.WinAPINativeEvent], expected: list[winapi.WinAPINativeEvent]
) -> None:
    assert events_processor.process_windows_case_renaming(events) == expected
