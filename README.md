# PatchGym

PatchGym is a small local playground for code-repair agents. Phase one sets up the
project skeleton, three intentionally buggy Python tasks, and a simple pytest
runner that reports structured results.

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

## Current Tasks

- `task_001_off_by_one`: a list counter skips the last item.
- `task_002_none_guard`: a formatter crashes when the input is `None`.
- `task_003_wrong_operator`: an age check uses `>` instead of `>=`.

## Phase One Scope

- Package skeleton under `patchgym/`
- Task loader and metadata schema
- Subprocess-based pytest runner
- First three buggy tasks
- Basic README
