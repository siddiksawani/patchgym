"""Tiny Q-learning training loop for PatchGym."""

from __future__ import annotations

from pathlib import Path

from patchgym.agents import QLearningAgent
from patchgym.env import PatchEnv
from patchgym.runners.benchmark_runner import discover_task_dirs


def train_task(task_dir: str | Path, episodes: int = 20) -> QLearningAgent:
    with PatchEnv(task_dir, trajectory_dir=None) as probe_env:
        agent = QLearningAgent(
            probe_env.action_space,
            bug_type=probe_env.task.bug_type,
            epsilon=0.2,
            seed=0,
        )

    solved = 0
    for episode in range(episodes):
        with PatchEnv(task_dir, trajectory_dir=None) as env:
            observation, _info = env.reset()
            done = False
            truncated = False

            while not done and not truncated:
                action = agent.act(observation)
                next_observation, reward, done, truncated, _info = env.step(action)
                agent.observe(
                    observation,
                    action,
                    reward,
                    next_observation,
                    done,
                    truncated,
                )
                observation = next_observation

            solved += int(done)

        print(f"{Path(task_dir).name}: episode={episode + 1} solved={solved}/{episode + 1}")

    return agent


def train(tasks_dir: str | Path = "tasks", episodes: int = 20) -> dict[str, QLearningAgent]:
    agents = {}

    for task_dir in discover_task_dirs(tasks_dir):
        agents[Path(task_dir).name] = train_task(task_dir, episodes=episodes)

    return agents


if __name__ == "__main__":
    train()
