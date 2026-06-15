"""Registry of predefined safe patch actions."""

from __future__ import annotations

from patchgym.actions.base import PatchAction
from patchgym.actions.guard_actions import AddEmptyListGuardAction, AddNoneGuardAction
from patchgym.actions.text_actions import RegexReplaceAction

_SINGLE_LT = r"(?<![<>=!])<(?![=<])"
_SINGLE_GT = r"(?<![<>=!-])>(?![=>])"
_EQUAL_EQUAL = r"(?<![=!])==(?!=)"
_NOT_EQUAL = r"(?<![=!])!=(?!=)"
_STANDALONE_AND = r"\band\b"
_STANDALONE_OR = r"\bor\b"
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
_BINARY_PLUS_ONE = (
    rf"(?P<prefix>(?:{_IDENTIFIER_OPERAND}|\d+|\]|\)))\s*\+\s*1\b"
)
_IF_IN = (
    r"if\s+(?P<item>[A-Za-z_][A-Za-z0-9_]*)\s+in\s+"
    r"(?P<collection>[A-Za-z_][A-Za-z0-9_]*):"
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
            id="replace_plus_one_with_minus_one",
            name="Replace + 1 with - 1",
            description="Replace the first binary addition by one with minus one.",
            pattern=_BINARY_PLUS_ONE,
            replacement=r"\g<prefix> - 1",
        ),
        RegexReplaceAction(
            id="replace_range_len_minus_one_with_range_len",
            name="Replace range(len(x) - 1) with range(len(x))",
            description="Remove a minus-one boundary inside range(len(...)).",
            pattern=r"range\(len\((?P<target>[A-Za-z_][A-Za-z0-9_]*)\)\s*-\s*1\)",
            replacement=r"range(len(\g<target>))",
        ),
        RegexReplaceAction(
            id="replace_return_true_with_return_false",
            name="Replace return True with return False",
            description="Replace the first literal true return with false.",
            pattern=r"\breturn\s+True\b",
            replacement="return False",
        ),
        RegexReplaceAction(
            id="replace_return_false_with_return_true",
            name="Replace return False with return True",
            description="Replace the first literal false return with true.",
            pattern=r"\breturn\s+False\b",
            replacement="return True",
        ),
        RegexReplaceAction(
            id="replace_and_with_or",
            name="Replace and with or",
            description="Replace the first boolean and operator with or.",
            pattern=_STANDALONE_AND,
            replacement="or",
        ),
        RegexReplaceAction(
            id="replace_or_with_and",
            name="Replace or with and",
            description="Replace the first boolean or operator with and.",
            pattern=_STANDALONE_OR,
            replacement="and",
        ),
        RegexReplaceAction(
            id="replace_if_in_with_if_not_in",
            name="Replace if x in y with if x not in y",
            description="Replace the first membership condition with a negative membership check.",
            pattern=_IF_IN,
            replacement=r"if \g<item> not in \g<collection>:",
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
