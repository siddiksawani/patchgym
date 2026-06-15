import pytest

from patchgym.agents import HeuristicAgent, RandomAgent
from patchgym.env import PatchEnv


def test_random_agent_chooses_from_action_space() -> None:
    agent = RandomAgent(["a"], seed=7)

    assert agent.act({}) == "a"


def test_random_agent_rejects_empty_action_space() -> None:
    agent = RandomAgent([])

    with pytest.raises(ValueError, match="requires at least one action"):
        agent.act({})


def test_heuristic_agent_prefers_off_by_one_action() -> None:
    agent = HeuristicAgent(
        [
            "replace_less_than_with_less_equal",
            "replace_range_len_minus_one_with_range_len",
        ],
        bug_type="off_by_one",
    )

    assert agent.act({}) == "replace_range_len_minus_one_with_range_len"


def test_heuristic_agent_solves_starter_tasks() -> None:
    task_names = [
        "task_001_off_by_one",
        "task_002_none_guard",
        "task_003_wrong_operator",
    ]

    for task_name in task_names:
        with PatchEnv(f"tasks/{task_name}", trajectory_dir=None) as env:
            obs, _info = env.reset()
            agent = HeuristicAgent(env.action_space, bug_type=env.task.bug_type)
            obs, _reward, done, truncated, _info = env.step(agent.act(obs))

            assert done is True
            assert truncated is False
            assert obs["tests_failed"] == 0
