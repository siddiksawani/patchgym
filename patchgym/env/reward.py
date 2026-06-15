"""Reward calculation for PatchEnv."""

from __future__ import annotations

from patchgym.runners import TestResult


def calculate_reward(previous: TestResult, current: TestResult) -> float:
    reward = 0.0

    if current.all_passed:
        reward += 10.0

    if current.passed > previous.passed:
        reward += 2.0 * (current.passed - previous.passed)
    elif current.passed == previous.passed:
        reward -= 0.5

    if current.error_type == "syntax_error":
        reward -= 2.0
    elif current.error_type == "timeout":
        reward -= 3.0

    reward -= 0.1
    return round(reward, 3)
