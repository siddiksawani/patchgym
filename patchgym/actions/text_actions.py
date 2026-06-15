"""Regex-backed text replacement actions."""

from __future__ import annotations

import re
from dataclasses import dataclass

from patchgym.actions.base import PatchAction


@dataclass(frozen=True)
class RegexReplaceAction(PatchAction):
    pattern: str
    replacement: str
    count: int = 1

    def apply(self, code: str) -> str:
        return re.sub(self.pattern, self.replacement, code, count=self.count)
