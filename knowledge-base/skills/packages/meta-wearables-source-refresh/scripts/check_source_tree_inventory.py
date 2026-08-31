#!/usr/bin/env python3
"""Check the pinned Meta Wearables repository/package tree inventory."""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import tarfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

import yaml


USER_AGENT = "bishoptech-iosskills-meta-source-refresh/1.0"
EXPECTED_IOS_PRODUCTS = {
    "MWDATCore",
    "MWDATCamera",
    "MWDATDisplay",
    "MWDATMockDevice",
    "MWDATMockDeviceTestClient",
}
EXPECTED_AI_ROOT_FILES = ["AGENTS.md", "README.md", "install-skills.sh"]
ARCHIVE_CACHE: dict[tuple[str, str], list[dict]] = {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", type=Path, help="path to the source-pinned surface manifest")
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout in seconds")
    return parser.parse_args()


def default_manifest_path() -> Path:
    candidates = (
        Path.cwd() / "knowledge-base" / "skills" / "packages" / "meta-wearables-full-sdk-audit" / "references" / "surface-manifest.yaml",
        Path(__file__).resolve().parents[2] / "meta-wearables-full-sdk-audit" / "references" / "surface-manifest.yaml",
    )
    return next((candidate for candidate in candidates if candidate.is_file()), candidates[0])


def fetch(url: str, timeout: float) -> bytes:
    request = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def raw_file(repository: str, revision: str, path: str, timeout: float) -> str:
    owner, repo = urlsplit(repository).path.strip("/").split("/")[:2]
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{revision}/{path}"
    return fetch(url, timeout).decode("utf-8")


def api_directory(repository: str, revision: str, path: str, timeout: float) -> list[dict]:
    owner, repo = urlsplit(repository).path.strip("/").split("/")[:2]
    encoded_path = quote(path.strip("/"), safe="/")
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{encoded_path}?ref={quote(revision, safe='')}"
    try:
        payload = json.loads(fetch(url, timeout).decode("utf-8"))
        if not isinstance(payload, list):
            raise ValueError(f"GitHub contents response is not a directory: {url}")
        return [entry for entry in payload if isinstance(entry, dict)]
    except HTTPError as error:
        if error.code not in {403, 429}:
            raise
        return archive_directory(repository, revision, path, timeout)


def archive_directory(repository: str, revision: str, path: str, timeout: float) -> list[dict]:
    """List one directory from a read-only GitHub source archive.

    The public Contents API is useful for small directory inventories but is
    rate-limited without credentials. A codeload archive keeps this checker
    credential-free and preserves the same exact-name checks when that API is
    unavailable.
    """
    owner, repo = urlsplit(repository).path.strip("/").split("/")[:2]
    cache_key = (repository, revision)
    members = ARCHIVE_CACHE.get(cache_key)
    if members is None:
        archive_url = f"https://codeload.github.com/{owner}/{repo}/tar.gz/{quote(revision, safe='')}"
        with tarfile.open(fileobj=io.BytesIO(fetch(archive_url, timeout)), mode="r:gz") as archive:
            members = [
                {"name": member.name, "type": "dir" if member.isdir() else "file"}
                for member in archive.getmembers()
                if member.name
            ]
        ARCHIVE_CACHE[cache_key] = members

    root_prefix = members[0]["name"].split("/", 1)[0] + "/"
    relative_path = path.strip("/")
    directory_prefix = root_prefix + (relative_path + "/" if relative_path else "")
    entries: dict[str, dict] = {}
    for member in members:
        member_path = member["name"]
        if not member_path.startswith(directory_prefix):
            continue
        remainder = member_path[len(directory_prefix):].strip("/")
        if not remainder or "/" in remainder:
            continue
        entries[remainder] = {"name": remainder, "type": member["type"]}
    return list(entries.values())


def check(results: list[bool], label: str, observed: object, expected: object) -> None:
    matches = observed == expected
    results.append(matches)
    status = "MATCH" if matches else "DRIFT"
    print(f"{status} {label} expected={expected!r} observed={observed!r}")


def plugin_version(repository: str, revision: str, plugin_root: str, timeout: float, plugin_manifest: str | None = None) -> str:
    plugin_path = plugin_manifest or f"{plugin_root.rsplit('/skills', 1)[0]}/.codex-plugin/plugin.json"
    payload = json.loads(raw_file(repository, revision, plugin_path, timeout))
    return str(payload.get("version", ""))


def directory_names(entries: list[dict], entry_type: str | None = None) -> list[str]:
    return sorted(entry["name"] for entry in entries if entry.get("name") and (entry_type is None or entry.get("type") == entry_type))


def main() -> int:
    args = parse_args()
    manifest_path = (args.manifest or default_manifest_path()).resolve()
    if not manifest_path.is_file():
        raise ValueError(f"manifest not found: {manifest_path}")
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("manifest root must be a mapping")

    journeys = {entry.get("id"): entry for entry in data.get("journeys", []) if isinstance(entry, dict)}
    inventory = data.get("source_inventory", {})
    results: list[bool] = []
    ai_surfaces = inventory["ai_surfaces"]

    ios_repo = journeys["native-dat-ios"]["repository"]
    ios_main = journeys["native-dat-ios"]["revision"]
    ios_tag = inventory["ios"]["release_revision"]
    ios_root_files = directory_names(api_directory(ios_repo, ios_main, "", args.timeout), "file")
    check(results, "ios.root_ai_files", [name for name in ios_root_files if name in ai_surfaces["root_files"]], EXPECTED_AI_ROOT_FILES)
    package = raw_file(ios_repo, ios_tag, inventory["ios"]["package_manifest"], args.timeout)
    products = set(re.findall(r"\.library\(\s*name:\s*\"([^\"]+)\"", package, re.DOTALL))
    binaries = {f"{product}.xcframework" for product, _ in re.findall(r"\.binaryTarget\(\s*name:\s*\"([^\"]+)\"\s*,\s*path:\s*\"([^\"]+)\"", package, re.DOTALL)}
    check(results, "ios.package_products", products, EXPECTED_IOS_PRODUCTS)
    check(results, "ios.binary_targets", binaries, set(inventory["ios"]["binary_targets"]))
    check(results, "ios.plugin_version", plugin_version(ios_repo, ios_main, inventory["ios"]["plugin_root"], args.timeout, ai_surfaces["plugin_manifests"]["ios"]), str(inventory["ios"]["plugin_version"]))
    ios_roles = directory_names(api_directory(ios_repo, ios_main, inventory["ios"]["plugin_root"], args.timeout), "dir")
    check(results, "ios.plugin_skill_count", len(ios_roles), int(inventory["ios"]["plugin_skill_count"]))
    check(results, "ios.plugin_skill_roles", ios_roles, sorted(inventory["ios"]["plugin_roles"]))
    ios_samples = directory_names(api_directory(ios_repo, ios_main, "samples", args.timeout), "dir")
    check(results, "ios.sample_roots", [name for name in ios_samples if name in inventory["ios"]["sample_roots"]], sorted(inventory["ios"]["sample_roots"]))
    ios_display_readme = raw_file(ios_repo, ios_main, "samples/DisplayAccess/README.md", args.timeout)
    ios_toolchain = (
        bool(re.search(r"iOS\s+17\.2\+", ios_display_readme)),
        bool(re.search(r"Xcode\s+26\.4\+", ios_display_readme)),
        bool(re.search(r"Swift\s+6\.3\+", ios_display_readme)),
    )
    check(results, "ios.sample_toolchain", ios_toolchain, (True, True, True))

    android_repo = journeys["native-dat-android"]["repository"]
    android_main = journeys["native-dat-android"]["revision"]
    android_inventory = inventory["android"]
    android_root_files = directory_names(api_directory(android_repo, android_main, "", args.timeout), "file")
    check(results, "android.root_ai_files", [name for name in android_root_files if name in ai_surfaces["root_files"]], EXPECTED_AI_ROOT_FILES)
    check(results, "android.plugin_version", plugin_version(android_repo, android_main, android_inventory["plugin_root"], args.timeout, ai_surfaces["plugin_manifests"]["android"]), str(android_inventory["plugin_version"]))
    android_roles = directory_names(api_directory(android_repo, android_main, android_inventory["plugin_root"], args.timeout), "dir")
    check(results, "android.plugin_skill_count", len(android_roles), int(android_inventory["plugin_skill_count"]))
    check(results, "android.plugin_skill_roles", android_roles, sorted(android_inventory["plugin_roles"]))
    android_samples = directory_names(api_directory(android_repo, android_main, "samples", args.timeout), "dir")
    check(results, "android.sample_roots", [name for name in android_samples if name in android_inventory["sample_roots"]], sorted(android_inventory["sample_roots"]))
    android_tomls = "\n".join(raw_file(android_repo, android_main, f"samples/{sample}/gradle/libs.versions.toml", args.timeout) for sample in android_inventory["sample_roots"])
    check(results, "android.dat_version", sorted(set(re.findall(r"mwdat\s*=\s*\"([^\"]+)\"", android_tomls))), ["0.9.0"])
    artifact_names = {f"com.meta.wearable:{name}:0.9.0" for name in set(re.findall(r'name\s*=\s*\"(mwdat-[^\"]+)\"', android_tomls))}
    check(results, "android.sample_dat_artifacts", artifact_names, set(android_inventory["sample_dat_artifacts"]))
    android_build = raw_file(android_repo, android_main, "samples/DisplayAccess/app/build.gradle.kts", args.timeout)
    sdk_tuple = (
        int(re.search(r"minSdk\s*=\s*(\d+)", android_build).group(1)),
        int(re.search(r"compileSdk\s*=\s*(\d+)", android_build).group(1)),
        int(re.search(r"targetSdk\s*=\s*(\d+)", android_build).group(1)),
    )
    check(results, "android.sample_sdk_tuple", sdk_tuple, (int(android_inventory["sample_min_sdk"]), int(android_inventory["sample_compile_sdk"]), int(android_inventory["sample_target_sdk"])))

    web_repo = journeys["web-apps"]["repository"]
    web_main = journeys["web-apps"]["revision"]
    web_inventory = inventory["web_apps"]
    web_root_files = directory_names(api_directory(web_repo, web_main, "", args.timeout), "file")
    check(results, "web_apps.root_ai_files", [name for name in web_root_files if name in ai_surfaces["root_files"]], EXPECTED_AI_ROOT_FILES)
    check(results, "web_apps.plugin_version", plugin_version(web_repo, web_main, web_inventory["plugin_root"], args.timeout, ai_surfaces["plugin_manifests"]["web_apps"]), str(web_inventory["plugin_version"]))
    web_roles = directory_names(api_directory(web_repo, web_main, f"{web_inventory['plugin_root']}/skills", args.timeout), "dir")
    check(results, "web_apps.plugin_skill_count", len(web_roles), int(web_inventory["plugin_skill_count"]))
    check(results, "web_apps.plugin_skill_roles", web_roles, sorted(web_inventory["plugin_roles"]))
    web_references = directory_names(api_directory(web_repo, web_main, f"{web_inventory['plugin_root']}/references", args.timeout), "file")
    check(results, "web_apps.reference_files", [name for name in web_references if name in web_inventory["reference_files"]], sorted(web_inventory["reference_files"]))
    web_examples = directory_names(api_directory(web_repo, web_main, "examples", args.timeout), "dir")
    check(results, "web_apps.example_roots", [name for name in web_examples if name in web_inventory["example_roots"]], sorted(web_inventory["example_roots"]))
    web_templates = directory_names(api_directory(web_repo, web_main, "templates", args.timeout), "file")
    check(results, "web_apps.template_assets", [name for name in web_templates if name in web_inventory["template_assets"]], sorted(web_inventory["template_assets"]))

    drift = len(results) - sum(results)
    print(f"CHECKS {len(results)} DRIFT {drift}")
    return 1 if drift else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (HTTPError, URLError, OSError, KeyError, TypeError, ValueError, AttributeError, json.JSONDecodeError, yaml.YAMLError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        raise SystemExit(2)
