from pathlib import Path

from patchgym.runners import PytestRunner


def test_runner_reports_failing_buggy_task() -> None:
    result = PytestRunner().run(Path("tasks") / "task_003_wrong_operator")

    assert result.passed == 2
    assert result.failed == 1
    assert result.error_type == "assertion_failure"


def test_runner_reports_runtime_error_type() -> None:
    result = PytestRunner().run(Path("tasks") / "task_002_none_guard")

    assert result.passed == 2
    assert result.failed == 1
    assert result.error_type == "runtime_error"


def test_runner_reports_passing_task(tmp_path: Path) -> None:
    (tmp_path / "buggy.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    (tmp_path / "tests.py").write_text(
        "from buggy import add\n\n"
        "def test_add():\n"
        "    assert add(1, 2) == 3\n",
        encoding="utf-8",
    )

    result = PytestRunner().run(tmp_path)

    assert result.all_passed
    assert result.passed == 1
    assert result.failed == 0
    assert result.error_type is None
