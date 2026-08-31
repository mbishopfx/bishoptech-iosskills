#!/usr/bin/env python3
"""Emit a conservative Meta Wearables Web App source/hosting receipt.

The runner distinguishes a generic local web surface from a Meta-marked Web
App, checks the 600x600/metadata contract, optionally syntax-checks referenced
JavaScript, and can perform a read-only HTTPS reachability check. It never
claims Meta AI launch, physical Display behavior, or release readiness.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen


IGNORED_DIRS = {".git", ".next", "build", "dist", "node_modules", "vendor"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)
SIX_HUNDRED_RE = re.compile(r"(?:600\s*[x×]\s*600|600\s*px)", re.IGNORECASE)


class SurfaceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, str] = {}
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "meta" and attributes.get("name"):
            self.meta[attributes["name"].lower()] = attributes.get("content", "")
        if tag.lower() == "script" and attributes.get("src"):
            self.scripts.append(attributes["src"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target_root", type=Path, help="Web App source root")
    parser.add_argument("--entry", type=Path, help="relative or absolute HTML entrypoint; otherwise require one index.html")
    parser.add_argument("--package-json", type=Path, help="optional package.json to inventory")
    parser.add_argument("--origin", help="public URL to check; query and fragment are never retained in the receipt")
    parser.add_argument("--check-origin", action="store_true", help="perform a read-only HEAD request to --origin")
    parser.add_argument("--require-meta-markers", action="store_true", help="fail unless Meta Web App metadata markers are present")
    parser.add_argument("--require-https-origin", action="store_true", help="fail unless --origin is HTTPS and checked successfully")
    parser.add_argument("--node-check", action="store_true", help="run node --check on local JavaScript referenced by the entrypoint")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def ignored(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def resolve_path(root: Path, value: Path) -> Path:
    return value.resolve() if value.is_absolute() else (root / value).resolve()


def relative_path(root: Path, value: Path) -> str:
    try:
        return value.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return value.name


def find_entry(root: Path, explicit: Path | None) -> Path:
    if explicit:
        path = resolve_path(root, explicit)
        if not path.is_file():
            raise ValueError(f"entrypoint not found: {path}")
        return path
    candidates = sorted(path for path in root.rglob("index.html") if path.is_file() and not ignored(path))
    if len(candidates) != 1:
        names = ", ".join(relative_path(root, path) for path in candidates) or "none"
        raise ValueError(f"expected exactly one index.html or pass --entry; found {names}")
    return candidates[0]


def git_revision(root: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    value = completed.stdout.strip()
    return value if completed.returncode == 0 and SHA_RE.fullmatch(value) else None


def package_inventory(root: Path, explicit: Path | None) -> dict[str, object]:
    if explicit:
        path = resolve_path(root, explicit)
    else:
        path = root / "package.json"
    if not path.is_file():
        return {"status": "not-found"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "invalid", "path": relative_path(root, path)}
    return {
        "status": "pass",
        "path": relative_path(root, path),
        "name": data.get("name"),
        "version": data.get("version"),
        "private": bool(data.get("private", False)),
        "script_names": sorted(data.get("scripts", {}).keys()) if isinstance(data.get("scripts"), dict) else [],
    }


def local_scripts(root: Path, entry: Path, sources: list[str]) -> list[dict[str, object]]:
    result = []
    for source in sources:
        parsed = urlsplit(source)
        if parsed.scheme or parsed.netloc:
            result.append({"source": source, "local": False, "status": "external"})
            continue
        path = (entry.parent / unquote(parsed.path)).resolve()
        inside = False
        try:
            path.relative_to(root.resolve())
            inside = True
        except ValueError:
            pass
        result.append(
            {
                "source": source,
                "local": inside,
                "path": relative_path(root, path) if inside else None,
                "status": "present" if inside and path.is_file() else "missing",
            }
        )
    return result


def node_checks(root: Path, scripts: list[dict[str, object]]) -> dict[str, object]:
    local_paths = [item["path"] for item in scripts if item.get("local") and item.get("status") == "present"]
    results = []
    for value in local_paths:
        path = root / str(value)
        try:
            completed = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True, check=False)
        except OSError:
            return {"status": "unavailable", "files": [str(value) for value in local_paths]}
        results.append({"path": str(value), "status": "pass" if completed.returncode == 0 else "fail"})
    failed = any(item["status"] == "fail" for item in results)
    return {"status": "fail" if failed else "pass", "files": results}


def origin_check(origin: str | None, should_check: bool) -> dict[str, object]:
    if not origin:
        return {"status": "not-run"}
    parsed = urlsplit(origin)
    safe = {
        "scheme": parsed.scheme.lower(),
        "host": parsed.hostname,
        "path": parsed.path or "/",
        "query_omitted": bool(parsed.query),
        "fragment_omitted": bool(parsed.fragment),
        "credentials_omitted": bool(parsed.username or parsed.password),
    }
    if parsed.username or parsed.password or not parsed.hostname:
        safe["status"] = "invalid"
        safe["error"] = "origin must have a host and no embedded credentials"
        return safe
    if parsed.scheme.lower() != "https":
        safe["status"] = "insecure"
        safe["error"] = "Meta Web App delivery requires HTTPS"
        return safe
    if not should_check:
        safe["status"] = "provided-not-checked"
        return safe
    try:
        request = Request(origin, method="HEAD", headers={"User-Agent": "meta-wearables-preflight/1"})
        with urlopen(request, timeout=10) as response:
            safe["status"] = "pass" if 200 <= response.status < 400 else "fail"
            safe["http_status"] = response.status
            safe["content_type"] = response.headers.get("Content-Type")
    except HTTPError as error:
        safe["status"] = "fail"
        safe["http_status"] = error.code
    except (URLError, TimeoutError, OSError) as error:
        safe["status"] = "fail"
        safe["error"] = error.__class__.__name__
    return safe


def main() -> int:
    args = parse_args()
    if args.check_origin and not args.origin:
        raise SystemExit("--check-origin requires --origin")
    root = args.target_root.resolve()
    if not root.is_dir():
        raise SystemExit(f"target root is not a directory: {root}")
    try:
        entry = find_entry(root, args.entry)
        html = entry.read_text(encoding="utf-8")
    except (OSError, ValueError) as error:
        raise SystemExit(str(error))

    parser = SurfaceParser()
    parser.feed(html)
    meta_description = bool(parser.meta.get("description", "").strip())
    viewport = bool(parser.meta.get("viewport", "").strip())
    mrbd_capable = parser.meta.get("mrbd-web-app-capable", "").strip().lower() == "yes"
    script_records = local_scripts(root, entry, parser.scripts)
    missing_scripts = [item["source"] for item in script_records if item.get("status") == "missing"]
    node_result = node_checks(root, script_records) if args.node_check else {"status": "not-run"}
    origin_result = origin_check(args.origin, args.check_origin)
    source_text = html
    source_contract = {
        "entrypoint": relative_path(root, entry),
        "git_revision": git_revision(root),
        "meta_description": meta_description,
        "viewport": viewport,
        "mrbd_web_app_capable_yes": mrbd_capable,
        "six_hundred_canvas_marker": bool(SIX_HUNDRED_RE.search(source_text)),
        "local_script_references": script_records,
        "missing_local_scripts": missing_scripts,
        "event_hooks": [
            label
            for label, token in (
                ("focus", "focus"),
                ("keyboard", "keydown"),
                ("pointer", "pointer"),
                ("input", "input"),
                ("change", "change"),
            )
            if token in source_text.lower()
        ],
        "localhost_reference": bool(re.search(r"(?:localhost|127\\.0\\.0\\.1)", source_text, re.IGNORECASE)),
        "source_conflict_features_present": [
            label
            for label, pattern in (
                ("text-input", r"<input|contenteditable|text composer"),
                ("offline", r"serviceWorker|service-worker|Cache API"),
                ("back", r"Escape|history\\.back|back navigation"),
                ("sensors", r"Accelerometer|Gyroscope|Geolocation|sensor"),
                ("gestures", r"gesture|pinch|pointermove"),
            )
            if re.search(pattern, source_text, re.IGNORECASE)
        ],
    }
    surface_class = "meta-web-app-source" if mrbd_capable else "generic-web-surface"
    static_pass = not missing_scripts and not source_contract["localhost_reference"]
    meta_contract_satisfied = meta_description and viewport and mrbd_capable
    meta_pass = not args.require_meta_markers or meta_contract_satisfied
    hosted_pass = not args.require_https_origin or origin_result.get("status") == "pass"
    node_pass = not args.node_check or node_result.get("status") == "pass"
    overall_pass = static_pass and meta_pass and hosted_pass and node_pass
    if not mrbd_capable:
        next_gate = "add and validate Meta Web App metadata before treating this as a Meta delivery target"
    elif origin_result.get("status") != "pass":
        next_gate = "check a public HTTPS origin, then run the official browser simulator"
    else:
        next_gate = "run the official browser simulator, then the named physical Ray-Ban Display script"
    receipt = {
        "receipt_version": 1,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if overall_pass else "fail",
        "evidence_level": "static",
        "surface_class": surface_class,
        "target_root_label": root.name,
        "source_contract": source_contract,
        "package": package_inventory(root, args.package_json),
        "origin": origin_result,
        "node_check": node_result,
        "proves": [
            "the selected local HTML source and referenced local assets were inspected",
            "the Meta Web App metadata contract is satisfied" if meta_contract_satisfied else "the Meta Web App metadata markers were inspected but are not all present",
            "the selected HTTPS origin responded to a read-only check" if origin_result.get("status") == "pass" else "hosted HTTPS delivery was not proven",
        ],
        "does_not_prove": [
            "Meta AI add/launch authorization or Developer Center account state",
            "browser-simulator behavior or physical Ray-Ban Display rendering, focus, input, latency, brightness, or comfort",
            "text-input, offline, back, sensor, or extended-gesture source-conflict features beyond their separate evidence rows",
            "Gen 2, Gen 3, signed, release-channel, or production support",
        ],
        "next_gate": next_gate,
    }
    if args.as_json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(f"WEBAPP_PREFLIGHT status={receipt['status']} class={surface_class} entry={source_contract['entrypoint']}")
        print(f"META_MARKERS {str(mrbd_capable).lower()} VIEWPORT {str(viewport).lower()} DESCRIPTION {str(meta_description).lower()}")
        print(f"ORIGIN {origin_result.get('status')} host={origin_result.get('host', 'not-run')}")
        print(f"NODE {node_result.get('status')}")
        print(f"NEXT {next_gate}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
