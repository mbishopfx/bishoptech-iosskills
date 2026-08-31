#!/usr/bin/env python3
"""Emit a redacted, reproducible Android DAT target-preflight receipt.

This runner inventories an Android/Gradle target without publishing, signing,
cleaning, resolving dependencies, or printing credential values. It reports
the target-owned build graph, DAT coordinates, SDK/toolchain presence, manifest
configuration, and current 0.9 migration markers. Static inventory is not an
Android compile, connected-device result, physical-glasses result, or release
proof.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXCLUDED_PARTS = {".git", ".gradle", "build", "node_modules", "__pycache__"}
SOURCE_SUFFIXES = {".kt", ".java", ".kts", ".gradle", ".xml", ".properties", ".toml"}
PUBLIC_DAT_GROUP = "com.meta.wearable"
SECRET_KEY_RE = re.compile(r"(?i)(token|password|secret|private[_-]?key)")
VERSION_RE = re.compile(r"(?P<key>agp|kotlin|mwdat)\s*=\s*[\"'](?P<value>[^\"']+)")
SDK_RE = re.compile(r"(?P<key>compileSdk|minSdk|targetSdk)\s*=\s*(?P<value>\d+)")
JAVA_RE = re.compile(r"(?:VERSION_|JVM_)(?P<value>\d+)")
DAT_COORDINATE_RE = re.compile(
    r"com\.meta\.wearable:mwdat-(?P<artifact>[A-Za-z0-9_-]+)(?::(?P<version>[A-Za-z0-9_.-]+))?"
)
CATALOG_ARTIFACT_RE = re.compile(r"name\s*=\s*[\"'](?P<artifact>mwdat-[A-Za-z0-9_-]+)[\"']")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target_root", type=Path, help="actual Android/Gradle target root")
    parser.add_argument("--module", default="app", help="Gradle module name, with or without a leading colon")
    parser.add_argument("--variant", default="debug", help="variant used for the eventual dependency/build gate")
    parser.add_argument(
        "--route",
        default="native-dat-android",
        choices=("native-dat-android", "native-display", "phone-fallback"),
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def excluded(path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.parts)


def relative_path(root: Path, value: Path) -> str:
    try:
        return value.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return value.name


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def first_file(root: Path, names: tuple[str, ...]) -> Path | None:
    for name in names:
        candidate = root / name
        if candidate.is_file():
            return candidate
    return None


def module_path(root: Path, module: str) -> Path:
    normalized = module.strip().lstrip(":")
    return root.joinpath(*normalized.split(":"))


def source_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix in SOURCE_SUFFIXES and not excluded(path)
    )


def version_inventory(texts: list[str]) -> dict[str, str | None]:
    result: dict[str, str | None] = {"agp": None, "kotlin": None, "mwdat": None}
    for text in texts:
        for match in VERSION_RE.finditer(text):
            result.setdefault(match.group("key"), match.group("value"))
            if result.get(match.group("key")) is None:
                result[match.group("key")] = match.group("value")
    return result


def sdk_inventory(texts: list[str]) -> dict[str, int | None]:
    result: dict[str, int | None] = {"compileSdk": None, "minSdk": None, "targetSdk": None}
    for text in texts:
        for match in SDK_RE.finditer(text):
            key = match.group("key")
            if result[key] is None:
                result[key] = int(match.group("value"))
    return result


def java_inventory(texts: list[str]) -> dict[str, list[int]]:
    values = sorted({int(match.group("value")) for text in texts for match in JAVA_RE.finditer(text)})
    return {"declared_versions": values}


def artifact_inventory(texts: list[str], version: str | None) -> list[dict[str, str | None]]:
    names: set[str] = set()
    for text in texts:
        names.update(match.group("artifact") for match in DAT_COORDINATE_RE.finditer(text))
        names.update(match.group("artifact") for match in CATALOG_ARTIFACT_RE.finditer(text))
    return [
        {"group": PUBLIC_DAT_GROUP, "artifact": name, "version": version}
        for name in sorted(names)
    ]


def repository_inventory(texts: list[str]) -> dict[str, bool]:
    combined = "\n".join(texts)
    return {
        "github_packages_repository_present": "maven.pkg.github.com/facebook/meta-wearables-dat-android" in combined,
        "google_repository_present": "google()" in combined,
        "maven_central_present": "mavenCentral()" in combined,
    }


def credential_presence(root: Path) -> dict[str, bool]:
    local_properties = root / "local.properties"
    local_text = read_text(local_properties) if local_properties.is_file() else ""
    return {
        "github_token_environment_present": bool(os.environ.get("GITHUB_TOKEN")),
        "local_properties_present": local_properties.is_file(),
        "github_token_key_present_in_local_properties": bool(re.search(r"(?im)^\s*github_token\s*=", local_text)),
        "developer_values_present_in_local_properties": bool(
            re.search(r"(?im)^\s*mwdat_(?:application_id|client_token)\s*=", local_text)
        ),
        "credential_values_omitted": True,
    }


def java_runtime() -> dict[str, Any]:
    java_path = shutil.which("java")
    if not java_path:
        return {"present": False, "version": None, "major": None}
    try:
        completed = subprocess.run(
            [java_path, "-version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {"present": True, "version": None, "major": None}
    first_line = next(
        (line.strip() for line in (completed.stderr + "\n" + completed.stdout).splitlines() if line.strip()),
        "",
    )
    match = re.search(r'version\s+[\"\'](?P<version>[^\"\']+)', first_line)
    version = match.group("version") if match else None
    major_match = re.match(r"(?P<major>\d+)", version or "")
    return {
        "present": True,
        "version": version,
        "major": int(major_match.group("major")) if major_match else None,
    }


def manifest_inventory(root: Path, module_root: Path) -> dict[str, Any]:
    manifests = sorted(
        path for path in module_root.rglob("AndroidManifest.xml") if path.is_file() and not excluded(path)
    )
    metadata: set[str] = set()
    permissions: set[str] = set()
    obsolete: set[str] = set()
    for manifest in manifests:
        text = read_text(manifest)
        metadata.update(re.findall(r"com\.meta\.wearable\.mwdat\.[A-Z0-9_]+", text))
        permissions.update(re.findall(r"android\.permission\.[A-Z0-9_]+", text))
        if "DAM_ENABLED" in text:
            obsolete.add("DAM_ENABLED")
    return {
        "paths": [relative_path(root, path) for path in manifests],
        "meta_metadata_keys": sorted(metadata),
        "permissions": sorted(permissions),
        "obsolete_keys_present": sorted(obsolete),
    }


def source_marker_inventory(root: Path, module_root: Path) -> dict[str, Any]:
    paths = source_files(module_root)
    contents = "\n".join(read_text(path) for path in paths)
    markers = {
        "device_session": "DeviceSession" in contents,
        "add_camera": ".addCamera" in contents or "addCamera(" in contents,
        "camera_stream": ".stream" in contents and "Camera" in contents,
        "add_display": ".addDisplay" in contents or "addDisplay(" in contents,
        "dat_result": "DatResult" in contents or ".fold(" in contents or ".onSuccess" in contents,
        "flow": "kotlinx.coroutines.flow" in contents or ".collect" in contents,
        "removed_add_stream": "addStream(" in contents,
        "obsolete_display_component": "DisplayComponent" in contents,
        "obsolete_dam_key": "DAM_ENABLED" in contents,
    }
    return {
        "source_file_count": len(paths),
        "source_paths": [relative_path(root, path) for path in paths],
        "markers": markers,
    }


def toolchain_inventory(root: Path) -> dict[str, Any]:
    sdk_candidates: list[str] = []
    for key in ("ANDROID_SDK_ROOT", "ANDROID_HOME"):
        if os.environ.get(key):
            sdk_candidates.append(key)
    local_properties = root / "local.properties"
    if local_properties.is_file() and re.search(r"(?im)^\s*sdk\.dir\s*=", read_text(local_properties)):
        sdk_candidates.append("local.properties:sdk.dir")
    wrapper_properties = root / "gradle/wrapper/gradle-wrapper.properties"
    wrapper_text = read_text(wrapper_properties)
    java = java_runtime()
    return {
        "java_present": java["present"],
        "java_version": java["version"],
        "java_major": java["major"],
        "declared_jvm_target": 17,
        "javac_present": shutil.which("javac") is not None,
        "gradle_present": shutil.which("gradle") is not None,
        "adb_present": shutil.which("adb") is not None,
        "kotlinc_present": shutil.which("kotlinc") is not None,
        "sdkmanager_present": shutil.which("sdkmanager") is not None,
        "android_sdk_signal_present": bool(sdk_candidates),
        "android_sdk_signal_sources": sdk_candidates,
        "gradle_wrapper_script_present": (root / "gradlew").is_file(),
        "gradle_wrapper_jar_present": (root / "gradle/wrapper/gradle-wrapper.jar").is_file(),
        "gradle_wrapper_distribution": re.search(r"distributionUrl=(.+)", wrapper_text).group(1)
        if re.search(r"distributionUrl=(.+)", wrapper_text)
        else None,
    }


def main() -> int:
    args = parse_args()
    root = args.target_root.resolve()
    if not root.is_dir():
        raise SystemExit(f"target root is not a directory: {root}")

    module = args.module if args.module.startswith(":") else f":{args.module}"
    module_root = module_path(root, module)
    settings_path = first_file(root, ("settings.gradle.kts", "settings.gradle"))
    root_build_path = first_file(root, ("build.gradle.kts", "build.gradle"))
    module_build_path = first_file(module_root, ("build.gradle.kts", "build.gradle")) if module_root.is_dir() else None
    manifest = manifest_inventory(root, module_root) if module_root.is_dir() else {
        "paths": [],
        "meta_metadata_keys": [],
        "permissions": [],
        "obsolete_keys_present": [],
    }
    files = source_files(root)
    relevant_texts = [
        read_text(path)
        for path in (settings_path, root_build_path, module_build_path, root / "gradle/libs.versions.toml")
        if path and path.is_file()
    ]
    versions = version_inventory(relevant_texts)
    sdk_levels = sdk_inventory(relevant_texts)
    artifacts = artifact_inventory(relevant_texts, versions.get("mwdat"))
    source_markers = source_marker_inventory(root, module_root) if module_root.is_dir() else {
        "source_file_count": 0,
        "source_paths": [],
        "markers": {},
    }
    tools = toolchain_inventory(root)
    static_checks = {
        "settings_gradle_present": settings_path is not None,
        "root_build_file_present": root_build_path is not None,
        "module_directory_present": module_root.is_dir(),
        "module_build_file_present": module_build_path is not None,
        "manifest_present": bool(manifest["paths"]),
        "dat_artifact_declared": bool(artifacts),
        "github_packages_repository_present": repository_inventory(relevant_texts)[
            "github_packages_repository_present"
        ],
    }
    static_pass = all(static_checks.values())
    required_artifacts = {"mwdat-core", "mwdat-camera", "mwdat-display", "mwdat-mockdevice"}
    declared_artifacts = {str(row["artifact"]) for row in artifacts}
    missing_artifacts = sorted(required_artifacts - declared_artifacts)
    receipt = {
        "receipt_version": 1,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if static_pass else "fail",
        "evidence_level": "static",
        "route": args.route,
        "target_root_label": root.name,
        "module": module,
        "variant": args.variant,
        "build_graph": {
            "settings": relative_path(root, settings_path) if settings_path else None,
            "root_build": relative_path(root, root_build_path) if root_build_path else None,
            "module_build": relative_path(root, module_build_path) if module_build_path else None,
            "gradle_version": versions.get("agp"),
            "kotlin_version": versions.get("kotlin"),
            "mwdat_version": versions.get("mwdat"),
            "sdk_levels": sdk_levels,
            "java": java_inventory(relevant_texts),
            "artifacts": artifacts,
            "missing_full_surface_artifacts": missing_artifacts,
            "repositories": repository_inventory(relevant_texts),
        },
        "toolchain": tools,
        "credentials": credential_presence(root),
        "manifest": manifest,
        "source_markers": source_markers,
        "checks": {
            key: {"status": "pass" if value else "fail"}
            for key, value in static_checks.items()
        },
        "dependency_graph": {
            "status": "not-run",
            "configuration": f"{module}{args.variant.capitalize()}CompileClasspath",
            "resolved_artifacts": [],
            "reason": "Run the selected Gradle dependency report on a provisioned target; no resolution is performed by this static runner.",
        },
        "proves": [
            "the target-owned Gradle files, module, manifest, and declared DAT route are present"
        ]
        if static_pass
        else [],
        "does_not_prove": [
            "resolved Maven artifacts, Kotlin/Java compilation, R8 behavior, or a signed Android artifact",
            "registration, account, runtime DeviceType, firmware, companion, or permission state",
            "connected or physical glasses camera, audio, Display, input, sensor, latency, comfort, or thermal behavior",
            "Gen 2 or Gen 3 support beyond a later named-device evidence packet",
            "release-channel or production delivery",
        ],
        "next_gate": (
            f"run ./gradlew --version, {module}:properties, dependencies, and dependencyInsight on a provisioned target; then compile the selected variant"
            if static_pass
            else "repair the missing target-owned Gradle/module/manifest/repository inputs before dependency or build work"
        ),
    }
    if args.as_json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(
            f"ANDROID_TARGET_PREFLIGHT status={receipt['status']} evidence={receipt['evidence_level']} "
            f"target={root.name} module={module} variant={args.variant}"
        )
        print(f"DAT_VERSION {versions.get('mwdat') or 'not-found'}")
        print(f"ARTIFACTS {', '.join(sorted(declared_artifacts)) or 'none'}")
        print(
            "TOOLCHAIN "
            + ",".join(
                key
                for key in ("java_present", "gradle_present", "adb_present", "android_sdk_signal_present")
                if tools[key]
            )
            or "none"
        )
        print(f"MISSING_FULL_SURFACE {', '.join(missing_artifacts) or 'none'}")
        print(f"NEXT {receipt['next_gate']}")
    return 0 if static_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
