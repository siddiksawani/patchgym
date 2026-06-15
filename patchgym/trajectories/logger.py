"""JSONL trajectory logger."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import TextIO


class TrajectoryLogger:
    def __init__(
        self,
        output_dir: str | Path,
        agent_name: str,
        task_id: str,
        episode_id: str | None = None,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        self.episode_id = episode_id or f"{_slug(agent_name)}_{_slug(task_id)}_{timestamp}"
        self.path = self.output_dir / f"{self.episode_id}.jsonl"
        self._file: TextIO = self.path.open("a", encoding="utf-8")

    def write(self, record: dict[str, object]) -> None:
        line = json.dumps(record, sort_keys=True)
        self._file.write(f"{line}\n")
        self._file.flush()

    def close(self) -> None:
        if not self._file.closed:
            self._file.close()

    def __enter__(self) -> "TrajectoryLogger":
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")
    return slug or "unknown"
