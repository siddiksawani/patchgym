import json

from patchgym.env import PatchEnv
from patchgym.trajectories import TrajectoryLogger


def test_trajectory_logger_writes_jsonl_record(tmp_path) -> None:
    logger = TrajectoryLogger(tmp_path, agent_name="Agent One", task_id="task/demo")
    logger.write({"step": 1, "reward": 10.0})
    logger.close()

    lines = logger.path.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 1
    assert json.loads(lines[0]) == {"reward": 10.0, "step": 1}


def test_trajectory_logger_sanitizes_custom_episode_id(tmp_path) -> None:
    logger = TrajectoryLogger(
        tmp_path,
        agent_name="Agent",
        task_id="task",
        episode_id="../outside",
    )
    logger.close()

    assert logger.episode_id == "_outside"
    assert logger.path.parent == tmp_path
    assert logger.path.name == "_outside.jsonl"
    assert logger.path.resolve().parent == tmp_path.resolve()


def test_patch_env_writes_step_trajectory(tmp_path) -> None:
    with PatchEnv(
        "tasks/task_003_wrong_operator",
        trajectory_dir=tmp_path,
        agent_name="HeuristicAgent",
    ) as env:
        env.reset()
        _obs, reward, done, truncated, info = env.step(
            "replace_greater_than_with_greater_equal"
        )
        trajectory_path = env.trajectory_path

    assert trajectory_path is not None
    assert trajectory_path == tmp_path / trajectory_path.name
    records = [
        json.loads(line)
        for line in trajectory_path.read_text(encoding="utf-8").splitlines()
    ]

    assert len(records) == 1
    assert records[0]["agent"] == "HeuristicAgent"
    assert records[0]["task_id"] == "task_003_wrong_operator"
    assert records[0]["action_id"] == "replace_greater_than_with_greater_equal"
    assert records[0]["reward"] == reward
    assert records[0]["tests_passed"] == 3
    assert records[0]["tests_failed"] == 0
    assert records[0]["done"] is done
    assert records[0]["truncated"] is truncated
    assert records[0]["code_hash_before"] == info["code_hash_before"]
    assert records[0]["code_hash_after"] == info["code_hash_after"]
    assert records[0]["episode_id"] == info["episode_id"]
