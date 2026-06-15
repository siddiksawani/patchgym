"""Minimal Gym-style environment for code-repair tasks."""

from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from patchgym.actions import ACTION_REGISTRY, PatchAction, get_action
from patchgym.env.observation import Observation
from patchgym.env.reward import calculate_reward
from patchgym.runners import PytestRunner, TestResult
from patchgym.tasks import Task, load_task
from patchgym.trajectories import TrajectoryLogger
from patchgym.utils.hashing import hash_code


class PatchEnv:
    def __init__(
        self,
        task_dir: str | Path,
        runner: PytestRunner | None = None,
        workspace_root: str | Path | None = None,
        trajectory_dir: str | Path | None = Path("outputs") / "trajectories",
        agent_name: str = "PatchEnv",
    ) -> None:
        self.task: Task = load_task(task_dir)
        self.runner = runner or PytestRunner()
        self.workspace_root = Path(workspace_root).resolve() if workspace_root else None
        if self.workspace_root is not None:
            self.workspace_root.mkdir(parents=True, exist_ok=True)
        self.trajectory_dir = Path(trajectory_dir) if trajectory_dir is not None else None
        self.agent_name = agent_name
        unknown_actions = [
            action_id for action_id in self.task.allowed_actions if action_id not in ACTION_REGISTRY
        ]
        if unknown_actions:
            raise ValueError(
                f"Unknown action(s) in {self.task.task_id}: {', '.join(unknown_actions)}"
            )
        self.action_space = list(self.task.allowed_actions)

        self._temp_dir: TemporaryDirectory[str] | None = None
        self._workspace_dir: Path | None = None
        self._buggy_path: Path | None = None
        self._current_result: TestResult | None = None
        self._current_code = ""
        self._step = 0
        self._done = False
        self._truncated = False
        self._last_action: str | None = None
        self._trajectory_logger: TrajectoryLogger | None = None

    @property
    def workspace_dir(self) -> Path | None:
        return self._workspace_dir

    @property
    def trajectory_path(self) -> Path | None:
        return self._trajectory_logger.path if self._trajectory_logger is not None else None

    def reset(self) -> tuple[dict[str, object], dict[str, object]]:
        self.close()
        self._temp_dir = TemporaryDirectory(
            dir=self.workspace_root,
            prefix=f"patchgym_{self.task.task_id}_",
        )
        self._workspace_dir = Path(self._temp_dir.name) / self.task.task_id
        shutil.copytree(self.task.path, self._workspace_dir)
        self._buggy_path = self._workspace_dir / "buggy.py"

        self._current_code = self._buggy_path.read_text(encoding="utf-8")
        self._current_result = self.runner.run(self._workspace_dir)
        self._step = 0
        self._done = self._current_result.all_passed
        self._truncated = False
        self._last_action = None
        if self.trajectory_dir is not None:
            self._trajectory_logger = TrajectoryLogger(
                output_dir=self.trajectory_dir,
                agent_name=self.agent_name,
                task_id=self.task.task_id,
            )

        observation = self._build_observation()
        info = self._build_info(result=self._current_result, action_id=None, changed=False)
        return observation.to_dict(), info

    def step(
        self,
        action: str | PatchAction,
    ) -> tuple[dict[str, object], float, bool, bool, dict[str, object]]:
        self._require_active_episode()
        action_obj = self._resolve_action(action)

        previous_result = self._current_result
        if previous_result is None:
            raise RuntimeError("PatchEnv.reset() must be called before step().")

        code_before = self._current_code
        code_after = action_obj.apply(code_before)
        changed = code_after != code_before

        self._buggy_file().write_text(code_after, encoding="utf-8")
        current_result = self.runner.run(self._workspace())

        self._step += 1
        self._current_code = code_after
        self._current_result = current_result
        self._last_action = action_obj.id
        self._done = current_result.all_passed
        self._truncated = self._step >= self.task.max_steps and not self._done

        reward = calculate_reward(previous_result, current_result)
        observation = self._build_observation()
        info = self._build_info(
            result=current_result,
            action_id=action_obj.id,
            changed=changed,
            code_hash_before=hash_code(code_before),
            code_hash_after=hash_code(code_after),
        )
        self._log_step(info=info, reward=reward, done=self._done, truncated=self._truncated)
        return observation.to_dict(), reward, self._done, self._truncated, info

    def close(self) -> None:
        if self._trajectory_logger is not None:
            self._trajectory_logger.close()
        if self._temp_dir is not None:
            self._temp_dir.cleanup()
        self._trajectory_logger = None
        self._temp_dir = None
        self._workspace_dir = None
        self._buggy_path = None
        self._current_result = None
        self._current_code = ""
        self._step = 0
        self._done = False
        self._truncated = False
        self._last_action = None

    def _resolve_action(self, action: str | PatchAction) -> PatchAction:
        if isinstance(action, str):
            try:
                action_obj = get_action(action)
            except KeyError as exc:
                raise ValueError(f"Unknown action: {action}") from exc
        else:
            action_obj = ACTION_REGISTRY.get(action.id)
            if action_obj is None:
                raise ValueError(f"Unknown action: {action.id}")
            if action is not action_obj:
                raise ValueError(
                    f"Action object for {action.id!r} must come from the registry."
                )
        if action_obj.id not in self.action_space:
            raise ValueError(f"Action {action_obj.id!r} is not allowed for {self.task.task_id}.")
        return action_obj

    def _build_observation(self) -> Observation:
        result = self._current_result
        if result is None:
            raise RuntimeError("PatchEnv.reset() must be called before observation access.")

        return Observation(
            task_id=self.task.task_id,
            step=self._step,
            tests_passed=result.passed,
            tests_failed=result.failed,
            last_action=self._last_action,
            last_error_type=result.error_type,
            code_hash=hash_code(self._current_code),
        )

    def _build_info(
        self,
        result: TestResult,
        action_id: str | None,
        changed: bool,
        code_hash_before: str | None = None,
        code_hash_after: str | None = None,
    ) -> dict[str, object]:
        return {
            "task_id": self.task.task_id,
            "workspace_dir": str(self._workspace()) if self._workspace_dir else None,
            "action_id": action_id,
            "changed": changed,
            "result": result.to_dict(),
            "code_hash_before": code_hash_before,
            "code_hash_after": code_hash_after or hash_code(self._current_code),
            "trajectory_path": (
                str(self._trajectory_logger.path) if self._trajectory_logger else None
            ),
            "episode_id": (
                self._trajectory_logger.episode_id if self._trajectory_logger else None
            ),
        }

    def _log_step(
        self,
        info: dict[str, object],
        reward: float,
        done: bool,
        truncated: bool,
    ) -> None:
        if self._trajectory_logger is None:
            return

        result = info["result"]
        if not isinstance(result, dict):
            raise TypeError("info['result'] must be a result dictionary")

        self._trajectory_logger.write(
            {
                "episode_id": self._trajectory_logger.episode_id,
                "task_id": self.task.task_id,
                "agent": self.agent_name,
                "step": self._step,
                "action_id": info["action_id"],
                "reward": reward,
                "tests_passed": result["passed"],
                "tests_failed": result["failed"],
                "done": done,
                "truncated": truncated,
                "duration_ms": result["duration_ms"],
                "code_hash_before": info["code_hash_before"],
                "code_hash_after": info["code_hash_after"],
                "error_type": result["error_type"],
                "changed": info["changed"],
            }
        )

    def _require_active_episode(self) -> None:
        if self._workspace_dir is None or self._current_result is None:
            raise RuntimeError("PatchEnv.reset() must be called before step().")
        if self._done or self._truncated:
            raise RuntimeError("Episode has ended. Call PatchEnv.reset() to start a new one.")

    def _workspace(self) -> Path:
        if self._workspace_dir is None:
            raise RuntimeError("PatchEnv.reset() must be called before workspace access.")
        return self._workspace_dir

    def _buggy_file(self) -> Path:
        if self._buggy_path is None:
            raise RuntimeError("PatchEnv.reset() must be called before code access.")
        return self._buggy_path

    def __enter__(self) -> "PatchEnv":
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
