from pathlib import Path
from shutil import copyfile

from patchgym.actions import get_action, list_actions
from patchgym.runners import PytestRunner


def test_registry_contains_metadata_actions() -> None:
    action_ids = {action.id for action in list_actions()}

    assert "replace_range_len_minus_one_with_range_len" in action_ids
    assert "replace_greater_than_with_greater_equal" in action_ids
    assert "add_none_guard" in action_ids


def test_replace_greater_than_with_greater_equal_changes_only_single_operator() -> None:
    code = "def is_adult(age):\n    return age > 18 and age >= 0\n"

    patched = get_action("replace_greater_than_with_greater_equal").apply(code)

    assert patched == "def is_adult(age):\n    return age >= 18 and age >= 0\n"


def test_replace_greater_than_does_not_touch_return_type_arrow() -> None:
    code = "def is_positive(value) -> bool:\n    return value > 0\n"

    patched = get_action("replace_greater_than_with_greater_equal").apply(code)

    assert patched == "def is_positive(value) -> bool:\n    return value >= 0\n"


def test_replace_range_len_minus_one_with_range_len() -> None:
    code = "def count_items(items):\n    return len(list(range(len(items) - 1)))\n"

    patched = get_action("replace_range_len_minus_one_with_range_len").apply(code)

    assert patched == "def count_items(items):\n    return len(list(range(len(items))))\n"


def test_replace_minus_one_with_plus_one() -> None:
    code = "def shift(value):\n    return value - 1\n"

    patched = get_action("replace_minus_one_with_plus_one").apply(code)

    assert patched == "def shift(value):\n    return value + 1\n"


def test_replace_minus_one_does_not_touch_negative_literal_or_index() -> None:
    code = "def last(items):\n    offset = -1\n    return -1 if not items else items[-1]\n"

    patched = get_action("replace_minus_one_with_plus_one").apply(code)

    assert patched == code


def test_replace_minus_one_handles_binary_subtraction_without_spaces() -> None:
    code = "def shift(value):\n    return value-1\n"

    patched = get_action("replace_minus_one_with_plus_one").apply(code)

    assert patched == "def shift(value):\n    return value + 1\n"


def test_add_none_guard_uses_first_parameter() -> None:
    code = "def normalize_name(name):\n    return name.strip().title()\n"

    patched = get_action("add_none_guard").apply(code)

    assert patched == (
        "def normalize_name(name):\n"
        "    if name is None:\n"
        "        return \"\"\n"
        "    return name.strip().title()\n"
    )


def test_add_empty_list_guard_uses_first_parameter() -> None:
    code = "def first_item(items):\n    return items[0]\n"

    patched = get_action("add_empty_list_guard").apply(code)

    assert patched == (
        "def first_item(items):\n"
        "    if not items:\n"
        "        return 0\n"
        "    return items[0]\n"
    )


def test_guard_action_is_idempotent() -> None:
    code = (
        "def normalize_name(name):\n"
        "    if name is None:\n"
        "        return \"\"\n"
        "    return name.strip().title()\n"
    )

    patched = get_action("add_none_guard").apply(code)

    assert patched == code


def test_guard_action_uses_same_function_it_inspected() -> None:
    code = (
        "def version():\n"
        "    return '1.0'\n\n"
        "def normalize_name(name):\n"
        "    return name.strip().title()\n"
    )

    patched = get_action("add_none_guard").apply(code)

    assert patched == (
        "def version():\n"
        "    return '1.0'\n\n"
        "def normalize_name(name):\n"
        "    if name is None:\n"
        "        return \"\"\n"
        "    return name.strip().title()\n"
    )


def test_guard_action_preserves_function_docstring() -> None:
    code = (
        "def normalize_name(name):\n"
        "    \"\"\"Normalize a display name.\"\"\"\n"
        "    return name.strip().title()\n"
    )

    patched = get_action("add_none_guard").apply(code)

    assert patched == (
        "def normalize_name(name):\n"
        "    \"\"\"Normalize a display name.\"\"\"\n"
        "    if name is None:\n"
        "        return \"\"\n"
        "    return name.strip().title()\n"
    )


def test_actions_repair_starter_tasks(tmp_path: Path) -> None:
    repairs = {
        "task_001_off_by_one": "replace_range_len_minus_one_with_range_len",
        "task_002_none_guard": "add_none_guard",
        "task_003_wrong_operator": "replace_greater_than_with_greater_equal",
    }

    runner = PytestRunner()
    for task_name, action_id in repairs.items():
        source_task = Path("tasks") / task_name
        task_copy = tmp_path / task_name
        task_copy.mkdir()

        original_code = (source_task / "buggy.py").read_text(encoding="utf-8")
        patched_code = get_action(action_id).apply(original_code)
        (task_copy / "buggy.py").write_text(patched_code, encoding="utf-8")
        copyfile(source_task / "tests.py", task_copy / "tests.py")

        result = runner.run(task_copy)

        assert result.all_passed, f"{action_id} did not repair {task_name}"
