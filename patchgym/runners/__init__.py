"""Runner utilities for task verification."""

__all__ = ["PytestRunner", "TestResult"]


def __getattr__(name: str):
    if name in __all__:
        from patchgym.runners.test_runner import PytestRunner, TestResult

        return {"PytestRunner": PytestRunner, "TestResult": TestResult}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
