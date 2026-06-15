import csv
import subprocess
import sys

from patchgym.runners.benchmark_runner import discover_task_dirs, run_benchmark


def test_discover_task_dirs_finds_starter_tasks() -> None:
    task_ids = [path.name for path in discover_task_dirs("tasks")]

    expected = {"task_001_off_by_one", "task_002_none_guard", "task_003_wrong_operator"}
    assert expected.issubset(task_ids)
    assert task_ids == sorted(task_ids)


def test_run_benchmark_writes_csv_reports(tmp_path) -> None:
    result = run_benchmark(
        agent_name="heuristic",
        tasks_dir="tasks",
        episodes=1,
        reports_dir=tmp_path / "reports",
        trajectories_dir=tmp_path / "trajectories",
    )

    benchmark_path = result["benchmark_path"]
    leaderboard_path = result["leaderboard_path"]
    assert benchmark_path.is_file()
    assert leaderboard_path.is_file()

    with benchmark_path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 3
    assert {row["task_id"] for row in rows} == {
        "task_001_off_by_one",
        "task_002_none_guard",
        "task_003_wrong_operator",
    }
    assert all(row["agent"] == "HeuristicAgent" for row in rows)
    assert all(row["solved"] == "True" for row in rows)
    assert all(row["trajectory_path"] for row in rows)

    with leaderboard_path.open(newline="", encoding="utf-8") as file:
        leaderboard_rows = list(csv.DictReader(file))

    assert leaderboard_rows == [
        {
            "agent": "HeuristicAgent",
            "runs": "3",
            "solved_runs": "3",
            "solve_rate": "1.0",
            "avg_steps": "1.0",
            "avg_reward": "12.567",
            "syntax_errors": "0",
            "timeouts": "0",
        }
    ]


def test_benchmark_runner_module_cli_writes_reports(tmp_path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchgym.runners.benchmark_runner",
            "--agent",
            "heuristic",
            "--tasks",
            "tasks",
            "--episodes",
            "1",
            "--reports-dir",
            str(tmp_path / "reports"),
            "--trajectories-dir",
            str(tmp_path / "trajectories"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Solved: 3/3" in completed.stdout
    assert len(list((tmp_path / "reports").glob("benchmark_heuristic_*.csv"))) == 1
    assert len(list((tmp_path / "reports").glob("leaderboard_heuristic_*.csv"))) == 1
