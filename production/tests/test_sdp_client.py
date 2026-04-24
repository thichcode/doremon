from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from production.app.sdp_client import SDPClient


class FakeTransport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def __call__(self, url: str, method: str, headers, body, timeout):
        self.calls.append((method, url))
        if method == "GET":
            return 200, "{}"
        return 200, "{\"ok\":true}"


class SDPClientTests(unittest.TestCase):
    def test_apply_dry_run(self) -> None:
        cfg = {
            "timeout_seconds": 10,
            "resources": {
                "priority_rules": {"path": "/p", "method": "PUT"},
                "assignment_rules": {"path": "/a", "method": "PUT"},
            },
        }
        client = SDPClient("https://example", "token", cfg, transport=FakeTransport())
        result = client.apply_with_rollback({"priority_rules": [], "assignment_rules": []}, Path("/tmp"), dry_run=True)
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Dry run: no API call executed")

    def test_apply_with_backup_and_apply(self) -> None:
        cfg = {
            "timeout_seconds": 10,
            "resources": {
                "priority_rules": {"path": "/p", "method": "PUT"},
                "assignment_rules": {"path": "/a", "method": "PUT"},
            },
        }
        transport = FakeTransport()
        client = SDPClient("https://example", "token", cfg, transport=transport)
        payload = {"priority_rules": [{"p": 1}], "assignment_rules": [{"a": 1}]}
        with tempfile.TemporaryDirectory() as tmp:
            result = client.apply_with_rollback(payload, Path(tmp), dry_run=False)
            self.assertTrue(result.success)
            self.assertIsNotNone(result.backup_path)
            self.assertTrue(result.backup_path.exists())
            self.assertEqual(result.applied_resources, ["priority_rules", "assignment_rules"])


if __name__ == "__main__":
    unittest.main()
