"""Base interface for simple PatchGym agents."""

from __future__ import annotations

from collections.abc import Sequence


class BaseAgent:
    def __init__(self, action_space: Sequence[str]) -> None:
        self.action_space = list(action_space)

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def act(self, observation: dict[str, object]) -> str:
        raise NotImplementedError

    def _require_actions(self) -> None:
        if not self.action_space:
            raise ValueError(f"{self.name} requires at least one action.")
