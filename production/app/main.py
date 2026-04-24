#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from production.app.config_loader import ConfigLoader
from production.app.core.mock_connector import InMemoryConnector
from production.app.core.models import EvidenceItem, SourceRecord
from production.app.core.policy_engine import PolicyEngine
from production.app.core.source_registry import SourceRegistry
from production.app.payload_builder import build_sdp_payload
from production.app.sdp_client import SDPClient
from production.app.validator import validate_all


def cmd_validate(loader: ConfigLoader) -> int:
    errors = validate_all(loader.services(), loader.sla_and_escalation(), loader.sop_map())
    if errors:
        print("CONFIG VALIDATION: FAILED")
        for e in errors:
            print(f"- {e}")
        return 1
    print("CONFIG VALIDATION: PASSED")
    return 0


def _build_full_payload(loader: ConfigLoader) -> dict:
    payload = build_sdp_payload(loader.services(), loader.sla_and_escalation(), loader.sop_map())
    payload["response_templates"] = loader.response_templates().get("templates", {})
    return payload


def _build_demo_registry() -> SourceRegistry:
    registry = SourceRegistry()
    registry.register(
        InMemoryConnector(
            name="tickets",
            records=[
                SourceRecord("t1", "ticket", "change request CHG-100", "rollback plan attached"),
                SourceRecord("t2", "ticket", "incident INC-20", "monitoring alert for jira"),
            ],
        )
    )
    registry.register(
        InMemoryConnector(
            name="docs",
            records=[
                SourceRecord("d1", "doc", "security policy", "policy for privileged changes"),
                SourceRecord("d2", "doc", "runbook", "validation evidence checklist"),
            ],
        )
    )
    return registry


def cmd_core_list_sources() -> int:
    registry = _build_demo_registry()
    print(json.dumps({"sources": registry.list_sources(), "health": registry.health_report()}, indent=2))
    return 0


def cmd_core_search(query: str, limit_per_source: int) -> int:
    registry = _build_demo_registry()
    results = registry.search_all(query=query, limit_per_source=limit_per_source)
    data = [
        {
            "source_id": r.source_id,
            "source_type": r.source_type,
            "title": r.title,
            "content": r.content,
            "metadata": r.metadata,
        }
        for r in results
    ]
    print(json.dumps({"query": query, "count": len(data), "results": data}, ensure_ascii=False, indent=2))
    return 0


def cmd_core_evaluate_evidence(loader: ConfigLoader, evidence_file: Path) -> int:
    raw = json.loads(evidence_file.read_text(encoding="utf-8"))
    evidence = [
        EvidenceItem(
            key=item["key"],
            required=bool(item.get("required", False)),
            value=item.get("value"),
            source_refs=item.get("source_refs", []),
        )
        for item in raw
    ]
    engine = PolicyEngine(loader.policy_rules())
    decision = engine.evaluate(evidence)
    print(
        json.dumps(
            {
                "ready": decision.ready,
                "score": decision.score,
                "missing_required": decision.missing_required,
                "warnings": decision.warnings,
                "approval_conditions": decision.approval_conditions,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if decision.ready else 2


def cmd_build_payload(loader: ConfigLoader, out: Path) -> int:
    errors = validate_all(loader.services(), loader.sla_and_escalation(), loader.sop_map())
    if errors:
        print("Cannot build payload because config validation failed:")
        for e in errors:
            print(f"- {e}")
        return 1

    payload = _build_full_payload(loader)
    payload = build_sdp_payload(loader.services(), loader.sla_and_escalation(), loader.sop_map())
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Payload written: {out}")
    return 0


def cmd_render_template(loader: ConfigLoader, template_key: str, values: list[str]) -> int:
    templates = loader.response_templates().get("templates", {})
    if template_key not in templates:
        print(f"Unknown template: {template_key}")
        return 1

    value_map: dict[str, str] = {}
    for pair in values:
        if "=" not in pair:
            print(f"Invalid --set pair: {pair}. Expected KEY=VALUE")
            return 1
        k, v = pair.split("=", 1)
        value_map[k] = v

    text = templates[template_key]
    for k, v in value_map.items():
        text = text.replace(f"[{k}]", v)

    print(text)
    return 0


def cmd_apply_sdp(loader: ConfigLoader, base_url: str | None, token: str | None, dry_run: bool, backup_dir: Path) -> int:
    errors = validate_all(loader.services(), loader.sla_and_escalation(), loader.sop_map())
    if errors:
        print("Cannot apply because config validation failed:")
        for e in errors:
            print(f"- {e}")
        return 1

    integ = loader.sdp_integration()
    env_base = integ.get("base_url_env", "SDP_BASE_URL")
    env_token = integ.get("token_env", "SDP_AUTHTOKEN")
    base_url = base_url or os.getenv(env_base)
    token = token or os.getenv(env_token)

    if not base_url:
        print(f"Missing base URL. Use --base-url or env {env_base}")
        return 1
    if not token and not dry_run:
        print(f"Missing token. Use --token or env {env_token}")
        return 1

    payload = _build_full_payload(loader)
    client = SDPClient(base_url=base_url, authtoken=token or "DRY_RUN", integration_cfg=integ)
    result = client.apply_with_rollback(payload=payload, backup_dir=backup_dir, dry_run=dry_run)
    print(result.message)
    if result.backup_path:
        print(f"Backup saved: {result.backup_path}")
    if result.applied_resources:
        print(f"Applied: {', '.join(result.applied_resources)}")
    if result.rolled_back:
        print("Rollback status: executed")
    return 0 if result.success else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Service Owner production app")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="validate config files")

    p_build = sub.add_parser("build-sdp-payload", help="build ServiceDeskPlus payload json")
    p_build.add_argument("--out", default="production/out/sdp-payload.json", help="output json path")

    p_render = sub.add_parser("render-response", help="render one response template")
    p_render.add_argument("--template", required=True, help="template key")
    p_render.add_argument("--set", action="append", default=[], help="replace values as KEY=VALUE")

    p_apply = sub.add_parser("apply-sdp-config", help="apply config to ServiceDeskPlus with rollback")
    p_apply.add_argument("--base-url", help="ServiceDeskPlus base URL")
    p_apply.add_argument("--token", help="ServiceDeskPlus authtoken")
    p_apply.add_argument("--backup-dir", default="production/out/backups", help="backup directory")
    p_apply.add_argument("--dry-run", action="store_true", help="skip API calls")

    sub.add_parser("core-list-sources", help="list registered sources and health report")

    p_search = sub.add_parser("core-search", help="search across registered sources")
    p_search.add_argument("--query", required=True)
    p_search.add_argument("--limit-per-source", type=int, default=10)

    p_eval = sub.add_parser("core-evaluate-evidence", help="evaluate evidence with policy engine")
    p_eval.add_argument("--input", required=True, help="path to evidence json list")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    loader = ConfigLoader()

    if args.command == "validate":
        return cmd_validate(loader)
    if args.command == "build-sdp-payload":
        return cmd_build_payload(loader, Path(args.out))
    if args.command == "render-response":
        return cmd_render_template(loader, args.template, args.set)
    if args.command == "apply-sdp-config":
        return cmd_apply_sdp(loader, args.base_url, args.token, args.dry_run, Path(args.backup_dir))
    if args.command == "core-list-sources":
        return cmd_core_list_sources()
    if args.command == "core-search":
        return cmd_core_search(args.query, args.limit_per_source)
    if args.command == "core-evaluate-evidence":
        return cmd_core_evaluate_evidence(loader, Path(args.input))

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
