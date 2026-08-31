#!/usr/bin/env python3
"""Validate the machine-readable Meta Wearables capability/evidence plan."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


EXPECTED_PLAN_ID = "meta-wearables-capability-evidence-plan-2026-08-22"
EXPECTED_MANIFEST_ID = "meta-wearables-public-surface-2026-08-22"
EXPECTED_LEVELS = (
    "source",
    "static",
    "build",
    "mock",
    "browser-sim",
    "connected",
    "physical",
    "signed",
    "release-channel",
    "production",
)
SECRET_PATTERN = re.compile(
    r"(?:sk|pk)_(?:live|test)_[A-Za-z0-9]+|Bearer\s+[A-Za-z0-9._-]{20,}|"
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    package_dir = Path(__file__).resolve().parent.parent
    parser.add_argument(
        "plan",
        nargs="?",
        type=Path,
        default=package_dir / "references" / "capability-evidence-plan.yaml",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=package_dir / "references" / "surface-manifest.yaml",
    )
    return parser.parse_args()


def fail(message: str) -> None:
    raise ValueError(message)


def load_yaml(path: Path) -> dict:
    if not path.is_file():
        fail(f"file not found: {path.resolve()}")
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"YAML root must be a mapping: {path}")
    return value


def main() -> int:
    args = parse_args()
    plan_path = args.plan.resolve()
    manifest_path = args.manifest.resolve()
    raw = plan_path.read_text(encoding="utf-8") if plan_path.is_file() else ""
    if SECRET_PATTERN.search(raw):
        fail("plan contains a credential-like token or private key marker")
    plan = load_yaml(plan_path)
    manifest = load_yaml(manifest_path)

    if plan.get("schema_version") != 1:
        fail(f"schema_version must be 1, got {plan.get('schema_version')!r}")
    if plan.get("plan_id") != EXPECTED_PLAN_ID:
        fail(f"unexpected plan_id: {plan.get('plan_id')!r}")
    if plan.get("manifest_id") != EXPECTED_MANIFEST_ID:
        fail(f"unexpected plan manifest_id: {plan.get('manifest_id')!r}")
    if tuple(plan.get("evidence_levels", [])) != EXPECTED_LEVELS:
        fail("evidence_levels must match the canonical evidence ladder")

    catalog = plan.get("task_catalog")
    if not isinstance(catalog, list) or not catalog:
        fail("task_catalog must be a non-empty list")
    task_levels: dict[str, set[str]] = {}
    for task in catalog:
        if not isinstance(task, dict) or not task.get("id") or not task.get("purpose"):
            fail("every task_catalog entry needs id and purpose")
        task_id = task["id"]
        if task_id in task_levels:
            fail(f"duplicate task_catalog id: {task_id}")
        levels = set(task.get("levels", []))
        if not levels or not levels <= set(EXPECTED_LEVELS):
            fail(f"{task_id} has invalid levels: {sorted(levels)}")
        task_levels[task_id] = levels

    manifest_capabilities = {item.get("id"): item for item in manifest.get("capabilities", [])}
    plan_capabilities = plan.get("capabilities")
    if not isinstance(plan_capabilities, list):
        fail("capabilities must be a list")
    plan_ids = [item.get("id") for item in plan_capabilities if isinstance(item, dict)]
    if set(plan_ids) != set(manifest_capabilities) or len(plan_ids) != len(set(plan_ids)):
        fail("plan capability IDs must exactly match the manifest capability IDs")

    preflight_ids = set(manifest.get("preflight_contract", {}).get("task_ids", []))
    for capability in plan_capabilities:
        if not isinstance(capability, dict):
            fail("every capability plan entry must be a mapping")
        capability_id = capability.get("id")
        manifest_capability = manifest_capabilities[capability_id]
        for field in ("surfaces", "owner_roles", "implementation_route", "privacy_path", "fallback", "claim_boundary", "preflight_tasks", "required_levels", "evidence_tasks", "next_gate"):
            if not capability.get(field):
                fail(f"{capability_id} needs {field}")
        if set(capability["surfaces"]) != set(manifest_capability.get("surfaces", [])):
            fail(f"{capability_id} surfaces drift from surface manifest")
        if set(capability["preflight_tasks"]) != set(manifest_capability.get("preflight_tasks", [])):
            fail(f"{capability_id} preflight_tasks drift from surface manifest")
        if not set(capability["preflight_tasks"]) <= preflight_ids:
            fail(f"{capability_id} has an unknown preflight task")
        required_levels = set(capability["required_levels"])
        if not required_levels <= set(EXPECTED_LEVELS):
            fail(f"{capability_id} has invalid required_levels: {sorted(required_levels)}")
        if capability["next_gate"] not in required_levels:
            fail(f"{capability_id} next_gate must be in required_levels")
        evidence_tasks = capability["evidence_tasks"]
        if len(evidence_tasks) != len(set(evidence_tasks)):
            fail(f"{capability_id} evidence_tasks must be unique")
        unknown_tasks = set(evidence_tasks) - set(task_levels)
        if unknown_tasks:
            fail(f"{capability_id} has unknown evidence_tasks: {', '.join(sorted(unknown_tasks))}")
        manifest_evidence = set(manifest_capability.get("evidence", []))
        if not manifest_evidence <= set(evidence_tasks):
            missing = ", ".join(sorted(manifest_evidence - set(evidence_tasks)))
            fail(f"{capability_id} does not carry manifest evidence IDs: {missing}")
        observed_levels = set().union(*(task_levels[task_id] for task_id in evidence_tasks))
        if not required_levels <= observed_levels:
            missing = ", ".join(sorted(required_levels - observed_levels))
            fail(f"{capability_id} lacks evidence tasks for levels: {missing}")

    print(f"OK capability_evidence_plan={plan_path}")
    print(f"  plan_id={plan['plan_id']} manifest_id={plan['manifest_id']}")
    print(f"  capabilities={len(plan_capabilities)} tasks={len(task_levels)} levels={len(EXPECTED_LEVELS)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, TypeError, ValueError, yaml.YAMLError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        raise SystemExit(1)
