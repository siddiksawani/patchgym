from pathlib import Path

from patchgym.tasks import load_task


def test_loads_first_task_metadata() -> None:
    task = load_task(Path("tasks") / "task_001_off_by_one")

    assert task.task_id == "task_001_off_by_one"
    assert task.bug_type == "off_by_one"
    assert "replace_range_len_minus_one_with_range_len" in task.allowed_actions
