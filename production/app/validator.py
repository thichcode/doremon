from __future__ import annotations

from typing import Any


def require(cond: bool, message: str, errors: list[str]) -> None:
    if not cond:
        errors.append(message)


def validate_services(data: dict[str, Any], errors: list[str]) -> None:
    require("prioritized_services" in data, "services.json missing prioritized_services", errors)
    services = data.get("prioritized_services", [])
    require(len(services) == 5, "services.json must contain exactly 5 prioritized services", errors)
    required_fields = {"id", "name", "queue", "resolver_group_l1", "resolver_group_l2"}
    for idx, svc in enumerate(services):
        missing = required_fields - set(svc.keys())
        require(not missing, f"service index {idx} missing fields: {sorted(missing)}", errors)


def validate_sla(data: dict[str, Any], errors: list[str]) -> None:
    pm = data.get("priority_matrix", {})
    for p in ["P1", "P2", "P3", "P4"]:
        require(p in pm, f"sla-and-escalation.json missing {p}", errors)
        entry = pm.get(p, {})
        require("first_response_minutes" in entry, f"{p} missing first_response_minutes", errors)
        require("resolve_target_minutes" in entry, f"{p} missing resolve_target_minutes", errors)

    escalations = data.get("escalation_policy", {}).get("time_based", [])
    priorities = {e.get("priority") for e in escalations}
    for p in ["P1", "P2", "P3", "P4"]:
        require(p in priorities, f"escalation time_based missing priority {p}", errors)


def validate_sop_map(data: dict[str, Any], errors: list[str]) -> None:
    services = data.get("services", {})
    expected = {"jira_admin", "architecture_consulting", "sdp_admin", "zabbix_admin", "gitlab_admin"}
    require(expected.issubset(services.keys()), "service-sop-map.json missing one or more expected services", errors)


def validate_all(services: dict[str, Any], sla: dict[str, Any], sop: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    validate_services(services, errors)
    validate_sla(sla, errors)
    validate_sop_map(sop, errors)
    return errors
