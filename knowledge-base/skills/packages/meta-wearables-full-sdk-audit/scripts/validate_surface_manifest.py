#!/usr/bin/env python3
"""Validate the bundled Meta Wearables source/API surface manifest."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


EXPECTED_MANIFEST_ID = "meta-wearables-public-surface-2026-08-22"
EXPECTED_MANIFEST_REVISION = 6
EXPECTED_API_REVISION = "meta-wearables-api-surface-2026-08-22"
EXPECTED_FULL_REFERENCE_TERMS = [
    "# DAT SDK v0.9",
    "Ray-Ban Meta (Gen 1 and Gen 2)",
    "Ray-Ban Meta Optics",
    "Meta Ray-Ban Display glasses",
    "MWDATCore",
]
EXPECTED_PREFLIGHT_TASK_IDS = (
    "PRE-SOURCE-01",
    "PRE-IOS-01",
    "PRE-ANDROID-01",
    "PRE-WEB-01",
    "PRE-IDENTITY-01",
    "PRE-DATA-01",
    "PRE-TUPLE-01",
    "PRE-BUILD-01",
    "PRE-ARCHIVE-01",
)
EXPECTED_PLUGIN_ROLES = {
    "ios": [
        "camera-streaming",
        "dat-conventions",
        "debugging",
        "display-access",
        "getting-started",
        "live-debugging-mcp",
        "mockdevice-testing",
        "permissions-registration",
        "sample-app-guide",
        "session-lifecycle",
    ],
    "android": [
        "camera-streaming",
        "dat-conventions",
        "debugging",
        "display-access",
        "getting-started",
        "live-debugging-mcp",
        "mockdevice-testing",
        "permissions-registration",
        "sample-app-guide",
        "session-lifecycle",
    ],
    "web_apps": [
        "add-device-sensors",
        "add-gestures",
        "add-local-storage",
        "add-offline",
        "add-text-input",
        "add-ui",
        "connect-api",
        "create-webapp",
        "passcode-for-testing",
        "publish-to-vercel",
        "qr-code",
        "test-on-device",
    ],
}
EXPECTED_COUNTS = {
    "journeys": 4,
    "ios_modules": 6,
    "android_artifacts": 4,
    "capabilities": 14,
    "source_conflicts": 6,
    "generation_labels": 6,
    "evidence_levels": 10,
    "refresh_triggers": 7,
    "api_rows": 30,
    "terminology_terms": 5,
}
ROW_KEYS = {
    "journey",
    "platform",
    "lane",
    "symbols",
    "status",
    "source_refs",
    "evidence_level",
    "compile_or_runtime_gate",
    "privacy_path",
    "fallback",
}
SECRET_PATTERN = re.compile(
    r"(?:sk|pk)_(?:live|test)_[A-Za-z0-9]+|Bearer\s+[A-Za-z0-9._-]{20,}|"
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    default_path = Path(__file__).resolve().parent.parent / "references" / "surface-manifest.yaml"
    parser.add_argument("manifest", nargs="?", type=Path, default=default_path)
    return parser.parse_args()


def fail(message: str) -> None:
    raise ValueError(message)


def main() -> int:
    args = parse_args()
    manifest_path = args.manifest.resolve()
    if not manifest_path.is_file():
        fail(f"manifest not found: {manifest_path}")

    raw = manifest_path.read_text(encoding="utf-8")
    if SECRET_PATTERN.search(raw):
        fail("manifest contains a credential-like token or private key marker")

    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        fail("manifest root must be a mapping")
    if data.get("schema_version") != 1:
        fail(f"schema_version must be 1, got {data.get('schema_version')!r}")
    if data.get("manifest_id") != EXPECTED_MANIFEST_ID:
        fail(f"unexpected manifest_id: {data.get('manifest_id')!r}")
    if data.get("manifest_revision") != EXPECTED_MANIFEST_REVISION:
        fail(f"manifest_revision must be {EXPECTED_MANIFEST_REVISION}, got {data.get('manifest_revision')!r}")

    snapshot = data.get("snapshot", {})
    if snapshot.get("full_reference_url") != "https://wearables.developer.meta.com/llms.txt?full=true&product=dat":
        fail("snapshot.full_reference_url drifted")
    if snapshot.get("full_reference_anchor_terms") != EXPECTED_FULL_REFERENCE_TERMS:
        fail("snapshot.full_reference_anchor_terms drifted")

    for key in ("snapshot", "authority_order", "journeys", "native_modules", "source_inventory", "agent_surface_contract", "terminology_contract", "api_surface", "preflight_contract", "capabilities", "source_conflicts", "generation_labels", "evidence_ladder", "refresh_triggers"):
        if key not in data:
            fail(f"missing top-level key: {key}")

    preflight_contract = data["preflight_contract"]
    if not isinstance(preflight_contract, dict):
        fail("preflight_contract must be a mapping")
    if not preflight_contract.get("reference") or not preflight_contract.get("authority_note"):
        fail("preflight_contract needs reference and authority_note")
    preflight_ids = tuple(preflight_contract.get("task_ids", []))
    if preflight_ids != EXPECTED_PREFLIGHT_TASK_IDS:
        fail(
            "preflight task IDs drift: expected "
            f"{list(EXPECTED_PREFLIGHT_TASK_IDS)}, got {list(preflight_ids)}"
        )

    source_inventory = data["source_inventory"]
    if not isinstance(source_inventory, dict) or not source_inventory.get("authority_note"):
        fail("source_inventory needs an authority_note")
    ai_surfaces = source_inventory.get("ai_surfaces")
    if not isinstance(ai_surfaces, dict):
        fail("source_inventory needs ai_surfaces")
    if ai_surfaces.get("root_files") != ["AGENTS.md", "README.md", "install-skills.sh"]:
        fail("source_inventory.ai_surfaces.root_files drifted")
    if ai_surfaces.get("plugin_manifests") != {
        "ios": "plugins/mwdat-ios/.codex-plugin/plugin.json",
        "android": "plugins/mwdat-android/.codex-plugin/plugin.json",
        "web_apps": "plugins/meta-wearables-webapp/.codex-plugin/plugin.json",
    }:
        fail("source_inventory.ai_surfaces.plugin_manifests drifted")
    if ai_surfaces.get("docs_mcp_endpoint") != "https://mcp.developer.meta.com/wearables":
        fail("source_inventory.ai_surfaces.docs_mcp_endpoint drifted")
    agent_contract = data["agent_surface_contract"]
    if not isinstance(agent_contract, dict) or not agent_contract.get("authority_note"):
        fail("agent_surface_contract needs an authority_note")
    docs_mcp = agent_contract.get("docs_mcp")
    if not isinstance(docs_mcp, dict):
        fail("agent_surface_contract needs docs_mcp")
    if docs_mcp.get("endpoint") != "https://mcp.developer.meta.com/wearables":
        fail("agent_surface_contract.docs_mcp.endpoint drifted")
    if docs_mcp.get("authentication") != "none-per-official-repository-readmes":
        fail("agent_surface_contract.docs_mcp.authentication drifted")
    if docs_mcp.get("local_callable") is not False:
        fail("agent_surface_contract.docs_mcp.local_callable must remain false")
    if docs_mcp.get("tools") != {"native-dat": "search_dat_docs", "web-apps": "search_webapps_docs"}:
        fail("agent_surface_contract.docs_mcp.tools drifted")
    expected_agent_surfaces = {
        "native-dat-ios": {
            "repository": "https://github.com/facebook/meta-wearables-dat-ios",
            "plugin_manifest": "plugins/mwdat-ios/.codex-plugin/plugin.json",
            "source_revision": "225f64ff1617e7acc8c407bb8d3ee132f7263d00",
            "docs_mcp_tool": "search_dat_docs",
            "codex_mode": "local-plugin",
        },
        "native-dat-android": {
            "repository": "https://github.com/facebook/meta-wearables-dat-android",
            "plugin_manifest": "plugins/mwdat-android/.codex-plugin/plugin.json",
            "source_revision": "81dfb51b9be26de5cd262bb1dcbb4b8d0d6bd2bc",
            "docs_mcp_tool": "search_dat_docs",
            "codex_mode": "local-plugin",
        },
        "web-apps": {
            "repository": "https://github.com/facebook/meta-wearables-webapp",
            "plugin_manifest": "plugins/meta-wearables-webapp/.codex-plugin/plugin.json",
            "source_revision": "a2714f862c61b1ce9c6cb624fc7e4938087102db",
            "docs_mcp_tool": "search_webapps_docs",
            "codex_mode": "marketplace",
        },
    }
    observed_agent_surfaces = {entry.get("id"): entry for entry in agent_contract.get("surfaces", []) if isinstance(entry, dict)}
    if set(observed_agent_surfaces) != set(expected_agent_surfaces):
        fail("agent_surface_contract surface IDs drifted")
    for surface_id, expected in expected_agent_surfaces.items():
        entry = observed_agent_surfaces[surface_id]
        for field, value in expected.items():
            if field == "codex_mode":
                observed = entry.get("codex_install", {}).get("mode")
            else:
                observed = entry.get(field)
            if observed != value:
                fail(f"agent_surface_contract {surface_id}.{field} drifted")
    if observed_agent_surfaces["web-apps"].get("codex_install", {}).get("refresh") != "codex plugin marketplace upgrade meta-wearables":
        fail("agent_surface_contract web-apps marketplace refresh drifted")
    ios_inventory = source_inventory.get("ios", {})
    expected_ios_products = {
        "MWDATCore",
        "MWDATCamera",
        "MWDATDisplay",
        "MWDATMockDevice",
        "MWDATMockDeviceTestClient",
    }
    if set(ios_inventory.get("products", [])) != expected_ios_products:
        fail("iOS source_inventory products must match the 0.9.0 Package.swift product set")
    if set(ios_inventory.get("binary_targets", [])) != {f"{name}.xcframework" for name in expected_ios_products}:
        fail("iOS source_inventory binary_targets must match the Package.swift products")
    if ios_inventory.get("test_only_products") != ["MWDATMockDeviceTestClient"]:
        fail("iOS source_inventory must identify MWDATMockDeviceTestClient as test-only")
    if ios_inventory.get("plugin_version") != "0.9.0":
        fail("iOS source_inventory plugin_version must be 0.9.0")
    if ios_inventory.get("sample_roots") != ["CameraAccess", "DisplayAccess"]:
        fail("iOS source_inventory sample_roots must include CameraAccess and DisplayAccess")
    if ios_inventory.get("sample_min_ios") != "17.2" or ios_inventory.get("sample_xcode") != "26.4" or ios_inventory.get("sample_swift") != "6.3":
        fail("iOS source_inventory sample toolchain facts drifted")
    for platform in ("android", "web_apps"):
        if not isinstance(source_inventory.get(platform), dict):
            fail(f"source_inventory needs {platform}")
    if source_inventory["android"].get("plugin_version") != "0.9.0":
        fail("Android source_inventory plugin_version must be 0.9.0")
    if source_inventory["web_apps"].get("plugin_version") != "127.0.0":
        fail("Web Apps source_inventory plugin_version must be 127.0.0")
    for platform, expected_roles in EXPECTED_PLUGIN_ROLES.items():
        inventory_roles = source_inventory[platform].get("plugin_roles")
        if inventory_roles != expected_roles:
            fail(f"{platform} source_inventory plugin_roles drifted")
        if source_inventory[platform].get("plugin_skill_count") != len(inventory_roles):
            fail(f"{platform} source_inventory plugin_skill_count does not match plugin_roles")

    native_modules = data["native_modules"]
    api_surface = data["api_surface"]
    counts = {
        "journeys": len(data["journeys"]),
        "ios_modules": len(native_modules["ios"]),
        "android_artifacts": len(native_modules["android"]),
        "capabilities": len(data["capabilities"]),
        "source_conflicts": len(data["source_conflicts"]),
        "generation_labels": len(data["generation_labels"]),
        "evidence_levels": len(data["evidence_ladder"]),
        "refresh_triggers": len(data["refresh_triggers"]),
        "api_rows": len(api_surface.get("rows", [])),
        "terminology_terms": len(data["terminology_contract"].get("terms", [])),
    }
    for key, expected in EXPECTED_COUNTS.items():
        if counts[key] != expected:
            fail(f"{key} count drift: expected {expected}, got {counts[key]}")
    if api_surface.get("revision") != EXPECTED_API_REVISION:
        fail(f"unexpected api_surface revision: {api_surface.get('revision')!r}")

    anchors = set(api_surface.get("source_anchors", {}))
    terminology_contract = data["terminology_contract"]
    if not isinstance(terminology_contract, dict) or not terminology_contract.get("authority_note"):
        fail("terminology_contract needs an authority_note")
    expected_term_ids = {"regular-sdk", "full-sdk", "ray-ban-display", "gen-2", "gen-3"}
    terms = terminology_contract.get("terms", [])
    if {term.get("id") for term in terms} != expected_term_ids:
        fail("terminology_contract term IDs drifted")
    journey_ids = {journey.get("id") for journey in data["journeys"]}
    for term in terms:
        required = {"id", "user_phrases", "resolution_status", "canonical_routes", "source_refs", "public_sdk_family", "agent_action", "evidence_boundary"}
        missing = required - set(term)
        if missing:
            fail(f"terminology term {term.get('id', '<unknown>')} missing keys: {', '.join(sorted(missing))}")
        if not set(term["canonical_routes"]).issubset(journey_ids):
            fail(f"terminology term {term['id']} has unknown canonical_routes")
        unknown_refs = set(term["source_refs"]) - anchors
        if unknown_refs:
            fail(f"terminology term {term['id']} has unknown source_refs: {', '.join(sorted(unknown_refs))}")
    regular_sdk = next(term for term in terms if term["id"] == "regular-sdk")
    if regular_sdk["resolution_status"] != "ambiguous-user-phrase" or regular_sdk["public_sdk_family"] is not False:
        fail("regular-sdk must remain an ambiguous non-family user phrase")
    gen_three = next(term for term in terms if term["id"] == "gen-3")
    if gen_three["resolution_status"] != "unresolved-alias":
        fail("gen-3 must remain unresolved-alias")
    rows = api_surface["rows"]
    row_ids = [row.get("id") for row in rows]
    if any(not row_id for row_id in row_ids):
        fail("every api_surface row needs an id")
    if len(row_ids) != len(set(row_ids)):
        fail("api_surface row ids must be unique")
    for row in rows:
        missing = ROW_KEYS - set(row)
        if missing:
            fail(f"{row['id']} missing keys: {', '.join(sorted(missing))}")
        unknown_refs = set(row["source_refs"]) - anchors
        if unknown_refs:
            fail(f"{row['id']} has unknown source_refs: {', '.join(sorted(unknown_refs))}")
        if not row["symbols"] or not row["fallback"] or not row["compile_or_runtime_gate"]:
            fail(f"{row['id']} must include symbols, fallback, and compile/runtime gate")

    for capability in data["capabilities"]:
        if not capability.get("preflight_tasks"):
            fail(f"{capability.get('id', '<unknown>')} needs preflight_tasks")
        unknown_tasks = set(capability["preflight_tasks"]) - set(EXPECTED_PREFLIGHT_TASK_IDS)
        if unknown_tasks:
            fail(
                f"{capability.get('id', '<unknown>')} has unknown preflight_tasks: "
                f"{', '.join(sorted(unknown_tasks))}"
            )
        if "PRE-SOURCE-01" not in capability["preflight_tasks"]:
            fail(f"{capability.get('id', '<unknown>')} must include PRE-SOURCE-01")

    print(f"OK manifest={manifest_path}")
    print(f"  manifest_id={data['manifest_id']}")
    print(f"  manifest_revision={data['manifest_revision']}")
    print(f"  api_revision={api_surface['revision']}")
    print(f"  api_rows={counts['api_rows']} journeys={counts['journeys']} capabilities={counts['capabilities']}")
    print(f"  ios_modules={counts['ios_modules']} android_artifacts={counts['android_artifacts']}")
    print(f"  terminology_terms={counts['terminology_terms']}")
    print(f"  preflight_tasks={len(preflight_ids)} mapped_capabilities={len(data['capabilities'])}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, KeyError, TypeError, ValueError, yaml.YAMLError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        raise SystemExit(1)
