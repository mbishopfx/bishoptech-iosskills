#!/usr/bin/env python3
"""Emit a source-pinned Meta Wearables capability/team routing receipt.

This is a read-only orchestration helper. It selects existing manifest entries;
it does not invent APIs, resolve credentials, inspect account state, build an
app, or promote a source/static result to physical or release evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


SURFACES = ("native-dat-ios", "native-dat-android", "web-apps", "phone-fallback")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    selector = parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--capability", help="capability ID from capability-evidence-plan.yaml")
    selector.add_argument(
        "--full-sdk",
        action="store_true",
        help="route the composite full-SDK request across every planned capability",
    )
    parser.add_argument("--surface", choices=SURFACES, help="limit the receipt to one delivery surface")
    parser.add_argument("--workspace-root", type=Path, default=Path.cwd())
    parser.add_argument("--team-manifest", type=Path)
    parser.add_argument("--surface-manifest", type=Path)
    parser.add_argument("--capability-plan", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def fail(message: str) -> None:
    raise ValueError(message)


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail(f"manifest not found: {path.resolve()}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail(f"manifest root must be a mapping: {path}")
    return data


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def resolve_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    workspace_root = args.workspace_root.resolve()
    packages_root = workspace_root / "knowledge-base" / "skills" / "packages"
    team_path = (args.team_manifest or packages_root / "meta-wearables-agentic-team/references/team-manifest.yaml").resolve()
    surface_path = (args.surface_manifest or packages_root / "meta-wearables-full-sdk-audit/references/surface-manifest.yaml").resolve()
    plan_path = (args.capability_plan or packages_root / "meta-wearables-full-sdk-audit/references/capability-evidence-plan.yaml").resolve()
    return team_path, surface_path, plan_path


def compact_term(term: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": term.get("id"),
        "resolution_status": term.get("resolution_status"),
        "canonical_routes": term.get("canonical_routes", []),
        "agent_action": term.get("agent_action"),
        "evidence_boundary": term.get("evidence_boundary"),
    }


def compact_capability(capability: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "id",
        "surfaces",
        "owner_roles",
        "implementation_route",
        "privacy_path",
        "fallback",
        "claim_boundary",
        "preflight_tasks",
        "required_levels",
        "evidence_tasks",
        "next_gate",
    )
    return {field: capability.get(field) for field in fields if field in capability}


def handoff_id(handoff: dict[str, Any]) -> str:
    return f"{handoff.get('surface')}:{handoff.get('role')}"


def ordered_evidence_levels(levels: list[str], order: list[str]) -> list[str]:
    rank = {level: index for index, level in enumerate(order)}
    return sorted(unique(levels), key=lambda level: (rank.get(level, len(rank)), level))


def main() -> int:
    args = parse_args()
    team_path, surface_path, plan_path = resolve_paths(args)
    team = load_yaml(team_path)
    surface_manifest = load_yaml(surface_path)
    plan = load_yaml(plan_path)

    team_surfaces = [entry for entry in team.get("surfaces", []) if isinstance(entry, dict)]
    team_surface_ids = [entry.get("id") for entry in team_surfaces]
    if set(team_surface_ids) != set(SURFACES):
        fail(f"team surface IDs drifted: expected {list(SURFACES)}, got {team_surface_ids}")

    capabilities = [entry for entry in plan.get("capabilities", []) if isinstance(entry, dict)]
    capability_by_id = {entry.get("id"): entry for entry in capabilities}
    selected_capabilities: list[dict[str, Any]]
    request_kind: str

    if args.full_sdk:
        request_kind = "full-sdk"
        if args.surface == "phone-fallback":
            fail("--full-sdk --surface phone-fallback is ambiguous; the phone route is a fallback, not a standalone plan capability")
        selected_capabilities = [
            capability
            for capability in capabilities
            if not args.surface or args.surface in capability.get("surfaces", [])
        ]
        if not selected_capabilities:
            fail(f"no planned capabilities use surface {args.surface!r}")
        selected_surface_ids = [args.surface] if args.surface else list(SURFACES)
    else:
        request_kind = "capability"
        if args.capability not in capability_by_id:
            fail(f"unknown capability {args.capability!r}; expected one of {sorted(capability_by_id)}")
        selected_capabilities = [capability_by_id[args.capability]]
        selected_surface_ids = list(selected_capabilities[0].get("surfaces", []))
        if args.surface:
            if args.surface not in selected_surface_ids:
                fail(f"capability {args.capability!r} does not include surface {args.surface!r}")
            selected_surface_ids = [args.surface]

    team_roles = [entry for entry in team.get("team_roles", []) if isinstance(entry, dict)]
    role_ids = {entry.get("id") for entry in team_roles}
    owner_roles = unique(
        [role for capability in selected_capabilities for role in capability.get("owner_roles", [])]
    )
    missing_owner_roles = sorted(set(owner_roles) - role_ids)
    if missing_owner_roles:
        fail(f"capability owner roles are absent from team manifest: {missing_owner_roles}")

    handoffs = [entry for entry in team.get("upstream_role_handoffs", []) if isinstance(entry, dict)]
    selected_handoffs = [entry for entry in handoffs if entry.get("surface") in selected_surface_ids]
    selected_handoff_ids = [handoff_id(entry) for entry in selected_handoffs]
    selected_roles = unique(owner_roles)
    if args.full_sdk and not args.surface:
        selected_roles = [entry.get("id") for entry in team_roles]
    else:
        selected_roles.extend(
            entry.get("id")
            for entry in team_roles
            if set(entry.get("surfaces", [])) & set(selected_surface_ids)
        )
        selected_roles = unique([role for role in selected_roles if role])

    evidence_order = team.get("handoff_contract", {}).get("evidence_order", [])
    required_levels = ordered_evidence_levels(
        [level for capability in selected_capabilities for level in capability.get("required_levels", [])],
        evidence_order,
    )
    preflight_tasks = unique(
        [task for capability in selected_capabilities for task in capability.get("preflight_tasks", [])]
    )
    evidence_tasks = unique(
        [task for capability in selected_capabilities for task in capability.get("evidence_tasks", [])]
    )
    claim_boundaries = unique(
        [capability.get("claim_boundary") for capability in selected_capabilities if capability.get("claim_boundary")]
    )

    terminology = surface_manifest.get("terminology_contract", {})
    terms = [entry for entry in terminology.get("terms", []) if isinstance(entry, dict)]
    source_snapshot = surface_manifest.get("snapshot", {})
    agent_surface_contract = surface_manifest.get("agent_surface_contract", {})
    if not isinstance(agent_surface_contract, dict):
        fail("surface manifest agent_surface_contract is missing")
    docs_mcp = agent_surface_contract.get("docs_mcp", {})
    if docs_mcp.get("endpoint") != "https://mcp.developer.meta.com/wearables":
        fail("surface manifest agent_surface_contract docs MCP endpoint drifted")
    if docs_mcp.get("local_callable") is not False:
        fail("surface manifest agent_surface_contract cannot promote local MCP availability")
    agent_surfaces = [entry for entry in agent_surface_contract.get("surfaces", []) if isinstance(entry, dict)]
    agent_surface_by_id = {entry.get("id"): entry for entry in agent_surfaces}
    selected_agent_surface_ids = [surface_id for surface_id in selected_surface_ids if surface_id in agent_surface_by_id]
    manifest_ids = {
        "team_manifest_id": team.get("manifest_id"),
        "team_manifest_revision": team.get("manifest_revision"),
        "surface_manifest_id": surface_manifest.get("manifest_id"),
        "surface_manifest_revision": surface_manifest.get("manifest_revision"),
        "capability_plan_id": plan.get("plan_id"),
    }

    if request_kind == "full-sdk":
        next_action = (
            "Run team preflight with --live-source, preserve this composite receipt, then select one vertical slice "
            "before implementation; full SDK is an audit across DAT iOS, DAT Android, Web Apps, phone fallback, and proof lanes."
        )
    else:
        next_gate = unique([capability.get("next_gate") for capability in selected_capabilities if capability.get("next_gate")])
        next_action = (
            "Run team preflight with --live-source and the target handoff, then load the implementation-recipes role; "
            f"first capability gate={next_gate[0] if next_gate else 'to-verify'}."
        )

    receipt: dict[str, Any] = {
        "receipt_version": 1,
        "request_kind": request_kind,
        "request": "full Meta Wearables SDK composite audit" if args.full_sdk else args.capability,
        "surface_filter": args.surface,
        "selected_surfaces": selected_surface_ids,
        "selected_surface_labels": {
            entry.get("id"): entry.get("label")
            for entry in team_surfaces
            if entry.get("id") in selected_surface_ids
        },
        "manifests": manifest_ids,
        "source_snapshot": {
            "reviewed_at": source_snapshot.get("reviewed_at"),
            "current_dat_release": source_snapshot.get("current_dat_release"),
            "web_apps_revision": source_snapshot.get("web_apps_revision"),
            "full_reference_url": source_snapshot.get("full_reference_url"),
            "authenticated_developer_center": source_snapshot.get("authenticated_developer_center"),
            "callable_wearables_mcp_in_workspace": source_snapshot.get("callable_wearables_mcp_in_workspace"),
            "docs_mcp_authentication": source_snapshot.get("docs_mcp_authentication"),
        },
        "agent_surface_contract": {
            "source_only": True,
            "docs_mcp": docs_mcp,
            "selected_surfaces": [agent_surface_by_id[surface_id] for surface_id in selected_agent_surface_ids],
            "phone_fallback_has_no_upstream_agent_plugin": "phone-fallback" in selected_surface_ids,
        },
        "capabilities": [compact_capability(capability) for capability in selected_capabilities],
        "selected_local_roles": selected_roles,
        "owner_roles": owner_roles,
        "selected_upstream_role_handoff_ids": selected_handoff_ids,
        "selected_upstream_role_handoffs": selected_handoffs,
        "preflight_tasks": preflight_tasks,
        "required_evidence_levels": required_levels,
        "evidence_tasks": evidence_tasks,
        "claim_boundaries": claim_boundaries,
        "terminology": {
            "authority_note": terminology.get("authority_note"),
            "terms": [compact_term(term) for term in terms],
        },
        "status": "route-and-source receipt only",
        "non_claims": [
            "This receipt does not prove package compilation, account access, registration, named-device capability, physical behavior, signed release, or production.",
            "Phone-local or remote processing must not be labeled glasses-native without a separate processing-location receipt.",
            "Gen 3 remains unresolved unless an official mapping and named runtime evidence close the compatibility gate.",
        ],
        "next_action": next_action,
    }

    if args.as_json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(
            f"ROUTE_RECEIPT request={request_kind} surfaces={','.join(selected_surface_ids)} "
            f"capabilities={len(selected_capabilities)} local_roles={len(selected_roles)} "
            f"upstream_handoffs={len(selected_handoffs)}"
        )
        print(f"MANIFESTS team={manifest_ids['team_manifest_revision']} surface={manifest_ids['surface_manifest_revision']} plan={manifest_ids['capability_plan_id']}")
        print(f"EVIDENCE {' '.join(required_levels)}")
        print(f"PREFLIGHT {' '.join(preflight_tasks)}")
        print(f"AGENT_SURFACES {' '.join(selected_agent_surface_ids) or 'none'} MCP_LOCAL={str(docs_mcp.get('local_callable')).lower()}")
        print(f"NEXT {next_action}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, TypeError, ValueError, yaml.YAMLError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        raise SystemExit(2)
