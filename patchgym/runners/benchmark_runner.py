"""Benchmark runner for PatchGym agents."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from patchgym.agents import BaseAgent, HeuristicAgent, RandomAgent
from patchgym.env import PatchEnv
from patchgym.reporting import build_leaderboard, write_benchmark_csv, write_leaderboard_csv

SUPPORTED_AGENTS = ("random", "heuristic")


def run_benchmark(
    agent_name: str,
    tasks_dir: str | Path = "tasks",
    episodes: int = 1,
    reports_dir: str | Path = Path("outputs") / "reports",
    trajectories_dir: str | Path | None = Path("outputs") / "trajectories",
    seed: int | None = None,
) -> dict[str, object]:
    if episodes < 1:
        raise ValueError("episodes must be at least 1")

    task_dirs = discover_task_dirs(tasks_dir)
    if not task_dirs:
        raise ValueError(f"No task directories found under {tasks_dir}")

    rows: list[dict[str, object]] = []
    for episode in range(episodes):
        for task_index, task_dir in enumerate(task_dirs):
            rows.append(
                run_episode(
                    task_dir=task_dir,
                    agent_name=agent_name,
                    episode=episode,
                    trajectories_dir=trajectories_dir,
                    seed=_episode_seed(seed, episode, task_index),
                )
            )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    reports_path = Path(reports_dir)
    benchmark_path = reports_path / f"benchmark_{agent_name}_{timestamp}.csv"
    leaderboard_path = reports_path / f"leaderboard_{agent_name}_{timestamp}.csv"
    write_benchmark_csv(rows, benchmark_path)
    leaderboard = build_leaderboard(rows)
    write_leaderboard_csv(leaderboard, leaderboard_path)

    return {
        "agent": agent_name,
        "rows": rows,
        "leaderboard": leaderboard,
        "benchmark_path": benchmark_path,
        "leaderboard_path": leaderboard_path,
    }


def run_episode(
    task_dir: str | Path,
    agent_name: str,
    episode: int,
    trajectories_dir: str | Path | None,
    seed: int | None = None,
) -> dict[str, object]:
    with PatchEnv(task_dir, trajectory_dir=trajectories_dir) as env:
        agent = create_agent(agent_name, env, seed=seed)
        env.agent_name = agent.name
        observation, info = env.reset()

        total_reward = 0.0
        syntax_errors = 0
        timeouts = 0
        result = info["result"]
        if not isinstance(result, dict):
            raise TypeError("info['result'] must be a result dictionary")
        done = bool(result["return_code"] == 0 and result["failed"] == 0)
        truncated = False

        while not done and not truncated:
            action_id = agent.act(observation)
            observation, reward, done, truncated, info = env.step(action_id)
            total_reward += reward

            result = info["result"]
            if not isinstance(result, dict):
                raise TypeError("info['result'] must be a result dictionary")
            syntax_errors += int(result["error_type"] == "syntax_error")
            timeouts += int(result["error_type"] == "timeout")

        result = info["result"]
        if not isinstance(result, dict):
            raise TypeError("info['result'] must be a result dictionary")

        return {
            "agent": agent.name,
            "task_id": env.task.task_id,
            "episode": episode,
            "solved": done,
            "truncated": truncated,
            "steps": observation["step"],
            "total_reward": round(total_reward, 3),
            "tests_passed": result["passed"],
            "tests_failed": result["failed"],
            "syntax_errors": syntax_errors,
            "timeouts": timeouts,
            "trajectory_path": info["trajectory_path"],
        }


def create_agent(agent_name: str, env: PatchEnv, seed: int | None = None) -> BaseAgent:
    normalized = agent_name.lower()
    if normalized == "random":
        return RandomAgent(env.action_space, seed=seed)
    if normalized == "heuristic":
        return HeuristicAgent(env.action_space, bug_type=env.task.bug_type)
    raise ValueError(f"Unsupported agent {agent_name!r}. Choose from: {', '.join(SUPPORTED_AGENTS)}")


def discover_task_dirs(tasks_dir: str | Path) -> list[Path]:
    root = Path(tasks_dir)
    return sorted(path for path in root.iterdir() if (path / "metadata.json").is_file())


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a PatchGym benchmark.")
    parser.add_argument("--agent", choices=SUPPORTED_AGENTS, default="heuristic")
    parser.add_argument("--tasks", default="tasks", help="Directory containing task folders")
    parser.add_argument("--episodes", type=int, default=1)
    parser.add_argument("--reports-dir", default=str(Path("outputs") / "reports"))
    parser.add_argument("--trajectories-dir", default=str(Path("outputs") / "trajectories"))
    parser.add_argument("--no-trajectories", action="store_true")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    result = run_benchmark(
        agent_name=args.agent,
        tasks_dir=args.tasks,
        episodes=args.episodes,
        reports_dir=args.reports_dir,
        trajectories_dir=None if args.no_trajectories else args.trajectories_dir,
        seed=args.seed,
    )
    leaderboard = result["leaderboard"]
    summary = leaderboard[0] if isinstance(leaderboard, list) and leaderboard else {}

    print(f"Agent: {result['agent']}")
    if summary:
        print(f"Solved: {summary['solved_runs']}/{summary['runs']}")
        print(f"Average reward: {summary['avg_reward']}")
        print(f"Average steps: {summary['avg_steps']}")
        print(f"Timeouts: {summary['timeouts']}")
        print(f"Syntax errors: {summary['syntax_errors']}")
    print(f"Results saved to {result['benchmark_path']}")
    print(f"Leaderboard saved to {result['leaderboard_path']}")
    if not args.no_trajectories:
        print(f"Trajectories saved to {args.trajectories_dir}")


def _episode_seed(seed: int | None, episode: int, task_index: int) -> int | None:
    return None if seed is None else seed + episode * 1009 + task_index


if __name__ == "__main__":
    main()
