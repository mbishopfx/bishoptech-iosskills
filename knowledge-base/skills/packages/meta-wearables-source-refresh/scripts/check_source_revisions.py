#!/usr/bin/env python3
"""Compare pinned Meta Wearables repository refs with public Git refs."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

import yaml


REQUIRED_JOURNEYS = ("native-dat-ios", "native-dat-android", "web-apps")
TAG_PATTERN = re.compile(r"(?:tag|release)\s+([0-9a-f]{40})", re.IGNORECASE)
VERSION_TAG_PATTERN = re.compile(r"(\d+\.\d+\.\d+)\s+tag\s+([0-9a-f]{40})", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", type=Path, help="path to the source-pinned surface manifest")
    parser.add_argument("--timeout", type=float, default=20.0, help="git ls-remote timeout in seconds")
    return parser.parse_args()


def fail(message: str) -> None:
    raise ValueError(message)


def default_manifest_path() -> Path:
    candidates = (
        Path.cwd() / "knowledge-base" / "skills" / "packages" / "meta-wearables-full-sdk-audit" / "references" / "surface-manifest.yaml",
        Path(__file__).resolve().parents[2] / "meta-wearables-full-sdk-audit" / "references" / "surface-manifest.yaml",
    )
    return next((candidate for candidate in candidates if candidate.is_file()), candidates[0])


def remote_revision(repository: str, ref: str, timeout: float) -> str:
    result = subprocess.run(
        ["git", "ls-remote", "--refs", repository, ref],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "git ls-remote failed"
        raise RuntimeError(f"{repository} {ref}: {detail}")
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[1] == ref:
            return fields[0]
    raise RuntimeError(f"{repository} {ref}: ref not found")


def check_ref(
    checks: list[tuple[str, str, str, str]],
    repository: str,
    ref: str,
    expected: str,
    label: str,
    timeout: float,
) -> bool:
    observed = remote_revision(repository, ref, timeout)
    matches = observed == expected
    checks.append((label, expected, observed, "match" if matches else "drift"))
    return matches


def full_reference_url(anchor: str) -> str:
    parts = urlsplit(anchor)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["full"] = "true"
    query["product"] = "dat"
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def check_full_reference(
    checks: list[tuple[str, str, str, str]],
    url: str,
    expected_terms: list[str],
    timeout: float,
) -> bool:
    url = full_reference_url(url)
    request = Request(url, headers={"User-Agent": "bishoptech-iosskills-source-refresh/1.0"})
    with urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8", errors="replace")
    observed = [term for term in expected_terms if term.lower() in body.lower()]
    missing = [term for term in expected_terms if term not in observed]
    matches = not missing
    expected = ", ".join(expected_terms)
    observed_text = ", ".join(observed) or f"missing={missing!r}"
    checks.append((f"full-reference {url}", expected, observed_text, "match" if matches else "drift"))
    return matches


def main() -> int:
    args = parse_args()
    manifest_path = (args.manifest or default_manifest_path()).resolve()
    if not manifest_path.is_file():
        fail(f"manifest not found: {manifest_path}; pass the source-pinned manifest path explicitly")

    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail("manifest root must be a mapping")
    journeys = {journey.get("id"): journey for journey in data.get("journeys", []) if isinstance(journey, dict)}
    missing = [journey_id for journey_id in REQUIRED_JOURNEYS if journey_id not in journeys]
    if missing:
        fail(f"manifest is missing journeys: {', '.join(missing)}")

    checks: list[tuple[str, str, str, str]] = []
    for journey_id in REQUIRED_JOURNEYS:
        journey = journeys[journey_id]
        repository = journey.get("repository")
        revision = journey.get("revision")
        if not repository or not revision:
            fail(f"{journey_id} needs repository and revision")
        check_ref(checks, repository, "refs/heads/main", revision, f"{journey_id} main", args.timeout)

        release = journey.get("reproducible_release", "")
        match = VERSION_TAG_PATTERN.search(release)
        if match:
            version, tag_revision = match.groups()
            check_ref(
                checks,
                repository,
                f"refs/tags/{version}",
                tag_revision,
                f"{journey_id} tag {version}",
                args.timeout,
            )
        elif journey_id == "native-dat-ios":
            match = TAG_PATTERN.search(release)
            if not match:
                fail("native-dat-ios reproducible_release needs an exact tag revision")

    snapshot = data.get("snapshot", {})
    full_reference_url_value = snapshot.get("full_reference_url")
    full_reference_terms = snapshot.get("full_reference_anchor_terms")
    if not full_reference_url_value or not isinstance(full_reference_terms, list) or not full_reference_terms:
        fail("snapshot needs full_reference_url and full_reference_anchor_terms")
    check_full_reference(checks, full_reference_url_value, full_reference_terms, args.timeout)

    drifted = False
    for label, expected, observed, status in checks:
        print(f"{status.upper()} {label} expected={expected} observed={observed}")
        drifted = drifted or status != "match"
    print(f"CHECKS {len(checks)} DRIFT {sum(status != 'match' for _, _, _, status in checks)}")
    return 1 if drifted else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (HTTPError, URLError, OSError, RuntimeError, subprocess.SubprocessError, TypeError, ValueError, yaml.YAMLError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        raise SystemExit(2)
