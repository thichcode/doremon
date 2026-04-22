#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from production.app.config_loader import ConfigLoader
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

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
