"""Tiny Q-learning training loop for PatchGym."""

from __future__ import annotations

from pathlib import Path

from patchgym.agents import QLearningAgent
from patchgym.env import PatchEnv
from patchgym.runners.benchmark_runner import discover_task_dirs


def train(tasks_dir: str | Path = "tasks", episodes: int = 3) -> QLearningAgent:
    task_dirs = discover_task_dirs(tasks_dir)
    action_space = sorted(
        {
            action_id
            for task_dir in task_dirs
            for action_id in PatchEnv(task_dir, trajectory_dir=None).action_space
        }
    )
    agent = QLearningAgent(action_space, epsilon=0.2, seed=0)

    for episode in range(episodes):
        solved = 0
        for task_dir in task_dirs:
            with PatchEnv(task_dir, trajectory_dir=None) as env:
                observation, _info = env.reset()
                done = False
                truncated = False
                while not done and not truncated:
                    action = agent.act(observation)
                    next_observation, reward, done, truncated, _info = env.step(action)
                    agent.observe(observation, action, reward, next_observation, done, truncated)
                    observation = next_observation
                solved += int(done)
        print(f"episode={episode + 1} solved={solved}/{len(task_dirs)}")

    return agent


if __name__ == "__main__":
    train()
