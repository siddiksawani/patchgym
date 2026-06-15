import pytest

from patchgym.agents import HeuristicAgent, QLearningAgent, RandomAgent
from patchgym.env import PatchEnv
from patchgym.tasks.validator import validate_tasks


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


def test_q_learning_agent_updates_action_value() -> None:
    agent = QLearningAgent(["repair", "noop"], epsilon=0.0, seed=7)
    observation = {"tests_passed": 1, "last_error_type": "assertion_failure", "step": 0}
    next_observation = {"tests_passed": 2, "last_error_type": None, "step": 1}

    assert agent.act(observation) == "repair"

    agent.observe(
        observation,
        "repair",
        10.0,
        next_observation,
        done=True,
        truncated=False,
    )

    state = "bug=|passed=1|error=assertion_failure|step=0"
    assert agent.q_table[state]["repair"] > 0


def test_heuristic_agent_solves_all_tasks() -> None:
    task_names = [result.task_id for result in validate_tasks("tasks")]

    for task_name in task_names:
        with PatchEnv(f"tasks/{task_name}", trajectory_dir=None) as env:
            obs, _info = env.reset()
            agent = HeuristicAgent(env.action_space, bug_type=env.task.bug_type)
            done = False
            truncated = False
            while not done and not truncated:
                obs, _reward, done, truncated, _info = env.step(agent.act(obs))

            assert done is True
            assert truncated is False
            assert obs["tests_failed"] == 0
