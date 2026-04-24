from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SourceRecord:
    source_id: str
    source_type: str
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceItem:
    key: str
    required: bool
    value: Any | None = None
    source_refs: list[str] = field(default_factory=list)

    @property
    def is_present(self) -> bool:
        if self.value is None:
            return False
        if isinstance(self.value, str):
            return bool(self.value.strip())
        return True


@dataclass
class PolicyDecision:
    ready: bool
    score: int
    missing_required: list[str]
    warnings: list[str]
    approval_conditions: list[str]
