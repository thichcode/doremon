from __future__ import annotations

from typing import Any


def build_priority_rules(sla_cfg: dict[str, Any]) -> list[dict[str, Any]]:
    matrix = sla_cfg["priority_matrix"]
    return [
        {
            "priority": p,
            "first_response_minutes": matrix[p]["first_response_minutes"],
            "resolve_target_minutes": matrix[p]["resolve_target_minutes"],
        }
        for p in ["P1", "P2", "P3", "P4"]
    ]


def build_assignment_rules(services_cfg: dict[str, Any]) -> list[dict[str, Any]]:
    rules = []
    for svc in services_cfg["prioritized_services"]:
        rules.append(
            {
                "service_id": svc["id"],
                "queue": svc["queue"],
                "resolver_group_l1": svc["resolver_group_l1"],
                "resolver_group_l2": svc["resolver_group_l2"],
            }
        )
    return rules


def build_sdp_payload(
    services_cfg: dict[str, Any], sla_cfg: dict[str, Any], sop_cfg: dict[str, Any]
) -> dict[str, Any]:
    return {
        "version": 1,
        "module": "ServiceDeskPlus",
        "priority_rules": build_priority_rules(sla_cfg),
        "assignment_rules": build_assignment_rules(services_cfg),
        "escalation_policy": sla_cfg["escalation_policy"],
        "service_sop": sop_cfg["services"],
    }
