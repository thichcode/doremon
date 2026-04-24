from __future__ import annotations

from typing import Any

from production.app.core.models import EvidenceItem, PolicyDecision


class PolicyEngine:
    """Evaluate evidence completeness/readiness using configurable thresholds."""

    def __init__(self, rules: dict[str, Any] | None = None) -> None:
        self.rules = rules or {
            "minimum_score": 80,
            "required_keys": ["change_request", "rollback_plan", "validation_evidence", "owner"],
            "warning_keys": ["monitoring_plan", "support_readiness", "risk_register"],
        }

    def evaluate(self, evidence: list[EvidenceItem]) -> PolicyDecision:
        by_key = {e.key: e for e in evidence}
        missing_required: list[str] = []
        warnings: list[str] = []

        for key in self.rules.get("required_keys", []):
            item = by_key.get(key)
            if not item or not item.is_present:
                missing_required.append(key)

        for key in self.rules.get("warning_keys", []):
            item = by_key.get(key)
            if not item or not item.is_present:
                warnings.append(key)

        score = 100
        score -= len(missing_required) * 20
        score -= len(warnings) * 5
        score = max(score, 0)

        ready = score >= int(self.rules.get("minimum_score", 80)) and not missing_required

        approval_conditions: list[str] = []
        if missing_required:
            approval_conditions.append(
                "Provide required evidence before approval: " + ", ".join(missing_required)
            )
        if warnings:
            approval_conditions.append(
                "Should provide additional evidence: " + ", ".join(warnings)
            )

        return PolicyDecision(
            ready=ready,
            score=score,
            missing_required=missing_required,
            warnings=warnings,
            approval_conditions=approval_conditions,
        )
