"""Small pytest runner for PatchGym tasks."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

_COUNT_RE = re.compile(r"(?P<count>\d+)\s+(?P<label>passed|failed|error|errors)")


@dataclass(frozen=True)
class TestResult:
    passed: int
    failed: int
    total: int
    return_code: int
    stdout: str
    stderr: str
    duration_ms: int
    error_type: str | None

    @property
    def all_passed(self) -> bool:
        return self.total > 0 and self.failed == 0 and self.return_code == 0

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class PytestRunner:
    def __init__(self, timeout_seconds: float = 15.0) -> None:
        self.timeout_seconds = timeout_seconds

    def run(self, task_dir: str | Path) -> TestResult:
        task_path = Path(task_dir).resolve()
        tests_path = task_path / "tests.py"
        if not tests_path.is_file():
            raise FileNotFoundError(f"Task tests not found: {tests_path}")

        started = time.perf_counter()
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "pytest", tests_path.name, "-q"],
                cwd=task_path,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            duration_ms = int((time.perf_counter() - started) * 1000)
            return TestResult(
                passed=0,
                failed=0,
                total=0,
                return_code=124,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                duration_ms=duration_ms,
                error_type="timeout",
            )

        duration_ms = int((time.perf_counter() - started) * 1000)
        passed, failed = _parse_counts(completed.stdout)
        error_type = _classify_error(completed.stdout, completed.stderr, completed.returncode)

        return TestResult(
            passed=passed,
            failed=failed,
            total=passed + failed,
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            duration_ms=duration_ms,
            error_type=error_type,
        )


def _parse_counts(output: str) -> tuple[int, int]:
    passed = 0
    failed = 0
    for match in _COUNT_RE.finditer(output):
        count = int(match.group("count"))
        label = match.group("label")
        if label == "passed":
            passed += count
        else:
            failed += count
    return passed, failed


def _classify_error(stdout: str, stderr: str, return_code: int) -> str | None:
    if return_code == 0:
        return None

    combined = f"{stdout}\n{stderr}"
    if "SyntaxError" in combined:
        return "syntax_error"
    if "ImportError" in combined or "ModuleNotFoundError" in combined:
        return "import_error"
    if any(name in combined for name in ("AttributeError", "TypeError", "IndexError")):
        return "runtime_error"
    if "AssertionError" in combined or "assert " in combined:
        return "assertion_failure"
    return "runtime_error"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run pytest for one PatchGym task.")
    parser.add_argument("task_dir", help="Path to a task directory containing tests.py")
    parser.add_argument("--timeout", type=float, default=15.0, help="Timeout in seconds")
    args = parser.parse_args()

    result = PytestRunner(timeout_seconds=args.timeout).run(args.task_dir)
    print(json.dumps(result.to_dict(), indent=2))
    raise SystemExit(result.return_code)


if __name__ == "__main__":
    main()
