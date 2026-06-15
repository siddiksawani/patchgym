from patchgym.reporting import build_leaderboard, load_benchmark_csv, write_benchmark_csv


def test_build_leaderboard_summarizes_agent_rows() -> None:
    rows = [
        {
            "agent": "RandomAgent",
            "solved": False,
            "steps": 5,
            "total_reward": -1.0,
            "syntax_errors": 1,
            "timeouts": 0,
        },
        {
            "agent": "HeuristicAgent",
            "solved": True,
            "steps": 1,
            "total_reward": 11.9,
            "syntax_errors": 0,
            "timeouts": 0,
        },
        {
            "agent": "HeuristicAgent",
            "solved": True,
            "steps": 2,
            "total_reward": 9.8,
            "syntax_errors": 0,
            "timeouts": 1,
        },
    ]

    leaderboard = build_leaderboard(rows)

    assert leaderboard == [
        {
            "agent": "HeuristicAgent",
            "runs": 2,
            "solved_runs": 2,
            "solve_rate": 1.0,
            "avg_steps": 1.5,
            "avg_reward": 10.85,
            "syntax_errors": 0,
            "timeouts": 1,
        },
        {
            "agent": "RandomAgent",
            "runs": 1,
            "solved_runs": 0,
            "solve_rate": 0.0,
            "avg_steps": 5.0,
            "avg_reward": -1.0,
            "syntax_errors": 1,
            "timeouts": 0,
        },
    ]


def test_benchmark_csv_round_trips(tmp_path) -> None:
    rows = [
        {
            "agent": "HeuristicAgent",
            "task_id": "task_001",
            "episode": 0,
            "solved": True,
            "truncated": False,
            "steps": 1,
            "total_reward": 11.9,
            "tests_passed": 3,
            "tests_failed": 0,
            "syntax_errors": 0,
            "timeouts": 0,
            "trajectory_path": "trajectory.jsonl",
        }
    ]
    path = write_benchmark_csv(rows, tmp_path / "benchmark.csv")

    loaded = load_benchmark_csv(path)

    assert loaded[0]["agent"] == "HeuristicAgent"
    assert loaded[0]["solved"] == "True"
    assert loaded[0]["total_reward"] == "11.9"
