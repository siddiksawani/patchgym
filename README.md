# PatchGym

PatchGym is a small local playground for code-repair agents. The current build
has the project skeleton, three intentionally buggy Python tasks, a simple pytest
runner, and a safe action system for predefined text repairs.

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
