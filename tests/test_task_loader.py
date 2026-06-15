from pathlib import Path

import pytest

from patchgym.tasks import load_task
from patchgym.tasks.schema import Task


def test_loads_first_task_metadata() -> None:
    task = load_task(Path("tasks") / "task_001_off_by_one")

    assert task.task_id == "task_001_off_by_one"
    assert task.bug_type == "off_by_one"
    assert "replace_range_len_minus_one_with_range_len" in task.allowed_actions


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
