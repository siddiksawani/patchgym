"""Actions that insert simple guard clauses into the first function."""

from __future__ import annotations

import ast
from dataclasses import dataclass

from patchgym.actions.base import PatchAction


@dataclass(frozen=True)
class AddGuardAction(PatchAction):
    condition_template: str
    return_expression: str

    def apply(self, code: str) -> str:
        parameter_name = _first_function_parameter(code)
        if parameter_name is None:
            return code

        condition = self.condition_template.format(param=parameter_name)
        return _insert_guard(code, condition, self.return_expression)


class AddNoneGuardAction(AddGuardAction):
    def __init__(self) -> None:
        super().__init__(
            id="add_none_guard",
            name="Add None guard",
            description="Return an empty string when the first argument is None.",
            condition_template="{param} is None",
            return_expression='""',
        )


class AddEmptyListGuardAction(AddGuardAction):
    def __init__(self) -> None:
        super().__init__(
            id="add_empty_list_guard",
            name="Add empty-list guard",
            description="Return 0 when the first argument is empty.",
            condition_template="not {param}",
            return_expression="0",
        )


def _first_function_parameter(code: str) -> str | None:
    try:
        module = ast.parse(code)
    except SyntaxError:
        return None

    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.args.args:
            return node.args.args[0].arg
    return None


def _insert_guard(code: str, condition: str, return_expression: str) -> str:
    try:
        module = ast.parse(code)
    except SyntaxError:
        return code

    function = next((node for node in module.body if isinstance(node, ast.FunctionDef)), None)
    if function is None:
        return code

    guard_line = f"if {condition}:"
    if any(line.strip() == guard_line for line in code.splitlines()):
        return code

    lines = code.splitlines()
    insert_at = function.lineno
    indent = _function_body_indent(lines, insert_at)
    guard_lines = [
        f"{indent}{guard_line}",
        f"{indent}    return {return_expression}",
    ]

    updated_lines = lines[:insert_at] + guard_lines + lines[insert_at:]
    trailing_newline = "\n" if code.endswith("\n") else ""
    return "\n".join(updated_lines) + trailing_newline


def _function_body_indent(lines: list[str], body_start_index: int) -> str:
    if body_start_index < len(lines):
        next_line = lines[body_start_index]
        stripped = next_line.lstrip()
        if stripped:
            return next_line[: len(next_line) - len(stripped)]
    def_line = lines[body_start_index - 1]
    return def_line[: len(def_line) - len(def_line.lstrip())] + "    "
