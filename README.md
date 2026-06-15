# PatchGym

PatchGym is a small local playground for code-repair agents. The current build
has the project skeleton, three intentionally buggy Python tasks, a simple pytest
runner, a safe action system for predefined text repairs, and a minimal
Gym-style environment with baseline agents and JSONL trajectory logging.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Run Project Tests

```powershell
pytest
```

## Run One Buggy Task

```powershell
python -m patchgym.runners.test_runner tasks/task_001_off_by_one
```

The task runner executes that task's `tests.py` file with pytest and prints JSON
with pass/fail counts, duration, return code, and a simple error type.

## Use an Action

```python
from pathlib import Path

from patchgym.actions import get_action

code = Path("tasks/task_003_wrong_operator/buggy.py").read_text()
patched = get_action("replace_greater_than_with_greater_equal").apply(code)
```

Actions are intentionally limited to safe predefined transformations. Phase two
supports operator replacements, `- 1` replacements, and simple guard insertion
for `None` or empty inputs.

## Run the Environment

```python
from patchgym.agents import HeuristicAgent
from patchgym.env import PatchEnv

env = PatchEnv("tasks/task_003_wrong_operator", agent_name="HeuristicAgent")
obs, info = env.reset()
agent = HeuristicAgent(env.action_space, bug_type=env.task.bug_type)
obs, reward, done, truncated, info = env.step(agent.act(obs))
env.close()
```

`reset()` copies the task into a temporary workspace and runs the baseline tests.
`step()` applies one allowed action, reruns pytest, calculates reward, and returns
`(observation, reward, done, truncated, info)`.

Each `step()` writes one JSONL trajectory row by default under
`outputs/trajectories/`. Pass `trajectory_dir=None` to disable file logging for a
run.

## Run a Benchmark

```powershell
python -m patchgym.runners.benchmark_runner --agent heuristic --tasks tasks --episodes 1
```

The benchmark runner evaluates one agent across all task folders, saves per-run
CSV rows under `outputs/reports/`, writes a CSV leaderboard, and keeps each
episode trajectory under `outputs/trajectories/`.

## Current Tasks

- `task_001_off_by_one`: a list counter skips the last item.
- `task_002_none_guard`: a formatter crashes when the input is `None`.
- `task_003_wrong_operator`: an age check uses `>` instead of `>=`.

## Current Scope

- Package skeleton under `patchgym/`
- Task loader and metadata schema
- Subprocess-based pytest runner
- First three buggy tasks
- Safe action registry
- Operator replacement actions
- `- 1` replacement actions
- Simple `None` and empty-list guard actions
- `PatchEnv.reset()` and `PatchEnv.step()`
- Simple observation and reward helpers
- RandomAgent and HeuristicAgent baselines
- JSONL trajectory logging
- Benchmark runner
- CSV leaderboard
