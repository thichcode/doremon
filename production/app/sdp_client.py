from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from urllib import request
from urllib.error import HTTPError, URLError


class SDPClientError(RuntimeError):
    pass


TransportFn = Callable[[str, str, dict[str, str], bytes | None, int], tuple[int, str]]


def default_transport(url: str, method: str, headers: dict[str, str], body: bytes | None, timeout: int) -> tuple[int, str]:
    req = request.Request(url=url, method=method, headers=headers, data=body)
    try:
        with request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            payload = resp.read().decode("utf-8")
            return resp.getcode(), payload
    except HTTPError as e:
        detail = e.read().decode("utf-8") if e.fp else str(e)
        raise SDPClientError(f"HTTPError {e.code}: {detail}") from e
    except URLError as e:
        raise SDPClientError(f"URLError: {e}") from e


@dataclass
class ApplyResult:
    success: bool
    backup_path: Path | None
    applied_resources: list[str]
    rolled_back: bool
    message: str


class SDPClient:
    def __init__(
        self,
        base_url: str,
        authtoken: str,
        integration_cfg: dict[str, Any],
        transport: TransportFn | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.authtoken = authtoken
        self.integration_cfg = integration_cfg
        self.timeout = int(integration_cfg.get("timeout_seconds", 30))
        self.transport = transport or default_transport

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "authtoken": self.authtoken,
        }

    def _resource_cfg(self, name: str) -> dict[str, Any]:
        resources = self.integration_cfg.get("resources", {})
        if name not in resources:
            raise SDPClientError(f"Resource not configured in sdp-integration.json: {name}")
        return resources[name]

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def get_resource(self, name: str) -> dict[str, Any]:
        cfg = self._resource_cfg(name)
        url = self._url(cfg["path"])
        status, payload = self.transport(url, "GET", self._headers(), None, self.timeout)
        if status >= 400:
            raise SDPClientError(f"GET {name} failed with status {status}")
        return json.loads(payload) if payload else {}

    def set_resource(self, name: str, data: Any) -> None:
        cfg = self._resource_cfg(name)
        method = cfg.get("method", "PUT")
        url = self._url(cfg["path"])
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        status, payload = self.transport(url, method, self._headers(), body, self.timeout)
        if status >= 400:
            raise SDPClientError(f"{method} {name} failed with status {status}: {payload}")

    def create_backup(self, payload: dict[str, Any], out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        snapshot: dict[str, Any] = {
            "created_at": datetime.utcnow().isoformat() + "Z",
            "state": {},
            "target_payload": payload,
        }
        for key in payload.keys():
            snapshot["state"][key] = self.get_resource(key)

        backup_path = out_dir / f"sdp-backup-{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json"
        backup_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
        return backup_path

    def rollback(self, backup_path: Path) -> None:
        backup = json.loads(backup_path.read_text(encoding="utf-8"))
        state = backup.get("state", {})
        for key, value in state.items():
            self.set_resource(key, value)

    def apply_with_rollback(self, payload: dict[str, Any], backup_dir: Path, dry_run: bool = False) -> ApplyResult:
        if dry_run:
            return ApplyResult(True, None, [], False, "Dry run: no API call executed")

        backup_path = self.create_backup(payload, backup_dir)
        applied: list[str] = []

        try:
            for key, value in payload.items():
                if key in {"version", "module"}:
                    continue
                self.set_resource(key, value)
                applied.append(key)
            return ApplyResult(True, backup_path, applied, False, "Apply completed successfully")
        except Exception as exc:  # rollback path
            self.rollback(backup_path)
            return ApplyResult(False, backup_path, applied, True, f"Apply failed, rollback executed: {exc}")
