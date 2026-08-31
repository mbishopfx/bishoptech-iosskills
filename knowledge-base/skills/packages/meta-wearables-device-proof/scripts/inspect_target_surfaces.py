#!/usr/bin/env python3
"""Inspect a workspace for concrete iOS, Android, and Web App targets.

This structural scan is intentionally separate from build and device proof.
It chooses bootstrap versus target-specific preflight without authenticating,
opening a project, or making a capability claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


IGNORED_DIRS = {
    ".build",
    ".git",
    ".gradle",
    "DerivedData",
    "build",
    "dist",
    "node_modules",
    "Pods",
    "vendor",
}

# The knowledge base keeps copyable Swift/Web App starters inside skill
# packages. They are assets and fixtures, not a concrete implementation target.
# Scan a real sibling app by passing its directory as --target-root to the
# team preflight runner.
IGNORED_PATH_PREFIXES = {
    ("knowledge-base", "skills", "packages"),
}


def is_ignored(path: Path, root: Path) -> bool:
    relative_parts = path.relative_to(root).parts
    if any(part in IGNORED_DIRS for part in relative_parts):
        return True
    return any(relative_parts[:len(prefix)] == prefix for prefix in IGNORED_PATH_PREFIXES)


def iter_entries(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if is_ignored(path, root):
            continue
        yield path


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def collect(entries: list[Path], root: Path, names: set[str] | None = None, suffixes: set[str] | None = None) -> list[str]:
    return sorted(
        relative(path, root)
        for path in entries
        if (names is None or path.name in names)
        and (suffixes is None or path.suffix in suffixes)
    )


def status(*groups: list[str]) -> str:
    if any(groups):
        return "present" if all(groups) else "partial"
    return "missing"


def inspect(root: Path) -> dict[str, object]:
    entries = list(iter_entries(root))
    files = [path for path in entries if path.is_file()]

    ios_projects = collect(entries, root, suffixes={".xcodeproj", ".xcworkspace"})
    ios_packages = collect(files, root, names={"Package.swift"})
    ios_resolved = collect(files, root, names={"Package.resolved"})
    ios_privacy = collect(files, root, names={"PrivacyInfo.xcprivacy"})
    ios_swift = collect(files, root, suffixes={".swift"})
    ios = {
        "status": status(ios_projects),
        "implementation_target": bool(ios_projects),
        "signals": {
            "projects": ios_projects[:12],
            "package_manifests": ios_packages[:12],
            "resolved_dependencies": ios_resolved[:12],
            "privacy_manifests": ios_privacy[:12],
            "swift_sources": ios_swift[:12],
        },
        "next_gate": "xcodebuild -showBuildSettings plus target-preflight" if ios_projects else "identify or create an Xcode target before implementation",
    }

    android_settings = collect(files, root, names={"settings.gradle", "settings.gradle.kts"})
    android_builds = collect(files, root, names={"build.gradle", "build.gradle.kts"})
    android_wrapper = collect(files, root, names={"gradlew", "gradlew.bat"})
    android_manifests = collect(files, root, names={"AndroidManifest.xml"})
    android_sources = collect(files, root, suffixes={".kt", ".java"})
    android = {
        "status": status(android_settings, android_builds),
        "implementation_target": bool(android_settings and android_builds),
        "signals": {
            "settings": android_settings[:12],
            "build_scripts": android_builds[:12],
            "gradle_wrappers": android_wrapper[:12],
            "manifests": android_manifests[:12],
            "kotlin_java_sources": android_sources[:12],
        },
        "next_gate": "Gradle dependency/configuration inspection plus target-preflight" if android_settings and android_builds else "identify or create a Gradle Android target before implementation",
    }

    web_entrypoints = collect(files, root, names={"index.html"})
    web_manifests = collect(files, root, names={"package.json"})
    web_sources = collect(files, root, suffixes={".html", ".js", ".jsx", ".ts", ".tsx"})
    web = {
        "status": "present" if web_entrypoints else ("partial" if web_manifests or web_sources else "missing"),
        "implementation_target": bool(web_entrypoints),
        "signals": {
            "html_entrypoints": web_entrypoints[:12],
            "package_manifests": web_manifests[:12],
            "web_sources": web_sources[:12],
        },
        "next_gate": "resolve hosted HTTPS revision and Web App preflight" if web_entrypoints else "identify or create a Web App entrypoint before implementation",
    }

    surfaces = {"ios": ios, "android": android, "web_app": web}
    configured = [name for name, data in surfaces.items() if data["implementation_target"]]
    partial = [name for name, data in surfaces.items() if data["status"] == "partial"]
    if configured:
        overall = "TARGETS_PRESENT"
        next_action = "Freeze the target tuple, run source checks, then run target-preflight."
    elif partial:
        overall = "TARGETS_PARTIAL"
        next_action = "Use the project bootstrap packet; partial files are not an implementation target."
    else:
        overall = "NO_TARGET"
        next_action = "Use the project bootstrap packet and create a sibling implementation project."

    return {
        "root": str(root),
        "overall": overall,
        "implementation_target": bool(configured),
        "bootstrap_required": not bool(configured),
        "configured_surfaces": configured,
        "partial_surfaces": partial,
        "surfaces": surfaces,
        "next_action": next_action,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--require-target", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        raise SystemExit(f"workspace root is not a directory: {root}")

    result = inspect(root)
    if args.as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"ROOT {result['root']}")
        print(f"OVERALL {result['overall']} IMPLEMENTATION_TARGET {str(result['implementation_target']).lower()} BOOTSTRAP_REQUIRED {str(result['bootstrap_required']).lower()}")
        for name, data in result["surfaces"].items():
            print(f"SURFACE {name} STATUS {data['status']} TARGET {str(data['implementation_target']).lower()}")
            for signal_name, values in data["signals"].items():
                if values:
                    print(f"  {signal_name}={','.join(values)}")
            print(f"  next_gate={data['next_gate']}")
        print(f"NEXT {result['next_action']}")

    if args.require_target and not result["implementation_target"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
