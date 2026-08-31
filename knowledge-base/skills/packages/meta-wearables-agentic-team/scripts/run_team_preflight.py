#!/usr/bin/env python3
"""Run the Meta Wearables team checks and emit one routing receipt.

The runner is intentionally evidence-conservative. It can report that a
workspace needs bootstrap, source refresh, manifest repair, implementation
handoff, or target preflight; it never upgrades a source/static result into
build or hardware proof.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
TEAM_VALIDATOR = PACKAGE_ROOT / "scripts" / "validate_team_manifest.py"
TARGET_SCANNER = PACKAGE_ROOT / "scripts" / "inspect_target_surfaces.py"


def tail(text: str, limit: int = 12) -> list[str]:
    lines = [line for line in text.splitlines() if line.strip()]
    return lines[-limit:]


def run_check(label: str, command: list[str], cwd: Path) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        return {
            "label": label,
            "status": "failed",
            "returncode": None,
            "output_tail": [f"could not execute: {error}"],
        }

    output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
    return {
        "label": label,
        "status": "pass" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "output_tail": tail(output),
    }


def unavailable(label: str, reason: str) -> dict[str, Any]:
    return {"label": label, "status": "unavailable", "returncode": None, "output_tail": [reason]}


def not_run(label: str, reason: str) -> dict[str, Any]:
    return {"label": label, "status": "not-run", "returncode": None, "output_tail": [reason]}


def path_if_file(root: Path, relative_path: str) -> Path | None:
    path = root / relative_path
    return path if path.is_file() else None


def run_target_scan(target_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    command = [sys.executable, str(TARGET_SCANNER), str(target_root), "--json"]
    try:
        completed = subprocess.run(
            command,
            cwd=target_root,
            check=False,
            capture_output=True,
            text=True,
        )
        output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
        result: dict[str, Any] = {
            "label": "target-surface",
            "status": "pass" if completed.returncode == 0 else "failed",
            "returncode": completed.returncode,
            "output_tail": tail(output),
        }
        if completed.returncode != 0:
            return {}, result
        scan = json.loads(completed.stdout)
        result["receipt"] = scan
        result["output_tail"] = [
            f"overall={scan.get('overall')} implementation_target={str(scan.get('implementation_target')).lower()} bootstrap_required={str(scan.get('bootstrap_required')).lower()}",
            f"configured_surfaces={scan.get('configured_surfaces', [])} partial_surfaces={scan.get('partial_surfaces', [])}",
            f"next_action={scan.get('next_action')}",
        ]
        return scan, result
    except (json.JSONDecodeError, OSError) as error:
        result = {
            "label": "target-surface",
            "status": "failed",
            "returncode": None,
            "output_tail": [f"target scanner did not return JSON: {error}"],
        }
        result["status"] = "failed"
        return {}, result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace_root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--target-root", type=Path)
    parser.add_argument("--live-source", action="store_true", help="run official source/tree checks")
    parser.add_argument("--implementation-handoff", type=Path, help="validate a concrete implementation handoff packet")
    parser.add_argument("--allow-handoff-placeholders", action="store_true", help="allow placeholders in the handoff packet")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--require-complete", action="store_true", help="exit 2 unless the decision is target-preflight")
    args = parser.parse_args()

    workspace_root = args.workspace_root.resolve()
    target_root = (args.target_root or workspace_root).resolve()
    if not workspace_root.is_dir():
        raise SystemExit(f"workspace root is not a directory: {workspace_root}")
    if not target_root.is_dir():
        raise SystemExit(f"target root is not a directory: {target_root}")

    surface_manifest = path_if_file(
        workspace_root,
        "knowledge-base/skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml",
    )
    capability_plan = path_if_file(
        workspace_root,
        "knowledge-base/skills/packages/meta-wearables-full-sdk-audit/references/capability-evidence-plan.yaml",
    )
    surface_validator = path_if_file(
        workspace_root,
        "knowledge-base/skills/packages/meta-wearables-full-sdk-audit/scripts/validate_surface_manifest.py",
    )
    capability_validator = path_if_file(
        workspace_root,
        "knowledge-base/skills/packages/meta-wearables-full-sdk-audit/scripts/validate_capability_evidence_plan.py",
    )
    handoff_validator = path_if_file(
        workspace_root,
        "knowledge-base/skills/packages/meta-wearables-implementation-recipes/scripts/validate_implementation_handoff.py",
    )
    source_tree_checker = path_if_file(
        workspace_root,
        "knowledge-base/skills/packages/meta-wearables-source-refresh/scripts/check_source_tree_inventory.py",
    )
    source_revision_checker = path_if_file(
        workspace_root,
        "knowledge-base/skills/packages/meta-wearables-source-refresh/scripts/check_source_revisions.py",
    )

    target_receipt, target_check = run_target_scan(target_root)
    checks: list[dict[str, Any]] = [target_check]

    team_command = [sys.executable, str(TEAM_VALIDATOR), "--workspace-root", str(workspace_root)]
    if surface_manifest:
        team_command.extend(["--surface-manifest", str(surface_manifest)])
    checks.append(run_check("team-manifest", team_command, workspace_root))

    if surface_manifest and surface_validator:
        checks.append(run_check("surface-manifest", [sys.executable, str(surface_validator), str(surface_manifest)], workspace_root))
    else:
        checks.append(unavailable("surface-manifest", "workspace surface manifest or validator is unavailable"))

    if capability_plan and capability_validator and surface_manifest:
        checks.append(
            run_check(
                "capability-evidence-plan",
                [
                    sys.executable,
                    str(capability_validator),
                    str(capability_plan),
                    "--manifest",
                    str(surface_manifest),
                ],
                workspace_root,
            )
        )
    else:
        checks.append(unavailable("capability-evidence-plan", "workspace capability plan, manifest, or validator is unavailable"))

    if args.live_source and source_tree_checker and source_revision_checker:
        checks.append(run_check("source-tree", [sys.executable, str(source_tree_checker)], workspace_root))
        checks.append(run_check("source-revisions", [sys.executable, str(source_revision_checker)], workspace_root))
    elif args.live_source:
        checks.append(unavailable("source-refresh", "workspace source-refresh checkers are unavailable"))
    else:
        checks.append(not_run("source-refresh", "pass --live-source for official repository and full-reference checks"))

    if args.implementation_handoff:
        handoff = args.implementation_handoff.resolve()
        if handoff_validator and surface_manifest and capability_plan and handoff.is_file():
            handoff_command = [
                sys.executable,
                str(handoff_validator),
                str(handoff),
                "--manifest",
                str(surface_manifest),
                "--plan",
                str(capability_plan),
                "--team-manifest",
                str(workspace_root / "knowledge-base/skills/packages/meta-wearables-agentic-team/references/team-manifest.yaml"),
            ]
            if args.allow_handoff_placeholders:
                handoff_command.append("--allow-placeholders")
            checks.append(run_check("implementation-handoff", handoff_command, workspace_root))
        else:
            checks.append(unavailable("implementation-handoff", "handoff packet, validator, manifest, or capability plan is unavailable"))
    else:
        checks.append(not_run("implementation-handoff", "pass --implementation-handoff for implementation readiness"))

    target_overall = target_receipt.get("overall", "UNKNOWN")
    failed = [check["label"] for check in checks if check["status"] == "failed"]
    unavailable_checks = [check["label"] for check in checks if check["status"] == "unavailable"]
    source_not_verified = any(check["label"] == "source-refresh" and check["status"] == "not-run" for check in checks)
    handoff_not_verified = any(check["label"] == "implementation-handoff" and check["status"] == "not-run" for check in checks)

    if target_overall in {"NO_TARGET", "TARGETS_PARTIAL", "UNKNOWN"}:
        decision = "bootstrap"
        next_action = "Create or identify a sibling implementation project, then rerun this receipt."
    elif failed:
        decision = "repair-failed-checks"
        next_action = "Resolve failed checks before target-specific implementation or evidence promotion."
    elif unavailable_checks:
        decision = "complete-missing-checks"
        next_action = "Make the unavailable workspace/source checks available, then rerun the receipt."
    elif source_not_verified:
        decision = "source-refresh-required"
        next_action = "Run again with --live-source before using the target-specific handoff."
    elif handoff_not_verified:
        decision = "implementation-handoff-required"
        next_action = "Create and validate the implementation-handoff packet before target-specific code is ready."
    else:
        decision = "target-preflight"
        next_action = "Load the device-proof target-preflight reference and freeze the exact target tuple."

    receipt = {
        "receipt_version": 1,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "workspace_root": str(workspace_root),
        "target_root": str(target_root),
        "decision": decision,
        "next_action": next_action,
        "target_surface": target_receipt,
        "checks": checks,
        "failed_checks": failed,
        "unavailable_checks": unavailable_checks,
        "live_source_requested": args.live_source,
        "implementation_handoff_requested": bool(args.implementation_handoff),
    }

    if args.as_json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(f"TEAM_PREFLIGHT decision={decision} target={target_overall} live_source={str(args.live_source).lower()}")
        for check in checks:
            print(f"CHECK {check['label']} {check['status']}")
            for line in check.get("output_tail", []):
                print(f"  {line}")
        print(f"NEXT {next_action}")

    if args.require_complete and decision != "target-preflight":
        return 2
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
