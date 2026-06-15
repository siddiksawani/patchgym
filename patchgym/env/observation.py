"""Observation model returned by PatchEnv."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Observation:
    task_id: str
    step: int
    tests_passed: int
    tests_failed: int
    last_action: str | None
    last_error_type: str | None
    code_hash: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
