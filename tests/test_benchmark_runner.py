import csv
import subprocess
import sys
from shutil import copytree

from patchgym.runners.benchmark_runner import discover_task_dirs, run_benchmark


def test_discover_task_dirs_finds_starter_tasks() -> None:
    task_ids = [path.name for path in discover_task_dirs("tasks")]

    assert task_ids == [
        "task_001_off_by_one",
        "task_002_none_guard",
        "task_003_wrong_operator",
        "task_004_empty_list_guard",
        "task_005_less_equal_boundary",
        "task_006_not_equal_operator",
        "task_007_greater_equal_boundary",
        "task_008_less_than_discount",
        "task_009_none_title_guard",
        "task_010_sum_off_by_one",
        "task_011_binary_search_boundary",
        "task_012_normalize_slug_none",
        "task_013_dedupe_preserve_order",
        "task_014_valid_name_logic",
        "task_015_public_default",
    ]


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

    assert len(rows) == 15
    assert all(row["agent"] == "HeuristicAgent" for row in rows)
    assert all(row["solved"] == "True" for row in rows)
    assert all(row["trajectory_path"] for row in rows)

    with leaderboard_path.open(newline="", encoding="utf-8") as file:
        leaderboard_rows = list(csv.DictReader(file))

    assert leaderboard_rows == [
        {
            "agent": "HeuristicAgent",
            "runs": "15",
            "solved_runs": "15",
            "solve_rate": "1.0",
            "avg_steps": "1.0",
            "avg_reward": leaderboard_rows[0]["avg_reward"],
            "syntax_errors": "0",
            "timeouts": "0",
        }
    ]


def test_benchmark_runner_module_cli_writes_reports(tmp_path) -> None:
    tasks_root = tmp_path / "tasks"
    copytree("tasks/task_003_wrong_operator", tasks_root / "task_003_wrong_operator")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchgym.runners.benchmark_runner",
            "--agent",
            "heuristic",
            "--tasks",
            str(tasks_root),
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
    assert "Solved: 1/1" in completed.stdout
    assert len(list((tmp_path / "reports").glob("benchmark_heuristic_*.csv"))) == 1
    assert len(list((tmp_path / "reports").glob("leaderboard_heuristic_*.csv"))) == 1
