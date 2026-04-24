from __future__ import annotations

from production.app.core.connector import Connector
from production.app.core.models import SourceRecord


class InMemoryConnector(Connector):
    def __init__(self, name: str, records: list[SourceRecord]) -> None:
        self._name = name
        self.records = records

    @property
    def name(self) -> str:
        return self._name

    def healthcheck(self) -> bool:
        return True

    def search(self, query: str, limit: int = 20):
        q = query.lower()
        hits = [r for r in self.records if q in r.title.lower() or q in r.content.lower()]
        return hits[:limit]
