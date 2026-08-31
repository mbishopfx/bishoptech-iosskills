#!/usr/bin/env python3
"""Validate a Meta Wearables implementation handoff packet."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PACKAGE_ROOT.parent / "meta-wearables-full-sdk-audit" / "references" / "surface-manifest.yaml"
DEFAULT_PLAN = PACKAGE_ROOT.parent / "meta-wearables-full-sdk-audit" / "references" / "capability-evidence-plan.yaml"
DEFAULT_TEAM = PACKAGE_ROOT.parent / "meta-wearables-agentic-team" / "references" / "team-manifest.yaml"
DEFAULT_PACKET = PACKAGE_ROOT / "references" / "implementation-handoff-template.yaml"

ALLOWED_ROUTES = {"native-dat-ios", "native-dat-android", "native-display", "web-app", "phone-fallback"}
ALLOWED_PLATFORMS = {"ios", "android", "web", "mixed"}
ALLOWED_STATUS = {"draft", "ready-for-implementation", "blocked", "complete"}
ALLOWED_LOCATIONS = {"glasses-native", "phone-local", "browser", "remote", "mixed", "unknown"}
SECRET_PATTERNS = (
    re.compile(r"(?i)(?:sk|rk|pk)_[A-Za-z0-9]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
)

REQUIRED_TOP_LEVEL = (
    "schema_version", "handoff_id", "status", "outcome", "selected_route",
    "fallback_surface", "target", "api_rows", "evidence_tasks", "owner_roles",
    "data_contract", "lifecycle", "tests", "open_gates", "next_proof_task",
)
REQUIRED_TARGET = (
    "project_root", "platform", "app_target", "os_min", "package_or_artifact",
    "revision", "runtime_identity", "phone_os", "companion_version", "firmware",
    "mode", "channel",
)
REQUIRED_DATA = (
    "processing_location", "inputs", "network", "storage_retention",
    "consent_trigger", "deletion", "raw_data_boundary",
)
REQUIRED_LIFECYCLE = (
    "state_owner", "session_epoch", "stop_order", "cancellation",
    "thermal_disconnect_doff",
)
REQUIRED_TESTS = ("reducer", "mock_or_browser", "build", "connected", "physical", "signed_release")


def strings(value: Any) -> list[str]:
    if isinstance(value, dict):
        return [item for child in value.values() for item in strings(child)]
    if isinstance(value, list):
        return [item for child in value for item in strings(child)]
    return [value] if isinstance(value, str) else []


def load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("packet root must be a mapping")
    return loaded


def ids_from(path: Path, *keys: str) -> set[str]:
    data = load_yaml(path)
    value: Any = data
    for key in keys:
        value = value.get(key, {}) if isinstance(value, dict) else {}
    if isinstance(value, list):
        return {item["id"] for item in value if isinstance(item, dict) and isinstance(item.get("id"), str)}
    return set()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", nargs="?", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--team-manifest", type=Path, default=DEFAULT_TEAM)
    parser.add_argument("--allow-placeholders", action="store_true")
    args = parser.parse_args()

    packet = args.packet.resolve()
    if not packet.is_file():
        raise SystemExit(f"missing implementation handoff: {packet}")

    errors: list[str] = []
    try:
        data = load_yaml(packet)
    except (OSError, ValueError, yaml.YAMLError) as error:
        raise SystemExit(f"invalid implementation handoff: {error}")

    missing = [key for key in REQUIRED_TOP_LEVEL if key not in data]
    if missing:
        errors.append(f"missing top-level fields: {missing}")
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if data.get("status") not in ALLOWED_STATUS:
        errors.append(f"status must be one of {sorted(ALLOWED_STATUS)}")
    if data.get("selected_route") not in ALLOWED_ROUTES:
        errors.append(f"selected_route must be one of {sorted(ALLOWED_ROUTES)}")
    if data.get("fallback_surface") not in ALLOWED_ROUTES:
        errors.append("fallback_surface must be a known route")
    if not isinstance(data.get("outcome"), str) or not data.get("outcome", "").strip():
        errors.append("outcome must be a non-empty string")
    if not isinstance(data.get("next_proof_task"), str) or not data.get("next_proof_task", "").strip():
        errors.append("next_proof_task must be a non-empty string")

    target = data.get("target", {})
    if not isinstance(target, dict):
        errors.append("target must be a mapping")
        target = {}
    else:
        missing_target = [key for key in REQUIRED_TARGET if key not in target]
        if missing_target:
            errors.append(f"missing target fields: {missing_target}")
        if target.get("platform") not in ALLOWED_PLATFORMS:
            errors.append(f"target.platform must be one of {sorted(ALLOWED_PLATFORMS)}")

    for section, required in (("data_contract", REQUIRED_DATA), ("lifecycle", REQUIRED_LIFECYCLE)):
        value = data.get(section, {})
        if not isinstance(value, dict):
            errors.append(f"{section} must be a mapping")
            continue
        missing_section = [key for key in required if key not in value]
        if missing_section:
            errors.append(f"missing {section} fields: {missing_section}")
    data_contract = data.get("data_contract", {})
    if isinstance(data_contract, dict) and data_contract.get("processing_location") not in ALLOWED_LOCATIONS:
        errors.append(f"data_contract.processing_location must be one of {sorted(ALLOWED_LOCATIONS)}")

    tests = data.get("tests", {})
    if not isinstance(tests, dict):
        errors.append("tests must be a mapping")
    else:
        missing_tests = [key for key in REQUIRED_TESTS if key not in tests]
        if missing_tests:
            errors.append(f"missing test groups: {missing_tests}")
        for key in REQUIRED_TESTS:
            if key in tests and not isinstance(tests[key], list):
                errors.append(f"tests.{key} must be a list")

    for key in ("api_rows", "evidence_tasks", "owner_roles", "open_gates"):
        if not isinstance(data.get(key), list) or not data[key]:
            errors.append(f"{key} must be a non-empty list")

    manifest_check = "not-run"
    if args.manifest.is_file():
        manifest_check = "pass"
        try:
            api_ids = ids_from(args.manifest.resolve(), "api_surface", "rows")
            unknown_api = sorted(set(data.get("api_rows", [])) - api_ids)
            if unknown_api:
                errors.append(f"api_rows not in surface manifest: {unknown_api}")
        except (OSError, ValueError, yaml.YAMLError) as error:
            manifest_check = "failed"
            errors.append(f"could not read surface manifest: {error}")

    plan_check = "not-run"
    if args.plan.is_file():
        plan_check = "pass"
        try:
            task_ids = ids_from(args.plan.resolve(), "task_catalog")
            unknown_tasks = sorted(set(data.get("evidence_tasks", [])) - task_ids)
            if unknown_tasks:
                errors.append(f"evidence_tasks not in capability plan: {unknown_tasks}")
        except (OSError, ValueError, yaml.YAMLError) as error:
            plan_check = "failed"
            errors.append(f"could not read capability plan: {error}")

    team_check = "not-run"
    if args.team_manifest.is_file():
        team_check = "pass"
        try:
            role_ids = ids_from(args.team_manifest.resolve(), "team_roles")
            unknown_roles = sorted(set(data.get("owner_roles", [])) - role_ids)
            if unknown_roles:
                errors.append(f"owner_roles not in team manifest: {unknown_roles}")
        except (OSError, ValueError, yaml.YAMLError) as error:
            team_check = "failed"
            errors.append(f"could not read team manifest: {error}")

    text = packet.read_text(encoding="utf-8")
    if any(pattern.search(text) for pattern in SECRET_PATTERNS):
        errors.append("secret-like literal found")
    if not args.allow_placeholders:
        placeholder_fields = [
            value for value in strings(data)
            if "<" in value or ">" in value or value == "to-verify"
        ]
        if placeholder_fields:
            errors.append("placeholder/to-verify values remain; use --allow-placeholders only for the template")

    if errors:
        print("INVALID implementation_handoff=" + str(packet))
        for error in errors:
            print("  " + error)
        return 1

    print(
        f"OK implementation_handoff={packet} route={data['selected_route']} "
        f"api_rows={len(data['api_rows'])} evidence_tasks={len(data['evidence_tasks'])} "
        f"owner_roles={len(data['owner_roles'])} manifest={manifest_check} plan={plan_check} team={team_check}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, TypeError, ValueError, yaml.YAMLError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        raise SystemExit(2)
