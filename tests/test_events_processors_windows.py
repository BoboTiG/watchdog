import pytest

from watchdog.utils.platform import is_windows

if not is_windows():
    pytest.skip(reason="Windows only", allow_module_level=True)

from watchdog import events_processor
from watchdog.observers import winapi

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
        ([REMOVED, ADDED2], [REMOVED, ADDED2]),
        ([REMOVED, ADDED2, ADDED], [REMOVED, ADDED2, ADDED]),
    ],
)
def test_process_windows_case_renaming_no_match(
    events: list[winapi.WinAPINativeEvent],
    expected: list[winapi.WinAPINativeEvent],
) -> None:
    assert events_processor.process_windows_case_renaming(events) == expected


@pytest.mark.parametrize(
    ("events", "expected"),
    [
        ([REMOVED, ADDED], [RENAMED_OLD, RENAMED_NEW]),
        ([REMOVED, ADDED, REMOVED, ADDED], [RENAMED_OLD, RENAMED_NEW, RENAMED_OLD, RENAMED_NEW]),
        ([REMOVED, ADDED, ADDED2, REMOVED, ADDED], [RENAMED_OLD, RENAMED_NEW, ADDED2, RENAMED_OLD, RENAMED_NEW]),
    ],
)
def test_process_windows_case_renaming_match(
    events: list[winapi.WinAPINativeEvent],
    expected: list[winapi.WinAPINativeEvent],
) -> None:
    assert events_processor.process_windows_case_renaming(events) == expected
