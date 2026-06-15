from pathlib import Path

import pytest

from patchgym.tasks import load_task
from patchgym.tasks.schema import Task
from patchgym.tasks.validator import validate_tasks

TASK_IDS = [
    "task_001_off_by_one",
    "task_002_none_guard",
    "task_003_wrong_operator",
    "task_004_empty_list_guard",
    "task_005_less_equal_boundary",
    "task_006_not_equal_operator",
    "task_007_greater_equal_boundary",
    "task_008_less_than_discount",
    "task_009_none_title_guard",
    "task_010_sum_off_by_one",
]


def test_loads_first_task_metadata() -> None:
    task = load_task(Path("tasks") / "task_001_off_by_one")

    assert task.task_id == "task_001_off_by_one"
    assert task.bug_type == "off_by_one"
    assert "replace_range_len_minus_one_with_range_len" in task.allowed_actions


def test_all_ten_tasks_validate() -> None:
    results = validate_tasks(Path("tasks"))

    assert [result.task_id for result in results] == TASK_IDS
    assert all(result.valid for result in results)


def test_task_metadata_rejects_bool_for_integer_field() -> None:
    metadata = {
        "task_id": "task_bool",
        "title": "Bool should not validate as int",
        "difficulty": "easy",
        "bug_type": "schema",
        "max_steps": True,
        "expected_fix": "Use an integer.",
        "allowed_actions": [],
        "tags": [],
    }

    with pytest.raises(ValueError, match="metadata.max_steps"):
        Task.from_metadata(Path("tasks") / "task_bool", metadata)
