"""Random baseline agent."""

from __future__ import annotations

import random
from collections.abc import Sequence

from patchgym.agents.base import BaseAgent


class RandomAgent(BaseAgent):
    def __init__(self, action_space: Sequence[str], seed: int | None = None) -> None:
        super().__init__(action_space)
        self._rng = random.Random(seed)

    def act(self, observation: dict[str, object]) -> str:
        self._require_actions()
        return self._rng.choice(self.action_space)
