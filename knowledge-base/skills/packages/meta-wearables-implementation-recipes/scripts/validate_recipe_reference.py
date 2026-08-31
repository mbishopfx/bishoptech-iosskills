#!/usr/bin/env python3
"""Validate the bundled Meta Wearables implementation recipe reference."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_HEADINGS = (
    "## Recipe contract",
    "## Shared domain and adapter shape",
    "## iOS DAT session and camera",
    "## iOS native Display",
    "## Android DAT session and camera",
    "## Android native Display",
    "## Ray-Ban Display Web App",
    "## On-device and privacy gates",
    "## Verification ladder",
    "## Implementation handoff",
    "## Sources",
)

REQUIRED_MARKERS = (
    "COMPILE GATE",
    "to-verify",
    "phone fallback",
    "Gen 3",
    "physical",
    "on-device",
    "IOS-SESSION-001",
    "AND-SESSION-001",
    "WEB-RUNTIME-001",
    "https://github.com/facebook/meta-wearables-dat-ios",
    "https://github.com/facebook/meta-wearables-dat-android",
    "https://github.com/facebook/meta-wearables-webapp",
)

SECRET_PATTERNS = (
    re.compile(r"(?i)(?:sk|rk|pk)_[A-Za-z0-9]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "references" / "implementation-recipes.md",
    )
    args = parser.parse_args()
    path = args.path.resolve()
    if not path.is_file():
        raise SystemExit(f"missing recipe reference: {path}")

    text = path.read_text(encoding="utf-8")
    missing_headings = [heading for heading in REQUIRED_HEADINGS if heading not in text]
    missing_markers = [marker for marker in REQUIRED_MARKERS if marker not in text]
    fence_count = text.count("```")
    secret_hits = [
        (line_no, pattern.pattern)
        for line_no, line in enumerate(text.splitlines(), 1)
        for pattern in SECRET_PATTERNS
        if pattern.search(line)
    ]

    if missing_headings or missing_markers or fence_count % 2 or secret_hits:
        if missing_headings:
            print("MISSING_HEADINGS", ", ".join(missing_headings))
        if missing_markers:
            print("MISSING_MARKERS", ", ".join(missing_markers))
        if fence_count % 2:
            print("UNBALANCED_FENCES", fence_count)
        if secret_hits:
            print("SECRET_HITS", secret_hits)
        return 1

    print(
        f"OK recipe_reference={path} headings={len(REQUIRED_HEADINGS)} "
        f"markers={len(REQUIRED_MARKERS)} code_fences={fence_count // 2}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
