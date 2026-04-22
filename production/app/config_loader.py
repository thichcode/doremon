from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigLoader:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[1]
        self.config_dir = self.root / "config"
        self.template_dir = self.root / "templates"

    def load_json(self, rel_path: str) -> dict[str, Any]:
        path = self.root / rel_path
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def services(self) -> dict[str, Any]:
        return self.load_json("config/services.json")

    def sla_and_escalation(self) -> dict[str, Any]:
        return self.load_json("config/sla-and-escalation.json")

    def sop_map(self) -> dict[str, Any]:
        return self.load_json("config/service-sop-map.json")

    def response_templates(self) -> dict[str, Any]:
        return self.load_json("templates/response-templates.json")
