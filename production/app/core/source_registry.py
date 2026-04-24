from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from production.app.core.connector import Connector
from production.app.core.models import SourceRecord


@dataclass
class SourceRegistry:
    connectors: dict[str, Connector] = field(default_factory=dict)

    def register(self, connector: Connector) -> None:
        self.connectors[connector.name] = connector

    def unregister(self, name: str) -> None:
        self.connectors.pop(name, None)

    def list_sources(self) -> list[str]:
        return sorted(self.connectors.keys())

    def health_report(self) -> dict[str, bool]:
        return {name: c.healthcheck() for name, c in self.connectors.items()}

    def search_all(self, query: str, limit_per_source: int = 10) -> list[SourceRecord]:
        results: list[SourceRecord] = []
        for name, connector in self.connectors.items():
            try:
                items: Iterable[SourceRecord] = connector.search(query=query, limit=limit_per_source)
                results.extend(items)
            except Exception as exc:
                results.append(
                    SourceRecord(
                        source_id=f"{name}:error",
                        source_type=name,
                        title="connector_error",
                        content=str(exc),
                        metadata={"error": True},
                    )
                )
        return results
