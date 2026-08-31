#!/usr/bin/env python3
"""Run the portable Meta Wearables static/mock fixture suite.

The suite gives the agent team one conservative receipt for reusable domain,
Web App, Android-target-preflight, manifest, recipe, target-intake, and routing checks. An
optional iOS DAT checkout adds typechecks for the four source-aligned iOS
starters. It never turns a fixture, source check, simulator, or target
preflight into connected, physical, signed, or release evidence.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def tail(text: str, limit: int = 10) -> list[str]:
    lines = [line for line in text.splitlines() if line.strip()]
    return lines[-limit:]


def unavailable(label: str, reason: str) -> dict[str, Any]:
    return {
        "label": label,
        "status": "unavailable",
        "returncode": None,
        "output_tail": [reason],
    }


def not_run(label: str, reason: str) -> dict[str, Any]:
    return {
        "label": label,
        "status": "not-run",
        "returncode": None,
        "output_tail": [reason],
    }


def run_command(
    label: str,
    command: list[str],
    cwd: Path,
    *,
    timeout: int = 120,
    json_output: bool = False,
) -> dict[str, Any]:
    executable = command[0]
    if not Path(executable).is_file() and shutil.which(executable) is None:
        return unavailable(label, f"executable unavailable: {executable}")
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {
            "label": label,
            "status": "failed",
            "returncode": None,
            "output_tail": [f"timed out after {timeout}s"],
        }
    except OSError as error:
        return unavailable(label, f"could not execute: {error}")

    output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
    result: dict[str, Any] = {
        "label": label,
        "status": "pass" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "output_tail": tail(output),
    }
    if json_output and completed.returncode == 0:
        try:
            result["receipt"] = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            result["status"] = "failed"
            result["output_tail"] = [f"expected JSON receipt: {error}", *tail(output)]
    return result


def compact_receipt(result: dict[str, Any], fields: tuple[str, ...]) -> None:
    receipt = result.get("receipt")
    if not isinstance(receipt, dict):
        return
    result["receipt_summary"] = {field: receipt.get(field) for field in fields if field in receipt}
    result.pop("receipt", None)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace_root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument(
        "--ios-dat-checkout",
        type=Path,
        help="optional DAT iOS checkout containing the simulator XCFrameworks",
    )
    parser.add_argument("--live-source", action="store_true", help="also run the official source/tree checks")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def path(root: Path, relative: str) -> Path:
    return root / relative


def macos_sdk_path(workspace_root: Path) -> str | None:
    if shutil.which("xcrun") is None:
        return None
    try:
        result = subprocess.run(
            ["xcrun", "--sdk", "macosx", "--show-sdk-path"],
            cwd=workspace_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else None


def run_ios_typechecks(workspace_root: Path, checkout: Path) -> list[dict[str, Any]]:
    if not checkout.is_dir():
        return [unavailable("ios-typechecks", f"DAT iOS checkout not found: {checkout}")]
    if shutil.which("swiftc") is None or shutil.which("xcrun") is None:
        return [unavailable("ios-typechecks", "swiftc or xcrun is unavailable")]

    sdk_result = subprocess.run(
        ["xcrun", "--sdk", "iphonesimulator", "--show-sdk-path"],
        cwd=workspace_root,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if sdk_result.returncode != 0 or not sdk_result.stdout.strip():
        return [unavailable("ios-typechecks", "iphonesimulator SDK path could not be resolved")]
    sdk_path = sdk_result.stdout.strip()
    module_names = ("MWDATCore", "MWDATCamera", "MWDATDisplay", "MWDATMockDevice", "MWDATMockDeviceTestClient")
    framework_flags: list[str] = []
    for module in module_names:
        slice_root = checkout / f"{module}.xcframework" / "ios-arm64_x86_64-simulator"
        if not (slice_root / f"{module}.framework").is_dir():
            return [unavailable("ios-typechecks", f"simulator framework slice missing: {module}")]
        framework_flags.extend(["-F", str(slice_root)])

    starter_files = (
        ("ios-camera-typecheck", "knowledge-base/skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-ios-camera-starter/MetaWearablesCameraStarter.swift"),
        ("ios-display-typecheck", "knowledge-base/skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-ios-display-starter/MetaWearablesDisplayStarter.swift"),
        ("ios-mockdevice-typecheck", "knowledge-base/skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-ios-mockdevice-starter/MetaWearablesMockDeviceStarter.swift"),
        ("ios-mockdevice-test-client-typecheck", "knowledge-base/skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-ios-mockdevice-test-client-starter/MetaWearablesMockDeviceTestClientStarter.swift"),
    )
    results: list[dict[str, Any]] = []
    for label, relative_file in starter_files:
        source = path(workspace_root, relative_file)
        if not source.is_file():
            results.append(unavailable(label, f"starter not found: {relative_file}"))
            continue
        command = [
            "swiftc",
            "-typecheck",
            "-target",
            "arm64-apple-ios17.2-simulator",
            "-sdk",
            sdk_path,
            *framework_flags,
            str(source),
        ]
        results.append(run_command(label, command, workspace_root, timeout=60))
    return results


def main() -> int:
    args = parse_args()
    workspace_root = args.workspace_root.resolve()
    if not workspace_root.is_dir():
        raise SystemExit(f"workspace root is not a directory: {workspace_root}")

    domain_package = path(
        workspace_root,
        "knowledge-base/skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-domain-starter",
    )
    web_package = path(
        workspace_root,
        "knowledge-base/skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-web-starter",
    )
    android_target = path(
        workspace_root,
        "knowledge-base/skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-android-target-starter",
    )
    web_preflight = path(workspace_root, "knowledge-base/skills/packages/meta-wearables-web-apps/scripts/run_webapp_preflight.py")
    android_preflight = path(workspace_root, "knowledge-base/skills/packages/meta-wearables-device-proof/scripts/run_android_target_preflight.py")
    surface_manifest = path(workspace_root, "knowledge-base/skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml")
    capability_plan = path(workspace_root, "knowledge-base/skills/packages/meta-wearables-full-sdk-audit/references/capability-evidence-plan.yaml")
    team_manifest = path(workspace_root, "knowledge-base/skills/packages/meta-wearables-agentic-team/references/team-manifest.yaml")
    handoff_validator = path(workspace_root, "knowledge-base/skills/packages/meta-wearables-implementation-recipes/scripts/validate_implementation_handoff.py")
    handoff_packets_root = path(workspace_root, "knowledge-base/70-meta-wearables/target-intakes")

    checks: list[dict[str, Any]] = []
    with TemporaryDirectory(prefix="meta-wearables-fixtures-") as scratch:
        domain_command = [
            "swift",
            "test",
            "--package-path",
            str(domain_package),
            "--scratch-path",
            scratch,
            "--disable-sandbox",
        ]
        sdk_path = macos_sdk_path(workspace_root)
        if sdk_path:
            domain_command = ["env", f"SDKROOT={sdk_path}", *domain_command]
        checks.append(
            run_command(
                "shared-domain-tests",
                domain_command,
                workspace_root,
                timeout=120,
            )
        )
    checks.append(
        run_command(
            "web-app-node-tests",
            ["node", "--test", str(web_package / "test/display-state.test.mjs")],
            workspace_root,
            timeout=60,
        )
    )
    web_result = run_command(
        "web-app-static-preflight",
        [sys.executable, str(web_preflight), str(web_package), "--require-meta-markers", "--node-check", "--json"],
        workspace_root,
        timeout=60,
        json_output=True,
    )
    compact_receipt(web_result, ("status", "evidence_level", "surface_class", "next_gate", "source_contract", "origin"))
    checks.append(web_result)

    android_result = run_command(
        "android-target-static-preflight",
        [sys.executable, str(android_preflight), str(android_target), "--json"],
        workspace_root,
        timeout=60,
        json_output=True,
    )
    compact_receipt(android_result, ("status", "evidence_level", "route", "build_graph", "toolchain", "dependency_graph", "next_gate"))
    checks.append(android_result)

    checks.extend(
        [
            run_command(
                "surface-manifest-validator",
                [sys.executable, str(path(workspace_root, "knowledge-base/skills/packages/meta-wearables-full-sdk-audit/scripts/validate_surface_manifest.py")), str(surface_manifest)],
                workspace_root,
            ),
            run_command(
                "capability-plan-validator",
                [sys.executable, str(path(workspace_root, "knowledge-base/skills/packages/meta-wearables-full-sdk-audit/scripts/validate_capability_evidence_plan.py")), str(capability_plan), "--manifest", str(surface_manifest)],
                workspace_root,
            ),
            run_command(
                "team-manifest-validator",
                [sys.executable, str(path(workspace_root, "knowledge-base/skills/packages/meta-wearables-agentic-team/scripts/validate_team_manifest.py")), str(team_manifest), "--surface-manifest", str(surface_manifest), "--workspace-root", str(workspace_root)],
                workspace_root,
            ),
            run_command(
                "recipe-reference-validator",
                [sys.executable, str(path(workspace_root, "knowledge-base/skills/packages/meta-wearables-implementation-recipes/scripts/validate_recipe_reference.py")), str(path(workspace_root, "knowledge-base/skills/packages/meta-wearables-implementation-recipes/references/implementation-recipes.md"))],
                workspace_root,
            ),
        ]
    )
    handoff_packets = sorted(handoff_packets_root.glob("*.yaml")) if handoff_packets_root.is_dir() else []
    if handoff_packets:
        for packet in handoff_packets:
            checks.append(
                run_command(
                    f"implementation-handoff:{packet.stem}",
                    [
                        sys.executable,
                        str(handoff_validator),
                        str(packet),
                        "--manifest",
                        str(surface_manifest),
                        "--plan",
                        str(capability_plan),
                        "--team-manifest",
                        str(team_manifest),
                    ],
                    workspace_root,
                )
            )
    else:
        checks.append(not_run("implementation-handoffs", "no target-intake YAML packets were found"))

    route_result = run_command(
        "full-sdk-route-receipt",
        [sys.executable, str(path(workspace_root, "knowledge-base/skills/packages/meta-wearables-agentic-team/scripts/route_capability.py")), "--full-sdk", "--json"],
        workspace_root,
        timeout=60,
        json_output=True,
    )
    compact_receipt(route_result, ("request_kind", "selected_surfaces", "capabilities", "selected_local_roles", "selected_upstream_role_handoffs", "preflight_tasks", "evidence_order", "source_snapshot", "terminology"))
    checks.append(route_result)

    if args.live_source:
        checks.extend(
            [
                run_command(
                    "source-tree-checker",
                    [sys.executable, str(path(workspace_root, "knowledge-base/skills/packages/meta-wearables-source-refresh/scripts/check_source_tree_inventory.py")), str(surface_manifest)],
                    workspace_root,
                    timeout=120,
                ),
                run_command(
                    "source-revision-checker",
                    [sys.executable, str(path(workspace_root, "knowledge-base/skills/packages/meta-wearables-source-refresh/scripts/check_source_revisions.py")), str(surface_manifest)],
                    workspace_root,
                    timeout=120,
                ),
            ]
        )
    else:
        checks.append(not_run("live-source-checks", "pass --live-source to contact the official public refs"))

    if args.ios_dat_checkout:
        checks.extend(run_ios_typechecks(workspace_root, args.ios_dat_checkout.resolve()))
    else:
        checks.append(not_run("ios-typechecks", "pass --ios-dat-checkout with a selected DAT iOS checkout to typecheck the four portable starters"))

    failed = [check["label"] for check in checks if check["status"] == "failed"]
    unavailable_checks = [check["label"] for check in checks if check["status"] == "unavailable"]
    not_run_checks = [check["label"] for check in checks if check["status"] == "not-run"]
    receipt = {
        "receipt_version": 1,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "suite": "meta-wearables-static-fixtures",
        "workspace_root_label": workspace_root.name,
        "status": "failed" if failed else "pass",
        "evidence_level": "source/static/mock",
        "checks": checks,
        "failed_checks": failed,
        "unavailable_checks": unavailable_checks,
        "not_run_checks": not_run_checks,
        "proves": [
            "the reusable domain, Web App, Android target-preflight, manifest, recipe, target-intake, and full-route fixture checks were exercised when available",
            "optional iOS starter typechecks were exercised only when an explicit DAT iOS simulator checkout was supplied",
        ],
        "does_not_prove": [
            "authenticated Developer Center or Meta AI account state",
            "connected or physical glasses behavior, firmware, optics, audio, Display, sensors, or thermal behavior",
            "Gen 2/Gen 3 support or a runtime mapping for the Meta Glasses product line",
            "signed artifacts, release channels, App Store/Play eligibility, or production delivery",
        ],
        "next_gate": "resolve any failed checks, then run target-specific preflight and the named connected/physical proof script",
    }
    if args.as_json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(f"FIXTURE_SUITE status={receipt['status']} checks={len(checks)} failed={len(failed)} unavailable={len(unavailable_checks)} not_run={len(not_run_checks)}")
        for check in checks:
            print(f"CHECK {check['label']} {check['status']}")
            for line in check.get("output_tail", []):
                print(f"  {line}")
        print(f"NEXT {receipt['next_gate']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
