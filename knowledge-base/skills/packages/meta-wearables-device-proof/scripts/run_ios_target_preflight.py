#!/usr/bin/env python3
"""Emit a redacted, reproducible iOS target preflight receipt.

This runner inventories an Xcode project/workspace, optionally resolves the
selected scheme's safe build settings, and can run an explicitly requested
test destination. It never prints raw xcodebuild output or credential-bearing
settings, and it never upgrades build evidence to connected or physical proof.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXCLUDED_PARTS = {".git", ".build", "build", "DerivedData", "Pods", "node_modules"}
SAFE_BUILD_SETTINGS = (
    "CODE_SIGN_ENTITLEMENTS",
    "CODE_SIGN_STYLE",
    "CONFIGURATION",
    "CURRENT_PROJECT_VERSION",
    "INFOPLIST_FILE",
    "IPHONEOS_DEPLOYMENT_TARGET",
    "MARKETING_VERSION",
    "SDKROOT",
    "SWIFT_DEFAULT_ACTOR_ISOLATION",
    "SWIFT_STRICT_CONCURRENCY",
    "SWIFT_VERSION",
    "TARGETED_DEVICE_FAMILY",
)
META_PACKAGE_MARKER = "meta-wearables"
TEST_SUMMARY_RE = re.compile(r"Test run with\s+(\d+)\s+tests?\s+in\s+(\d+)\s+suites?\s+passed", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target_root", type=Path, help="actual Xcode project/workspace root")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--project", type=Path, help="relative or absolute .xcodeproj path")
    group.add_argument("--workspace", type=Path, help="relative or absolute .xcworkspace path")
    parser.add_argument("--scheme", help="scheme to inspect and/or test")
    parser.add_argument("--configuration", default="Debug")
    parser.add_argument("--destination", help="required with --test; use an explicit simulator or device destination")
    parser.add_argument("--route", default="native-dat-ios", choices=("native-dat-ios", "native-display", "phone-fallback"))
    parser.add_argument("--test", action="store_true", help="run xcodebuild test after static inspection")
    parser.add_argument("--derived-data-path", type=Path, help="optional explicit DerivedData path for --test")
    parser.add_argument("--result-bundle-path", type=Path, help="optional explicit result bundle path for --test")
    parser.add_argument("--skip-package-updates", action="store_true", help="pass -skipPackageUpdates to xcodebuild test")
    parser.add_argument("--disable-automatic-package-resolution", action="store_true", help="pass -disableAutomaticPackageResolution to xcodebuild test")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def excluded(path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.parts)


def resolve_path(root: Path, value: Path) -> Path:
    return value.resolve() if value.is_absolute() else (root / value).resolve()


def relative_path(root: Path, value: Path) -> str:
    try:
        return value.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return value.name


def find_single(root: Path, suffix: str) -> Path:
    candidates = sorted(path for path in root.rglob(f"*{suffix}") if path.is_dir() and not excluded(path))
    if len(candidates) != 1:
        found = ", ".join(path.name for path in candidates) or "none"
        raise ValueError(f"expected exactly one {suffix} under target root; found {found}; pass --project or --workspace")
    return candidates[0]


def container_arguments(container: Path) -> list[str]:
    command: list[str] = []
    if container.suffix == ".xcodeproj":
        command.extend(["-project", str(container)])
    else:
        command.extend(["-workspace", str(container)])
    return command


def run_command(command: list[str], cwd: Path) -> tuple[int | None, str, str | None]:
    try:
        completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    except OSError as error:
        return None, "", str(error)
    return completed.returncode, completed.stdout, completed.stderr


def parse_json_output(raw: str) -> Any:
    raw = raw.strip()
    if not raw:
        raise ValueError("xcodebuild returned empty JSON output")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        starts = [index for index, char in enumerate(raw) if char in "[{]"]
        for start in starts:
            try:
                return json.loads(raw[start:])
            except json.JSONDecodeError:
                continue
        raise ValueError("xcodebuild JSON output could not be parsed")


def list_inventory(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {"projects": [], "targets": [], "schemes": [], "configurations": []}
    containers = []
    for key in ("project", "workspace"):
        value = data.get(key)
        if isinstance(value, dict):
            containers.append(value)
    if not containers:
        containers = [data]

    def values(key: str) -> list[str]:
        result: set[str] = set()
        for container in containers:
            value = container.get(key, [])
            if isinstance(value, list):
                result.update(str(item) for item in value)
        return sorted(result)

    return {
        "projects": values("projects"),
        "targets": values("targets"),
        "schemes": values("schemes"),
        "configurations": values("configurations"),
    }


def safe_settings(data: Any) -> list[dict[str, Any]]:
    rows = data if isinstance(data, list) else [data]
    result = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        settings = row.get("buildSettings")
        if not isinstance(settings, dict):
            continue
        selected: dict[str, Any] = {}
        for key in SAFE_BUILD_SETTINGS:
            if key not in settings:
                continue
            value = settings[key]
            if key == "SDKROOT":
                value = os.path.basename(str(value))
            selected[key] = value
        selected["bundle_identifier_present"] = bool(settings.get("PRODUCT_BUNDLE_IDENTIFIER"))
        selected["credential_values_omitted"] = True
        result.append({"target": row.get("target"), "settings": selected})
    return result


def package_lock_inventory(root: Path) -> list[dict[str, Any]]:
    result = []
    seen: set[str] = set()
    for lockfile in sorted(path for path in root.rglob("Package.resolved") if path.is_file() and not excluded(path)):
        try:
            data = json.loads(lockfile.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        pins = data.get("pins") or data.get("object", {}).get("pins", [])
        meta_pins = []
        for pin in pins if isinstance(pins, list) else []:
            if not isinstance(pin, dict):
                continue
            identity = str(pin.get("identity") or pin.get("package") or "")
            location = str(pin.get("location") or "")
            if META_PACKAGE_MARKER not in f"{identity} {location}".lower():
                continue
            state = pin.get("state", {}) if isinstance(pin.get("state"), dict) else {}
            meta_pins.append(
                {
                    "identity": identity,
                    "version": state.get("version"),
                    "revision": state.get("revision"),
                }
            )
        key = relative_path(root, lockfile)
        if key in seen:
            continue
        seen.add(key)
        result.append({"path": key, "meta_pins": meta_pins})
    return result


def target_files(root: Path, settings_rows: list[dict[str, Any]]) -> dict[str, Any]:
    info_paths: set[str] = set()
    entitlement_paths: set[str] = set()
    for row in settings_rows:
        settings = row.get("settings", {})
        if settings.get("INFOPLIST_FILE"):
            path = root / str(settings["INFOPLIST_FILE"])
            if path.is_file():
                info_paths.add(relative_path(root, path))
        if settings.get("CODE_SIGN_ENTITLEMENTS"):
            path = root / str(settings["CODE_SIGN_ENTITLEMENTS"])
            if path.is_file():
                entitlement_paths.add(relative_path(root, path))
    privacy_paths = {
        relative_path(root, path)
        for path in root.rglob("PrivacyInfo.xcprivacy")
        if path.is_file() and not excluded(path)
    }
    return {
        "info_plists": sorted(info_paths),
        "entitlements": sorted(entitlement_paths),
        "privacy_manifests": sorted(privacy_paths),
    }


def run_test(args: argparse.Namespace, root: Path, container: Path) -> dict[str, Any]:
    command = ["xcodebuild", "test"] + container_arguments(container)
    command.extend(["-scheme", args.scheme, "-configuration", args.configuration, "-destination", args.destination])
    if args.derived_data_path:
        command.extend(["-derivedDataPath", str(resolve_path(root, args.derived_data_path))])
    if args.result_bundle_path:
        command.extend(["-resultBundlePath", str(resolve_path(root, args.result_bundle_path))])
    if args.skip_package_updates:
        command.append("-skipPackageUpdates")
    if args.disable_automatic_package_resolution:
        command.append("-disableAutomaticPackageResolution")
    returncode, stdout, stderr = run_command(command, root)
    combined = "\n".join(part for part in (stdout, stderr) if part)
    match = TEST_SUMMARY_RE.search(combined)
    result: dict[str, Any] = {
        "requested": True,
        "status": "pass" if returncode == 0 else "fail",
        "returncode": returncode,
        "success_marker": "** TEST SUCCEEDED **" in combined,
        "test_count": int(match.group(1)) if match else None,
        "suite_count": int(match.group(2)) if match else None,
        "result_bundle_created": bool(args.result_bundle_path and resolve_path(root, args.result_bundle_path).exists()),
    }
    if returncode is None:
        result["failure"] = "xcodebuild could not be executed"
    elif returncode != 0:
        result["failure"] = "xcodebuild test failed; inspect the local redacted build log"
    return result


def main() -> int:
    args = parse_args()
    if args.test and (not args.scheme or not args.destination):
        raise SystemExit("--test requires both --scheme and --destination")

    root = args.target_root.resolve()
    if not root.is_dir():
        raise SystemExit(f"target root is not a directory: {root}")
    if args.project or args.workspace:
        container = resolve_path(root, args.project or args.workspace)
    else:
        container = find_single(root, ".xcodeproj")
    if not container.is_dir() or container.suffix not in {".xcodeproj", ".xcworkspace"}:
        raise SystemExit(f"Xcode project/workspace not found: {container}")

    list_returncode, list_stdout, _ = run_command(["xcodebuild", "-list", "-json"] + container_arguments(container), root)
    list_ok = list_returncode == 0
    inventory: dict[str, Any] = {"projects": [], "targets": [], "schemes": [], "configurations": []}
    list_error = None
    if list_ok:
        try:
            inventory = list_inventory(parse_json_output(list_stdout))
        except ValueError as error:
            list_ok = False
            list_error = str(error)
    elif list_returncode is None:
        list_error = "xcodebuild could not be executed"
    else:
        list_error = f"xcodebuild -list failed with exit code {list_returncode}"

    settings_rows: list[dict[str, Any]] = []
    settings_ok = None
    settings_error = None
    if args.scheme:
        settings_command = ["xcodebuild", "-showBuildSettings", "-json"] + container_arguments(container)
        settings_command.extend(["-scheme", args.scheme, "-configuration", args.configuration])
        settings_returncode, settings_stdout, _ = run_command(settings_command, root)
        settings_ok = settings_returncode == 0
        if settings_ok:
            try:
                settings_rows = safe_settings(parse_json_output(settings_stdout))
            except ValueError as error:
                settings_ok = False
                settings_error = str(error)
        elif settings_returncode is None:
            settings_error = "xcodebuild could not be executed"
        else:
            settings_error = f"xcodebuild -showBuildSettings failed with exit code {settings_returncode}"
    else:
        settings_error = "not run; pass --scheme for scheme settings"

    test_result = {"requested": False, "status": "not-run"}
    if args.test:
        test_result = run_test(args, root, container)

    version_returncode, version_stdout, _ = run_command(["xcodebuild", "-version"], root)
    xcode_version = [line.strip() for line in version_stdout.splitlines() if line.strip()][:2] if version_returncode == 0 else []
    files = target_files(root, settings_rows)
    package_locks = package_lock_inventory(root)

    overall_pass = list_ok and (settings_ok is not False) and (not args.test or test_result.get("status") == "pass")
    proofs = [
        "the selected Xcode project/workspace inventory is present",
        "the selected scheme's redacted build settings resolved" if settings_ok else "scheme build settings were not resolved",
    ]
    if args.test and test_result.get("status") == "pass":
        proofs.append("the selected scheme passed xcodebuild test at the explicitly named destination")
    receipt = {
        "receipt_version": 1,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if overall_pass else "fail",
        "evidence_level": "build" if args.test and test_result.get("status") == "pass" else "static",
        "route": args.route,
        "target_root_label": root.name,
        "container": relative_path(root, container),
        "scheme": args.scheme,
        "configuration": args.configuration if args.scheme else None,
        "xcode_version": xcode_version,
        "inventory": inventory,
        "checks": {
            "xcodebuild_list": {"status": "pass" if list_ok else "fail", "error": list_error},
            "show_build_settings": {
                "status": "pass" if settings_ok else ("not-run" if settings_ok is None else "fail"),
                "error": settings_error,
                "rows": settings_rows,
            },
            "package_resolved": package_locks,
            "target_files": files,
            "test": test_result,
        },
        "proves": proofs,
        "does_not_prove": [
            "connected registration, runtime DeviceType, firmware, companion, or account readiness",
            "physical glasses camera, audio, Display, input, sensor, latency, comfort, or thermal behavior",
            "Gen 2 or Gen 3 support beyond the exact target and evidence level recorded here",
            "signed, release-channel, App Store, or production delivery",
        ],
        "next_gate": (
            "capture the named connected-device tuple and run the physical capability script"
            if overall_pass and args.test
            else "run an explicit --scheme/--test receipt before connected or physical evidence"
        ),
    }
    if args.as_json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(
            f"IOS_TARGET_PREFLIGHT status={receipt['status']} evidence={receipt['evidence_level']} "
            f"target={root.name} scheme={args.scheme or 'not-run'}"
        )
        print(f"XCODE {' '.join(xcode_version) if xcode_version else 'not-found'}")
        print(f"TARGETS {', '.join(inventory['targets']) or 'none'}")
        print(f"DAT_LOCKS {sum(len(item['meta_pins']) for item in package_locks)}")
        if args.test:
            print(f"TEST {test_result.get('status')} count={test_result.get('test_count')} suites={test_result.get('suite_count')}")
        print(f"NEXT {receipt['next_gate']}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
