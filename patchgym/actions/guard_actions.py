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
        function = _first_function_with_parameter(code)
        if function is None:
            return code

        parameter_name = function.args.args[0].arg
        condition = self.condition_template.format(param=parameter_name)
        return _insert_guard(code, function, condition, self.return_expression)


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


def _first_function_with_parameter(code: str) -> ast.FunctionDef | None:
    try:
        module = ast.parse(code)
    except SyntaxError:
        return None

    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.args.args:
            return node
    return None


def _insert_guard(
    code: str,
    function: ast.FunctionDef,
    condition: str,
    return_expression: str,
) -> str:
    guard_line = f"if {condition}:"
    if any(line.strip() == guard_line for line in code.splitlines()):
        return code

    lines = code.splitlines()
    insert_at = _guard_insert_index(function)
    indent = _function_body_indent(lines, function)
    guard_lines = [
        f"{indent}{guard_line}",
        f"{indent}    return {return_expression}",
    ]

    updated_lines = lines[:insert_at] + guard_lines + lines[insert_at:]
    trailing_newline = "\n" if code.endswith("\n") else ""
    return "\n".join(updated_lines) + trailing_newline


def _guard_insert_index(function: ast.FunctionDef) -> int:
    if (
        function.body
        and isinstance(function.body[0], ast.Expr)
        and isinstance(function.body[0].value, ast.Constant)
        and isinstance(function.body[0].value.value, str)
    ):
        return function.body[0].end_lineno or function.body[0].lineno
    return function.lineno


def _function_body_indent(lines: list[str], function: ast.FunctionDef) -> str:
    if function.body:
        body_start_index = function.body[0].lineno - 1
        next_line = lines[body_start_index]
        stripped = next_line.lstrip()
        if stripped:
            return next_line[: len(next_line) - len(stripped)]
    def_line = lines[function.lineno - 1]
    return def_line[: len(def_line) - len(def_line.lstrip())] + "    "
