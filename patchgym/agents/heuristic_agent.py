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
                "replace_plus_one_with_minus_one",
                "replace_less_than_with_less_equal",
                "replace_greater_than_with_greater_equal",
            ]
        if "none" in bug_type or "None" in error_type:
            return ["add_none_guard"]
        if "empty" in bug_type or "IndexError" in error_type:
            return ["add_empty_list_guard"]
        if "less_equal" in bug_type:
            return ["replace_less_equal_with_less_than"]
        if "greater_equal" in bug_type:
            return ["replace_greater_equal_with_greater_than"]
        if "less_than" in bug_type:
            return ["replace_less_than_with_less_equal"]
        if "greater_than" in bug_type:
            return ["replace_greater_than_with_greater_equal"]
        if "not_equal" in bug_type:
            return ["replace_not_equal_with_equal_equal"]
        if "equal_equal" in bug_type:
            return ["replace_equal_equal_with_not_equal"]
        if "membership" in bug_type:
            return ["replace_if_in_with_if_not_in"]
        if "logic" in bug_type:
            return ["replace_or_with_and", "replace_and_with_or"]
        if "boolean" in bug_type:
            return [
                "replace_return_false_with_return_true",
                "replace_return_true_with_return_false",
            ]
        if "operator" in bug_type or "comparison" in bug_type or error_type == "assertion_failure":
            return [
                "replace_greater_than_with_greater_equal",
                "replace_less_than_with_less_equal",
                "replace_less_equal_with_less_than",
                "replace_greater_equal_with_greater_than",
                "replace_equal_equal_with_not_equal",
                "replace_not_equal_with_equal_equal",
            ]
        return []
