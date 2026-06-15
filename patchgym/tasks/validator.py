"""Validation helpers for PatchGym task folders."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from patchgym.actions import ACTION_REGISTRY
from patchgym.tasks.loader import load_task


@dataclass(frozen=True)
class TaskValidation:
    task_id: str
    path: Path
    errors: list[str]

    @property
    def valid(self) -> bool:
        return not self.errors


def validate_task(task_dir: str | Path) -> TaskValidation:
    path = Path(task_dir)
    errors: list[str] = []

    try:
        task = load_task(path)
    except Exception as exc:
        return TaskValidation(task_id=path.name, path=path, errors=[str(exc)])

    if task.task_id != path.name:
        errors.append(f"metadata.task_id {task.task_id!r} must match directory {path.name!r}")
    if task.max_steps < 1:
        errors.append("metadata.max_steps must be at least 1")
    if not task.allowed_actions:
        errors.append("metadata.allowed_actions must contain at least one action")

    unknown_actions = [
        action_id for action_id in task.allowed_actions if action_id not in ACTION_REGISTRY
    ]
    if unknown_actions:
        errors.append(f"unknown allowed action(s): {', '.join(unknown_actions)}")

    return TaskValidation(task_id=task.task_id, path=task.path, errors=errors)


def validate_tasks(tasks_dir: str | Path) -> list[TaskValidation]:
    root = Path(tasks_dir)
    task_dirs = sorted(path for path in root.iterdir() if path.is_dir())
    return [validate_task(path) for path in task_dirs]
