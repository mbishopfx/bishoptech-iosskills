#!/usr/bin/env python3
"""Validate the Meta Wearables local team and upstream-role manifest."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


EXPECTED_MANIFEST_ID = "meta-wearables-agent-team-2026-08-22"
EXPECTED_MANIFEST_REVISION = 4
EXPECTED_SOURCE_MANIFEST_ID = "meta-wearables-public-surface-2026-08-22"
EXPECTED_SOURCE_MANIFEST_REVISION = 6
EXPECTED_LOCAL_ROLES = {
    "meta-dat-android-api-atlas",
    "meta-dat-android-integration",
    "meta-dat-api-atlas",
    "meta-dat-camera-audio",
    "meta-dat-display",
    "meta-dat-ios-integration",
    "meta-wearables-agentic-team",
    "meta-wearables-app-architecture",
    "meta-wearables-debugging-observability",
    "meta-wearables-developer-operations",
    "meta-wearables-device-compatibility",
    "meta-wearables-device-proof",
    "meta-wearables-full-sdk-audit",
    "meta-wearables-implementation-recipes",
    "meta-wearables-input-sensors",
    "meta-wearables-on-device-compliance",
    "meta-wearables-operational-readiness",
    "meta-wearables-privacy-publishing",
    "meta-wearables-route-planner",
    "meta-wearables-security-attestation",
    "meta-wearables-source-refresh",
    "meta-wearables-transport-reliability",
    "meta-wearables-web-apps",
}
EXPECTED_UPSTREAM_ROLES = {
    "native-dat-ios": [
        "camera-streaming", "dat-conventions", "debugging", "display-access",
        "getting-started", "live-debugging-mcp", "mockdevice-testing",
        "permissions-registration", "sample-app-guide", "session-lifecycle",
    ],
    "native-dat-android": [
        "camera-streaming", "dat-conventions", "debugging", "display-access",
        "getting-started", "live-debugging-mcp", "mockdevice-testing",
        "permissions-registration", "sample-app-guide", "session-lifecycle",
    ],
    "web-apps": [
        "add-device-sensors", "add-gestures", "add-local-storage", "add-offline",
        "add-text-input", "add-ui", "connect-api", "create-webapp",
        "passcode-for-testing", "publish-to-vercel", "qr-code", "test-on-device",
    ],
}
EXPECTED_SURFACES = set(EXPECTED_UPSTREAM_ROLES) | {"phone-fallback"}
ALLOWED_EVIDENCE = {
    "source", "access-gated", "static", "fixture", "mock", "build",
    "browser-sim", "connected", "physical", "signed", "release-channel", "production",
}
SECRET_PATTERN = re.compile(
    r"(?:sk|pk)_(?:live|test)_[A-Za-z0-9]+|Bearer\s+[A-Za-z0-9._-]{20,}|"
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    default_path = Path(__file__).resolve().parent.parent / "references" / "team-manifest.yaml"
    parser.add_argument("manifest", nargs="?", type=Path, default=default_path)
    parser.add_argument("--surface-manifest", type=Path, help="optional source-pinned manifest for cross-checking exact role lists")
    parser.add_argument("--workspace-root", type=Path, help="optional workspace root for checking all local role directories")
    return parser.parse_args()


def fail(message: str) -> None:
    raise ValueError(message)


def load_yaml(path: Path) -> dict:
    if not path.is_file():
        fail(f"manifest not found: {path.resolve()}")
    raw = path.read_text(encoding="utf-8")
    if SECRET_PATTERN.search(raw):
        fail(f"manifest contains a credential-like token: {path}")
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        fail(f"manifest root must be a mapping: {path}")
    return data


def main() -> int:
    args = parse_args()
    manifest_path = args.manifest.resolve()
    data = load_yaml(manifest_path)
    if data.get("schema_version") != 1:
        fail("schema_version must be 1")
    if data.get("manifest_id") != EXPECTED_MANIFEST_ID:
        fail(f"unexpected manifest_id: {data.get('manifest_id')!r}")
    if data.get("manifest_revision") != EXPECTED_MANIFEST_REVISION:
        fail(f"manifest_revision must be {EXPECTED_MANIFEST_REVISION}")
    if data.get("source_manifest_id") != EXPECTED_SOURCE_MANIFEST_ID:
        fail("source_manifest_id does not match the source-pinned surface manifest")
    if data.get("source_manifest_revision") != EXPECTED_SOURCE_MANIFEST_REVISION:
        fail(f"source_manifest_revision must be {EXPECTED_SOURCE_MANIFEST_REVISION}")

    expected_agent_contract = {
        "source_manifest_field": "agent_surface_contract",
        "source_only": True,
        "docs_mcp_endpoint": "https://mcp.developer.meta.com/wearables",
        "docs_mcp_authentication": "none-per-official-repository-readmes",
        "docs_mcp_tools": ["search_dat_docs", "search_webapps_docs"],
        "local_callable_in_this_workspace": False,
        "expected_surface_ids": ["native-dat-ios", "native-dat-android", "web-apps"],
        "route_rule": "Use official local Codex plugin installs for native DAT; use the Web Apps marketplace route; use MCP for live docs lookup only when the client exposes it, otherwise use the pinned repository/full-reference fallback.",
    }
    if data.get("agent_surface_contract") != expected_agent_contract:
        fail("agent_surface_contract drifted")

    expected_ai_surfaces = {
        "root_files": ["AGENTS.md", "README.md", "install-skills.sh"],
        "plugin_manifests": {
            "native-dat-ios": "plugins/mwdat-ios/.codex-plugin/plugin.json",
            "native-dat-android": "plugins/mwdat-android/.codex-plugin/plugin.json",
            "web-apps": "plugins/meta-wearables-webapp/.codex-plugin/plugin.json",
        },
        "docs_mcp_endpoint": "https://mcp.developer.meta.com/wearables",
    }
    if data.get("source_ai_surfaces") != expected_ai_surfaces:
        fail("source_ai_surfaces drifted")

    surfaces = data.get("surfaces", [])
    surface_ids = {entry.get("id") for entry in surfaces if isinstance(entry, dict)}
    if surface_ids != EXPECTED_SURFACES:
        fail(f"surface IDs drifted: expected {sorted(EXPECTED_SURFACES)}, got {sorted(surface_ids)}")
    if any(not entry.get("upstream_repository") or not entry.get("local_primary_roles") for entry in surfaces):
        fail("every surface needs an upstream repository and local_primary_roles")

    roles = data.get("team_roles", [])
    role_ids = [entry.get("id") for entry in roles if isinstance(entry, dict)]
    if set(role_ids) != EXPECTED_LOCAL_ROLES or len(role_ids) != len(set(role_ids)):
        fail("team_roles must contain each expected local role exactly once")
    categories = {entry.get("category") for entry in roles}
    if not categories or any(not entry.get("primary_output") or not entry.get("hard_gate") for entry in roles):
        fail("every team role needs category, primary_output, and hard_gate")
    for role in roles:
        unknown_surfaces = set(role.get("surfaces", [])) - EXPECTED_SURFACES
        if unknown_surfaces:
            fail(f"{role['id']} has unknown surfaces: {sorted(unknown_surfaces)}")

    handoffs = data.get("upstream_role_handoffs", [])
    if len(handoffs) != sum(len(value) for value in EXPECTED_UPSTREAM_ROLES.values()):
        fail("upstream_role_handoffs count drifted")
    seen = set()
    for handoff in handoffs:
        required = {"surface", "role", "upstream_path", "primary_local_role", "local_handoff"}
        missing = required - set(handoff)
        if missing:
            fail(f"upstream handoff missing keys: {sorted(missing)}")
        key = (handoff["surface"], handoff["role"])
        if key in seen:
            fail(f"duplicate upstream handoff: {key}")
        seen.add(key)
        if handoff["surface"] not in EXPECTED_UPSTREAM_ROLES or handoff["role"] not in EXPECTED_UPSTREAM_ROLES[handoff["surface"]]:
            fail(f"unexpected upstream role handoff: {key}")
        if handoff["primary_local_role"] not in EXPECTED_LOCAL_ROLES:
            fail(f"unknown primary local role: {handoff['primary_local_role']}")
        if not set(handoff["local_handoff"]).issubset(EXPECTED_LOCAL_ROLES):
            fail(f"unknown local handoff role for {key}")
    for surface, expected_roles in EXPECTED_UPSTREAM_ROLES.items():
        observed = sorted(role for current_surface, role in seen if current_surface == surface)
        if observed != sorted(expected_roles):
            fail(f"{surface} upstream role set drifted")

    gates = data.get("device_claim_gates", [])
    expected_gate_ids = {"ray-ban-display", "gen-2", "gen-3"}
    if {gate.get("id") for gate in gates} != expected_gate_ids:
        fail("device_claim_gates must cover Ray-Ban Display, Gen 2, and Gen 3")
    for gate in gates:
        if gate.get("minimum_evidence") not in ALLOWED_EVIDENCE:
            fail(f"invalid minimum evidence for {gate.get('id')}")
        if not gate.get("required_tasks") or not gate.get("prohibited_shortcuts"):
            fail(f"device gate incomplete: {gate.get('id')}")

    contract = data.get("handoff_contract", {})
    if not contract.get("required_fields") or not contract.get("evidence_order") or not contract.get("non_claims"):
        fail("handoff_contract is incomplete")
    if set(contract["evidence_order"]) != ALLOWED_EVIDENCE:
        fail("handoff_contract evidence_order drifted")
    if not set(contract.get("required_separation", [])).issuperset({"native-dat-ios", "native-dat-android", "web-apps", "phone-fallback", "glasses-native", "phone-local", "remote", "mixed", "unknown"}):
        fail("handoff_contract must preserve surface and processing-location separation")

    if args.surface_manifest:
        surface_manifest = load_yaml(args.surface_manifest.resolve())
        if surface_manifest.get("manifest_id") != EXPECTED_SOURCE_MANIFEST_ID:
            fail("selected source manifest ID does not match the team manifest")
        if surface_manifest.get("manifest_revision") != EXPECTED_SOURCE_MANIFEST_REVISION:
            fail("selected source manifest revision does not match the team manifest")
        inventory = surface_manifest.get("source_inventory", {})
        source_ai_surfaces = inventory.get("ai_surfaces")
        if source_ai_surfaces != {
            "root_files": ["AGENTS.md", "README.md", "install-skills.sh"],
            "plugin_manifests": {
                "ios": "plugins/mwdat-ios/.codex-plugin/plugin.json",
                "android": "plugins/mwdat-android/.codex-plugin/plugin.json",
                "web_apps": "plugins/meta-wearables-webapp/.codex-plugin/plugin.json",
            },
            "docs_mcp_endpoint": "https://mcp.developer.meta.com/wearables",
        }:
            fail("selected source manifest AI surfaces drifted")
        source_agent_contract = surface_manifest.get("agent_surface_contract", {})
        if source_agent_contract.get("docs_mcp", {}).get("endpoint") != "https://mcp.developer.meta.com/wearables":
            fail("selected source manifest agent surface contract drifted")
        if set(entry.get("id") for entry in source_agent_contract.get("surfaces", []) if isinstance(entry, dict)) != {"native-dat-ios", "native-dat-android", "web-apps"}:
            fail("selected source manifest agent surface IDs drifted")
        for key, surface in (("ios", "native-dat-ios"), ("android", "native-dat-android"), ("web_apps", "web-apps")):
            observed = sorted(inventory.get(key, {}).get("plugin_roles", []))
            if observed != sorted(EXPECTED_UPSTREAM_ROLES[surface]):
                fail(f"source manifest role set drifted for {surface}")

    if args.workspace_root:
        workspace_root = args.workspace_root.resolve()
        missing = sorted(role for role in EXPECTED_LOCAL_ROLES if not (workspace_root / "knowledge-base/skills/packages" / role / "SKILL.md").is_file())
        if missing:
            fail(f"missing local role package SKILL.md files: {missing}")

    print(f"OK team_manifest={manifest_path}")
    print(f"  manifest_id={data['manifest_id']} manifest_revision={data['manifest_revision']}")
    print(f"  surfaces={len(surfaces)} local_roles={len(roles)} upstream_handoffs={len(handoffs)}")
    print(f"  device_claim_gates={len(gates)} evidence_levels={len(contract['evidence_order'])} agent_surfaces=3")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, TypeError, ValueError, yaml.YAMLError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        raise SystemExit(2)
