"""Registry of predefined safe patch actions."""

from __future__ import annotations

from patchgym.actions.base import PatchAction
from patchgym.actions.guard_actions import AddEmptyListGuardAction, AddNoneGuardAction
from patchgym.actions.text_actions import RegexReplaceAction

_SINGLE_LT = r"(?<![<>=!])<(?![=<])"
_SINGLE_GT = r"(?<![<>=!-])>(?![=>])"
_EQUAL_EQUAL = r"(?<![=!])==(?!=)"
_NOT_EQUAL = r"(?<![=!])!=(?!=)"
_IDENTIFIER_OPERAND = (
    r"(?<![A-Za-z0-9_])"
    r"(?!(?:False|None|True|and|as|assert|async|await|break|class|continue|"
    r"def|del|elif|else|except|finally|for|from|global|if|import|in|is|"
    r"lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b)"
    r"[A-Za-z_][A-Za-z0-9_]*"
)
_BINARY_MINUS_ONE = (
    rf"(?P<prefix>(?:{_IDENTIFIER_OPERAND}|\d+|\]|\)))\s*-\s*1\b"
)


ACTION_REGISTRY: dict[str, PatchAction] = {
    action.id: action
    for action in [
        RegexReplaceAction(
            id="replace_less_than_with_less_equal",
            name="Replace < with <=",
            description="Replace the first standalone less-than operator with less-than-or-equal.",
            pattern=_SINGLE_LT,
            replacement="<=",
        ),
        RegexReplaceAction(
            id="replace_less_equal_with_less_than",
            name="Replace <= with <",
            description="Replace the first less-than-or-equal operator with less-than.",
            pattern=r"<=",
            replacement="<",
        ),
        RegexReplaceAction(
            id="replace_greater_than_with_greater_equal",
            name="Replace > with >=",
            description="Replace the first standalone greater-than operator with greater-than-or-equal.",
            pattern=_SINGLE_GT,
            replacement=">=",
        ),
        RegexReplaceAction(
            id="replace_greater_equal_with_greater_than",
            name="Replace >= with >",
            description="Replace the first greater-than-or-equal operator with greater-than.",
            pattern=r">=",
            replacement=">",
        ),
        RegexReplaceAction(
            id="replace_equal_equal_with_not_equal",
            name="Replace == with !=",
            description="Replace the first equality comparison with an inequality comparison.",
            pattern=_EQUAL_EQUAL,
            replacement="!=",
        ),
        RegexReplaceAction(
            id="replace_not_equal_with_equal_equal",
            name="Replace != with ==",
            description="Replace the first inequality comparison with an equality comparison.",
            pattern=_NOT_EQUAL,
            replacement="==",
        ),
        RegexReplaceAction(
            id="replace_minus_one_with_plus_one",
            name="Replace - 1 with + 1",
            description="Replace the first binary subtraction by one with plus one.",
            pattern=_BINARY_MINUS_ONE,
            replacement=r"\g<prefix> + 1",
        ),
        RegexReplaceAction(
            id="replace_range_len_minus_one_with_range_len",
            name="Replace range(len(x) - 1) with range(len(x))",
            description="Remove a minus-one boundary inside range(len(...)).",
            pattern=r"range\(len\((?P<target>[A-Za-z_][A-Za-z0-9_]*)\)\s*-\s*1\)",
            replacement=r"range(len(\g<target>))",
        ),
        AddNoneGuardAction(),
        AddEmptyListGuardAction(),
    ]
}


def get_action(action_id: str) -> PatchAction:
    try:
        return ACTION_REGISTRY[action_id]
    except KeyError as exc:
        raise KeyError(f"Unknown action: {action_id}") from exc


def list_actions() -> list[PatchAction]:
    return list(ACTION_REGISTRY.values())
