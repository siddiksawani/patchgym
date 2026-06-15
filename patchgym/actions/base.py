"""Base types for safe code transformations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PatchAction:
    id: str
    name: str
    description: str

    def apply(self, code: str) -> str:
        raise NotImplementedError

    def changes(self, code: str) -> bool:
        return self.apply(code) != code
