import json
from pathlib import Path
from shutil import copytree

import pytest

from patchgym.actions import PatchAction, get_action
from patchgym.env import PatchEnv, calculate_reward
from patchgym.runners import TestResult


def make_env(task_name: str = "task_003_wrong_operator", **kwargs: object) -> PatchEnv:
    kwargs.setdefault("trajectory_dir", None)
    return PatchEnv(Path("tasks") / task_name, **kwargs)


def test_reset_copies_task_and_returns_baseline_observation() -> None:
    with make_env() as env:
        obs, info = env.reset()

        assert obs["task_id"] == "task_003_wrong_operator"
        assert obs["step"] == 0
        assert obs["tests_passed"] == 2
        assert obs["tests_failed"] == 1
        assert obs["last_action"] is None
        assert info["action_id"] is None
        assert env.workspace_dir is not None
        assert (env.workspace_dir / "buggy.py").is_file()


def test_step_applies_action_and_solves_task() -> None:
    with make_env() as env:
        env.reset()

        obs, reward, done, truncated, info = env.step(
            "replace_greater_than_with_greater_equal"
        )

        assert done is True
        assert truncated is False
        assert reward > 10.0
        assert obs["step"] == 1
        assert obs["tests_passed"] == 3
        assert obs["tests_failed"] == 0
        assert obs["last_action"] == "replace_greater_than_with_greater_equal"
        assert info["changed"] is True


def test_step_truncates_at_task_max_steps() -> None:
    with make_env() as env:
        env.reset()

        for _ in range(env.task.max_steps):
            obs, _reward, done, truncated, _info = env.step(
                "replace_less_than_with_less_equal"
            )

        assert done is False
        assert truncated is True
        assert obs["step"] == env.task.max_steps


def test_step_rejects_action_outside_task_action_space() -> None:
    with make_env() as env:
        env.reset()

        with pytest.raises(ValueError, match="not allowed"):
            env.step("replace_return_true_with_return_false")


def test_action_space_exposes_registered_task_actions_only() -> None:
    env = make_env("task_002_none_guard")

    assert "add_none_guard" in env.action_space
    assert "add_empty_list_guard" in env.action_space
    assert len(env.action_space) >= 4


def test_env_rejects_task_metadata_with_unknown_action(tmp_path: Path) -> None:
    task_copy = tmp_path / "task_003_wrong_operator"
    copytree(Path("tasks") / "task_003_wrong_operator", task_copy)
    metadata_path = task_copy / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["allowed_actions"] = ["missing_action"]
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    with pytest.raises(ValueError, match="Unknown action"):
        PatchEnv(task_copy, trajectory_dir=None)


def test_step_rejects_unknown_action() -> None:
    with make_env() as env:
        env.reset()

        with pytest.raises(ValueError, match="Unknown action"):
            env.step("missing_action")


def test_step_accepts_registered_action_object() -> None:
    with make_env() as env:
        env.reset()

        _obs, _reward, done, _truncated, _info = env.step(
            get_action("replace_greater_than_with_greater_equal")
        )

        assert done is True


def test_step_rejects_forged_action_object_with_allowed_id() -> None:
    class ForgedAction(PatchAction):
        def apply(self, code: str) -> str:
            return "def is_adult(age):\n    return True\n"

    forged = ForgedAction(
        id="replace_greater_than_with_greater_equal",
        name="Forged",
        description="Bypass registry",
    )

    with make_env() as env:
        env.reset()

        with pytest.raises(ValueError, match="registry"):
            env.step(forged)


def test_step_requires_reset() -> None:
    env = make_env()

    with pytest.raises(RuntimeError, match="reset"):
        env.step("replace_greater_than_with_greater_equal")


def test_reward_penalizes_syntax_errors() -> None:
    previous = TestResult(
        passed=1,
        failed=1,
        total=2,
        return_code=1,
        stdout="",
        stderr="",
        duration_ms=10,
        error_type="assertion_failure",
    )
    current = TestResult(
        passed=1,
        failed=0,
        total=1,
        return_code=1,
        stdout="",
        stderr="",
        duration_ms=10,
        error_type="syntax_error",
    )

    assert calculate_reward(previous, current) == -2.6
