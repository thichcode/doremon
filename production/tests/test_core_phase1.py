from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from production.app.core.mock_connector import InMemoryConnector
from production.app.core.models import EvidenceItem, SourceRecord
from production.app.core.policy_engine import PolicyEngine
from production.app.core.source_registry import SourceRegistry
from production.app.main import main


class CorePhase1Tests(unittest.TestCase):
    def test_source_registry_search(self) -> None:
        registry = SourceRegistry()
        registry.register(
            InMemoryConnector(
                "docs",
                [SourceRecord("1", "doc", "Security Policy", "change approval")],
            )
        )
        results = registry.search_all("security")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].source_id, "1")

    def test_policy_engine_missing_required(self) -> None:
        engine = PolicyEngine(
            {
                "minimum_score": 80,
                "required_keys": ["change_request", "rollback_plan"],
                "warning_keys": ["monitoring_plan"],
            }
        )
        evidence = [
            EvidenceItem(key="change_request", required=True, value="CHG-1"),
            EvidenceItem(key="monitoring_plan", required=False, value=None),
        ]
        decision = engine.evaluate(evidence)
        self.assertFalse(decision.ready)
        self.assertIn("rollback_plan", decision.missing_required)

    def test_cli_core_evaluate_evidence(self) -> None:
        sample = [
            {"key": "change_request", "required": True, "value": "CHG-100"},
            {"key": "rollback_plan", "required": True, "value": "attached"},
            {"key": "validation_evidence", "required": True, "value": "tests passed"},
            {"key": "owner", "required": True, "value": "owner-a"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.json"
            path.write_text(json.dumps(sample), encoding="utf-8")
            code = main(["core-evaluate-evidence", "--input", str(path)])
            self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
