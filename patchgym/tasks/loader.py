"""Load PatchGym task metadata from disk."""

from __future__ import annotations

import json
from pathlib import Path

from patchgym.tasks.schema import Task


class TaskLoader:
    def load(self, task_dir: str | Path) -> Task:
        task_path = Path(task_dir).resolve()
        metadata_path = task_path / "metadata.json"
        buggy_path = task_path / "buggy.py"
        tests_path = task_path / "tests.py"
        readme_path = task_path / "README.md"

        for path in (metadata_path, buggy_path, tests_path, readme_path):
            if not path.is_file():
                raise FileNotFoundError(f"Required task file missing: {path}")

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        return Task.from_metadata(task_path, metadata)


def load_task(task_dir: str | Path) -> Task:
    return TaskLoader().load(task_dir)
