"""Small tabular Q-learning baseline."""

from __future__ import annotations

import random
from collections import defaultdict
from collections.abc import Sequence

from patchgym.agents.base import BaseAgent


class QLearningAgent(BaseAgent):
    def __init__(
        self,
        action_space: Sequence[str],
        bug_type: str | None = None,
        learning_rate: float = 0.4,
        discount: float = 0.9,
        epsilon: float = 0.1,
        seed: int | None = None,
    ) -> None:
        super().__init__(action_space)
        self.bug_type = bug_type or ""
        self.learning_rate = learning_rate
        self.discount = discount
        self.epsilon = epsilon
        self._rng = random.Random(seed)
        self.q_table: defaultdict[str, dict[str, float]] = defaultdict(dict)

    def act(self, observation: dict[str, object]) -> str:
        self._require_actions()
        if self._rng.random() < self.epsilon:
            return self._rng.choice(self.action_space)

        state = self._state_key(observation)
        values = self.q_table[state]
        return max(
            self.action_space,
            key=lambda action_id: (
                values.get(action_id, self._initial_value(action_id)),
                -self.action_space.index(action_id),
            ),
        )

    def observe(
        self,
        observation: dict[str, object],
        action: str,
        reward: float,
        next_observation: dict[str, object],
        done: bool,
        truncated: bool,
    ) -> None:
        state = self._state_key(observation)
        next_state = self._state_key(next_observation)
        current = self.q_table[state].get(action, self._initial_value(action))
        future = 0.0
        if not done and not truncated:
            future_values = self.q_table[next_state]
            future = max(
                future_values.get(candidate, self._initial_value(candidate))
                for candidate in self.action_space
            )
        target = reward + self.discount * future
        self.q_table[state][action] = current + self.learning_rate * (target - current)

    def _state_key(self, observation: dict[str, object]) -> str:
        return "|".join(
            [
                f"bug={self.bug_type}",
                f"passed={observation.get('tests_passed', 0)}",
                f"error={observation.get('last_error_type') or 'none'}",
                f"step={observation.get('step', 0)}",
            ]
        )

    def _initial_value(self, action_id: str) -> float:
        if "off_by_one" in self.bug_type:
            if action_id in {
                "replace_range_len_minus_one_with_range_len",
                "replace_minus_one_with_plus_one",
                "replace_plus_one_with_minus_one",
                "replace_less_than_with_less_equal",
                "replace_greater_than_with_greater_equal",
            }:
                return 0.2
        if "none" in self.bug_type and action_id == "add_none_guard":
            return 0.2
        if "empty" in self.bug_type and action_id == "add_empty_list_guard":
            return 0.2
        if "logic" in self.bug_type and action_id in {
            "replace_and_with_or",
            "replace_or_with_and",
        }:
            return 0.2
        if "boolean" in self.bug_type and action_id.startswith("replace_return_"):
            return 0.2
        if any(token in self.bug_type for token in ("operator", "comparison", "membership")):
            if action_id.startswith("replace_"):
                return 0.1
        return 0.0
