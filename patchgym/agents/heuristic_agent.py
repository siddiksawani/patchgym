"""Metadata-aware baseline agent with small repair preferences."""

from __future__ import annotations

from collections.abc import Sequence

from patchgym.agents.base import BaseAgent


class HeuristicAgent(BaseAgent):
    def __init__(self, action_space: Sequence[str], bug_type: str | None = None) -> None:
        super().__init__(action_space)
        self.bug_type = bug_type

    def act(self, observation: dict[str, object]) -> str:
        self._require_actions()
        for action_id in self._preferred_actions(observation):
            if action_id in self.action_space:
                return action_id
        return self.action_space[0]

    def _preferred_actions(self, observation: dict[str, object]) -> list[str]:
        bug_type = self.bug_type or ""
        error_type = str(observation.get("last_error_type") or "")

        if "off_by_one" in bug_type:
            return [
                "replace_range_len_minus_one_with_range_len",
                "replace_minus_one_with_plus_one",
                "replace_less_than_with_less_equal",
                "replace_greater_than_with_greater_equal",
            ]
        if "none" in bug_type or "None" in error_type:
            return ["add_none_guard"]
        if "empty" in bug_type or "IndexError" in error_type:
            return ["add_empty_list_guard"]
        if "operator" in bug_type or "comparison" in bug_type or error_type == "assertion_failure":
            return [
                "replace_greater_than_with_greater_equal",
                "replace_less_than_with_less_equal",
                "replace_equal_equal_with_not_equal",
                "replace_not_equal_with_equal_equal",
            ]
        return []
