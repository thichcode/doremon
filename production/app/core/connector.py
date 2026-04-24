from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from production.app.core.models import SourceRecord


class Connector(ABC):
    """Contract for all source connectors (ticketing, docs, chat, email, etc.)."""

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def healthcheck(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str, limit: int = 20) -> Iterable[SourceRecord]:
        raise NotImplementedError
