from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from production.app.config_loader import ConfigLoader
from production.app.payload_builder import build_sdp_payload
from production.app.validator import validate_all


class ProductionAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.loader = ConfigLoader()

    def test_validate_all_passes_with_default_config(self) -> None:
        errors = validate_all(
            self.loader.services(),
            self.loader.sla_and_escalation(),
            self.loader.sop_map(),
        )
        self.assertEqual(errors, [])

    def test_payload_builder_contains_expected_keys(self) -> None:
        payload = build_sdp_payload(
            self.loader.services(),
            self.loader.sla_and_escalation(),
            self.loader.sop_map(),
        )
        self.assertIn("priority_rules", payload)
        self.assertIn("assignment_rules", payload)
        self.assertIn("escalation_policy", payload)
        self.assertIn("service_sop", payload)

    def test_payload_can_be_written_as_json(self) -> None:
        payload = build_sdp_payload(
            self.loader.services(),
            self.loader.sla_and_escalation(),
            self.loader.sop_map(),
        )
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "payload.json"
            out.write_text(json.dumps(payload), encoding="utf-8")
            self.assertTrue(out.exists())


if __name__ == "__main__":
    unittest.main()
