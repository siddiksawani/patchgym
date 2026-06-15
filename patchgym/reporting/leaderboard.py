"""CSV leaderboard helpers for benchmark results."""

from __future__ import annotations

import csv
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

BENCHMARK_FIELDS = [
    "agent",
    "task_id",
    "episode",
    "solved",
    "truncated",
    "steps",
    "total_reward",
    "tests_passed",
    "tests_failed",
    "syntax_errors",
    "timeouts",
    "trajectory_path",
]

LEADERBOARD_FIELDS = [
    "agent",
    "runs",
    "solved_runs",
    "solve_rate",
    "avg_steps",
    "avg_reward",
    "syntax_errors",
    "timeouts",
]


def write_benchmark_csv(rows: list[dict[str, object]], output_path: str | Path) -> Path:
    return _write_csv(rows, output_path, BENCHMARK_FIELDS)


def write_leaderboard_csv(rows: list[dict[str, object]], output_path: str | Path) -> Path:
    return _write_csv(rows, output_path, LEADERBOARD_FIELDS)


def load_benchmark_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def build_leaderboard(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["agent"])].append(row)

    leaderboard = []
    for agent, agent_rows in sorted(grouped.items()):
        runs = len(agent_rows)
        solved_runs = sum(1 for row in agent_rows if _as_bool(row["solved"]))
        syntax_errors = sum(_as_int(row["syntax_errors"]) for row in agent_rows)
        timeouts = sum(_as_int(row["timeouts"]) for row in agent_rows)
        avg_steps = _average(_as_int(row["steps"]) for row in agent_rows)
        avg_reward = _average(_as_float(row["total_reward"]) for row in agent_rows)

        leaderboard.append(
            {
                "agent": agent,
                "runs": runs,
                "solved_runs": solved_runs,
                "solve_rate": round(solved_runs / runs, 3) if runs else 0.0,
                "avg_steps": round(avg_steps, 3),
                "avg_reward": round(avg_reward, 3),
                "syntax_errors": syntax_errors,
                "timeouts": timeouts,
            }
        )

    return sorted(leaderboard, key=lambda row: (-float(row["solve_rate"]), row["agent"]))


def _write_csv(rows: list[dict[str, object]], output_path: str | Path, fields: list[str]) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _as_int(value: object) -> int:
    return int(value)


def _as_float(value: object) -> float:
    return float(value)


def _average(values: Iterable[float]) -> float:
    numbers = list(values)
    return sum(numbers) / len(numbers) if numbers else 0.0
