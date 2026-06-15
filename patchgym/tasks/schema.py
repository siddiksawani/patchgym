"""Task data model for phase one."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Task:
    task_id: str
    title: str
    difficulty: str
    bug_type: str
    max_steps: int
    expected_fix: str
    allowed_actions: list[str]
    tags: list[str]
    path: Path

    @classmethod
    def from_metadata(cls, path: Path, metadata: dict[str, object]) -> "Task":
        return cls(
            task_id=_required_str(metadata, "task_id"),
            title=_required_str(metadata, "title"),
            difficulty=_required_str(metadata, "difficulty"),
            bug_type=_required_str(metadata, "bug_type"),
            max_steps=_required_int(metadata, "max_steps"),
            expected_fix=_required_str(metadata, "expected_fix"),
            allowed_actions=_required_str_list(metadata, "allowed_actions"),
            tags=_required_str_list(metadata, "tags"),
            path=path,
        )


def _required_str(metadata: dict[str, object], key: str) -> str:
    value = metadata.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"metadata.{key} must be a non-empty string")
    return value


def _required_int(metadata: dict[str, object], key: str) -> int:
    value = metadata.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"metadata.{key} must be an integer")
    return value


def _required_str_list(metadata: dict[str, object], key: str) -> list[str]:
    value = metadata.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"metadata.{key} must be a list of strings")
    return value
