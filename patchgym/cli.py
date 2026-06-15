"""Command-line interface for PatchGym."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchgym.env import PatchEnv
from patchgym.reporting import build_leaderboard, load_benchmark_csv, write_leaderboard_csv
from patchgym.runners.benchmark_runner import SUPPORTED_AGENTS, create_agent, run_benchmark
from patchgym.tasks import validate_tasks


def main() -> None:
    parser = argparse.ArgumentParser(prog="patchgym", description="PatchGym command line")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate-tasks", help="Validate task folders")
    validate_parser.add_argument("--tasks", default="tasks")
    validate_parser.set_defaults(func=_validate_tasks)

    run_parser = subparsers.add_parser("run-task", help="Run one task with one agent")
    run_parser.add_argument("--task", required=True)
    run_parser.add_argument("--agent", choices=SUPPORTED_AGENTS, default="heuristic")
    run_parser.add_argument("--seed", type=int, default=None)
    run_parser.add_argument("--no-trajectories", action="store_true")
    run_parser.set_defaults(func=_run_task)

    benchmark_parser = subparsers.add_parser("benchmark", help="Benchmark an agent")
    benchmark_parser.add_argument("--agent", choices=SUPPORTED_AGENTS, default="heuristic")
    benchmark_parser.add_argument("--tasks", default="tasks")
    benchmark_parser.add_argument("--episodes", type=int, default=1)
    benchmark_parser.add_argument("--reports-dir", default=str(Path("outputs") / "reports"))
    benchmark_parser.add_argument(
        "--trajectories-dir",
        default=str(Path("outputs") / "trajectories"),
    )
    benchmark_parser.add_argument("--no-trajectories", action="store_true")
    benchmark_parser.add_argument("--seed", type=int, default=None)
    benchmark_parser.set_defaults(func=_benchmark)

    leaderboard_parser = subparsers.add_parser("leaderboard", help="Build a leaderboard CSV")
    leaderboard_parser.add_argument("--report", required=True)
    leaderboard_parser.add_argument("--output", default=None)
    leaderboard_parser.set_defaults(func=_leaderboard)

    show_parser = subparsers.add_parser("show-trajectory", help="Print a trajectory JSONL file")
    show_parser.add_argument("--file", required=True)
    show_parser.set_defaults(func=_show_trajectory)

    args = parser.parse_args()
    args.func(args)


def _validate_tasks(args: argparse.Namespace) -> None:
    results = validate_tasks(args.tasks)
    invalid = [result for result in results if not result.valid]
    for result in results:
        status = "ok" if result.valid else "error"
        print(f"{status}: {result.task_id}")
        for error in result.errors:
            print(f"  - {error}")
    if invalid:
        raise SystemExit(1)


def _run_task(args: argparse.Namespace) -> None:
    trajectories_dir = None if args.no_trajectories else Path("outputs") / "trajectories"
    with PatchEnv(args.task, trajectory_dir=trajectories_dir) as env:
        agent = create_agent(args.agent, env, seed=args.seed)
        env.agent_name = agent.name
        observation, _info = env.reset()

        total_reward = 0.0
        done = False
        truncated = False
        info: dict[str, object] = {}
        while not done and not truncated:
            previous_observation = observation
            action_id = agent.act(observation)
            observation, reward, done, truncated, info = env.step(action_id)
            agent.observe(previous_observation, action_id, reward, observation, done, truncated)
            total_reward += reward

        print(
            json.dumps(
                {
                    "task_id": env.task.task_id,
                    "agent": agent.name,
                    "done": done,
                    "truncated": truncated,
                    "steps": observation["step"],
                    "total_reward": round(total_reward, 3),
                    "trajectory_path": info.get("trajectory_path"),
                },
                indent=2,
            )
        )
        raise SystemExit(0 if done else 1)


def _benchmark(args: argparse.Namespace) -> None:
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


def _leaderboard(args: argparse.Namespace) -> None:
    rows = load_benchmark_csv(args.report)
    leaderboard = build_leaderboard(rows)
    output = args.output or str(Path(args.report).with_name("leaderboard.csv"))
    path = write_leaderboard_csv(leaderboard, output)
    print(f"Leaderboard saved to {path}")


def _show_trajectory(args: argparse.Namespace) -> None:
    print(Path(args.file).read_text(encoding="utf-8"), end="")


if __name__ == "__main__":
    main()
