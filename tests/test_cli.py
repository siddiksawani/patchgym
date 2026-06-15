import subprocess
import sys


def test_cli_validate_tasks() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchgym.cli", "validate-tasks", "--tasks", "tasks"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "ok: task_001_off_by_one" in completed.stdout
    assert "ok: task_015_public_default" in completed.stdout


def test_cli_run_task() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchgym.cli",
            "run-task",
            "--task",
            "tasks/task_003_wrong_operator",
            "--agent",
            "heuristic",
            "--no-trajectories",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert '"done": true' in completed.stdout


def test_cli_accepts_qlearning_agent() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchgym.cli",
            "run-task",
            "--task",
            "tasks/task_015_public_default",
            "--agent",
            "qlearning",
            "--seed",
            "0",
            "--no-trajectories",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert '"agent": "QLearningAgent"' in completed.stdout
