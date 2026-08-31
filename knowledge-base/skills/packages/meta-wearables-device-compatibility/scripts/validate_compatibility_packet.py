#!/usr/bin/env python3
"""Validate a sanitized Meta Wearables compatibility evidence packet."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


TOP_LEVEL_REQUIRED = {
    "schema_version",
    "packet_id",
    "status",
    "source_snapshot",
    "target",
    "capabilities",
    "evidence",
    "open_gates",
    "next_proof_task",
    "redaction",
}
SOURCE_REQUIRED = {
    "retrieval_date",
    "full_reference",
    "version_dependency_access",
    "repository_revisions",
}
TARGET_REQUIRED = {
    "consumer_label",
    "generation_label",
    "retail_product_or_sku",
    "route",
    "package_or_artifact",
    "sdk_revision",
    "phone_os_build",
    "meta_ai_version",
    "device_type_observed",
    "firmware",
    "on_glasses_dat_app",
    "link",
    "permission_compatibility",
    "account_mode",
    "evidence_level",
    "processing_claim",
}
CAPABILITY_REQUIRED = {
    "name",
    "status",
    "evidence_level",
    "operation",
    "processing_location",
    "fallback",
    "next_action",
}
EVIDENCE_REQUIRED = {
    "id",
    "status",
    "operation",
    "artifact_or_record",
    "proves",
    "does_not_prove",
}
EVIDENCE_IDS = {
    "COMP-SOURCE-01",
    "COMP-STATIC-01",
    "COMP-VERSION-01",
    "COMP-TUPLE-01",
    "COMP-CAPABILITY-01",
    "COMP-FIRMWARE-01",
    "COMP-GEN3-01",
    "COMP-RELEASE-01",
}
EVIDENCE_LEVELS = {
    "source",
    "access-gated",
    "static",
    "build",
    "mock",
    "browser-sim",
    "connected",
    "physical",
    "signed",
    "release",
    "release-channel",
    "production",
    "not-run",
    "blocked",
    "to-verify",
}
CAPABILITY_STATUSES = {
    "current",
    "to-verify",
    "device-gated",
    "source-conflict",
    "unsupported",
}
PROCESSING_CLAIMS = {
    "glasses-native",
    "phone-local",
    "remote",
    "mixed",
    "unknown",
}
ROUTES = {
    "native-dat-ios",
    "native-dat-android",
    "native-display-ios",
    "native-display-android",
    "web-app",
    "phone-fallback",
}
PACKET_STATUSES = {"draft", "ready-for-physical", "completed", "blocked"}
SAFE_REDACTED_VALUES = {
    "present-redacted",
    "omitted",
    "unknown",
    "to-verify",
    "not-run",
    "access-gated",
}
SENSITIVE_KEY_PARTS = {
    "token",
    "password",
    "secret",
    "private_key",
    "serial",
    "mac",
    "raw_device_identifier",
}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SECRET_RE = re.compile(r"(?:gh[pousr]_[A-Za-z0-9_\-]{20,}|github_pat_[A-Za-z0-9_\-]{20,}|sk-[A-Za-z0-9_\-]{20,})")
UNRESOLVED = {"unknown", "to-verify", "not-run", "access-gated"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    return parser.parse_args()


def is_mapping(value: Any) -> bool:
    return isinstance(value, dict)


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def missing_keys(mapping: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(required - set(mapping))


def validate_packet(data: Any) -> list[str]:
    errors: list[str] = []
    if not is_mapping(data):
        return ["root must be a mapping"]

    missing = missing_keys(data, TOP_LEVEL_REQUIRED)
    if missing:
        errors.append(f"root missing required keys: {', '.join(missing)}")

    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not is_nonempty_string(data.get("packet_id")):
        errors.append("packet_id must be a non-empty string")
    if data.get("status") not in PACKET_STATUSES:
        errors.append(f"status must be one of {sorted(PACKET_STATUSES)}")

    source = data.get("source_snapshot")
    if not is_mapping(source):
        errors.append("source_snapshot must be a mapping")
    else:
        missing = missing_keys(source, SOURCE_REQUIRED)
        if missing:
            errors.append(f"source_snapshot missing required keys: {', '.join(missing)}")
        if not DATE_RE.fullmatch(str(source.get("retrieval_date", ""))):
            errors.append("source_snapshot.retrieval_date must use YYYY-MM-DD")
        if not is_nonempty_string(source.get("full_reference")):
            errors.append("source_snapshot.full_reference must be a non-empty URL")
        if source.get("version_dependency_access") not in {"known", "access-gated", "not-run"}:
            errors.append("source_snapshot.version_dependency_access must be known, access-gated, or not-run")
        revisions = source.get("repository_revisions")
        if not is_mapping(revisions):
            errors.append("source_snapshot.repository_revisions must be a mapping")
        else:
            for key in ("dat_ios", "dat_android", "web_apps"):
                if not is_nonempty_string(revisions.get(key)):
                    errors.append(f"source_snapshot.repository_revisions.{key} must be recorded")

    target = data.get("target")
    if not is_mapping(target):
        errors.append("target must be a mapping")
    else:
        missing = missing_keys(target, TARGET_REQUIRED)
        if missing:
            errors.append(f"target missing required keys: {', '.join(missing)}")
        for key in TARGET_REQUIRED:
            if key in target and not is_nonempty_string(target[key]):
                errors.append(f"target.{key} must be a non-empty string")
        if target.get("route") not in ROUTES:
            errors.append(f"target.route must be one of {sorted(ROUTES)}")
        if target.get("evidence_level") not in EVIDENCE_LEVELS:
            errors.append(f"target.evidence_level must be one of {sorted(EVIDENCE_LEVELS)}")
        if target.get("processing_claim") not in PROCESSING_CLAIMS:
            errors.append(f"target.processing_claim must be one of {sorted(PROCESSING_CLAIMS)}")
        if target.get("link") not in {"bluetooth", "wifi", "mixed", "unknown"}:
            errors.append("target.link must be bluetooth, wifi, mixed, or unknown")
        if target.get("account_mode") not in {"developer-mode", "release-channel", "unknown", "not-run"}:
            errors.append("target.account_mode is not a recognized account mode")

    capabilities = data.get("capabilities")
    current_capabilities: list[str] = []
    if not isinstance(capabilities, list) or not capabilities:
        errors.append("capabilities must be a non-empty list")
    else:
        names: set[str] = set()
        for index, capability in enumerate(capabilities):
            path = f"capabilities[{index}]"
            if not is_mapping(capability):
                errors.append(f"{path} must be a mapping")
                continue
            missing = missing_keys(capability, CAPABILITY_REQUIRED)
            if missing:
                errors.append(f"{path} missing required keys: {', '.join(missing)}")
            name = capability.get("name")
            if not is_nonempty_string(name):
                errors.append(f"{path}.name must be a non-empty string")
            elif name in names:
                errors.append(f"duplicate capability name: {name}")
            else:
                names.add(name)
            if capability.get("status") not in CAPABILITY_STATUSES:
                errors.append(f"{path}.status must be one of {sorted(CAPABILITY_STATUSES)}")
            if capability.get("evidence_level") not in EVIDENCE_LEVELS:
                errors.append(f"{path}.evidence_level must be one of {sorted(EVIDENCE_LEVELS)}")
            if capability.get("processing_location") not in PROCESSING_CLAIMS:
                errors.append(f"{path}.processing_location must be one of {sorted(PROCESSING_CLAIMS)}")
            for key in ("operation", "fallback", "next_action"):
                if not is_nonempty_string(capability.get(key)):
                    errors.append(f"{path}.{key} must be a non-empty string")
            if capability.get("status") == "current":
                current_capabilities.append(str(name))
                if capability.get("evidence_level") not in {"physical", "release", "release-channel", "production"}:
                    errors.append(f"{path}.current requires physical or release-level evidence")
            if capability.get("status") == "unsupported" and capability.get("fallback") in {"", "none", "unknown"}:
                errors.append(f"{path}.unsupported requires an explicit fallback")

    evidence = data.get("evidence")
    evidence_by_id: dict[str, dict[str, Any]] = {}
    if not isinstance(evidence, list):
        errors.append("evidence must be a list")
    else:
        for index, row in enumerate(evidence):
            path = f"evidence[{index}]"
            if not is_mapping(row):
                errors.append(f"{path} must be a mapping")
                continue
            missing = missing_keys(row, EVIDENCE_REQUIRED)
            if missing:
                errors.append(f"{path} missing required keys: {', '.join(missing)}")
            row_id = row.get("id")
            if row_id not in EVIDENCE_IDS:
                errors.append(f"{path}.id must be one of {sorted(EVIDENCE_IDS)}")
            elif row_id in evidence_by_id:
                errors.append(f"duplicate evidence id: {row_id}")
            else:
                evidence_by_id[row_id] = row
            if row.get("status") not in EVIDENCE_LEVELS:
                errors.append(f"{path}.status must be one of {sorted(EVIDENCE_LEVELS)}")
            for key in ("operation", "artifact_or_record", "proves", "does_not_prove"):
                if not is_nonempty_string(row.get(key)):
                    errors.append(f"{path}.{key} must be a non-empty string")

    missing_evidence = sorted(EVIDENCE_IDS - set(evidence_by_id))
    if missing_evidence:
        errors.append(f"evidence is missing required rows: {', '.join(missing_evidence)}")

    next_task = data.get("next_proof_task")
    if not is_mapping(next_task) or not is_nonempty_string(next_task.get("id")) or not is_nonempty_string(next_task.get("action")):
        errors.append("next_proof_task must include non-empty id and action")
    elif next_task.get("id") not in EVIDENCE_IDS:
        errors.append("next_proof_task.id must identify a known COMP-* row")

    open_gates = data.get("open_gates")
    if not isinstance(open_gates, list) or not open_gates or not all(is_nonempty_string(gate) for gate in open_gates):
        errors.append("open_gates must be a non-empty list of strings")

    redaction = data.get("redaction")
    if not is_mapping(redaction):
        errors.append("redaction must be a mapping")
    else:
        for key, value in redaction.items():
            if any(part in str(key).lower() for part in SENSITIVE_KEY_PARTS):
                if value not in SAFE_REDACTED_VALUES:
                    errors.append(f"redaction.{key} must be a safe presence/omission value")

    generation = str(target.get("generation_label", "")).lower() if is_mapping(target) else ""
    consumer_label = str(target.get("consumer_label", "")).lower() if is_mapping(target) else ""
    mentions_gen3 = generation == "gen-3" or bool(re.search(r"gen\s*3", consumer_label))
    gen3_row = evidence_by_id.get("COMP-GEN3-01")
    if mentions_gen3 and gen3_row is not None:
        if data.get("status") == "completed" and gen3_row.get("status") not in {"physical", "release", "release-channel", "production"}:
            errors.append("a completed Gen 3 packet requires physical or release-level COMP-GEN3-01 evidence")
        if is_mapping(target) and target.get("evidence_level") in {"physical", "release", "release-channel", "production"} and gen3_row.get("status") not in {"physical", "release", "release-channel", "production"}:
            errors.append("target evidence_level cannot exceed COMP-GEN3-01 evidence")

    if data.get("status") == "completed":
        tuple_status = evidence_by_id.get("COMP-TUPLE-01", {}).get("status")
        if tuple_status not in {"connected", "physical", "release", "release-channel", "production"}:
            errors.append("completed packet requires connected-or-better COMP-TUPLE-01 evidence")
        capability_status = evidence_by_id.get("COMP-CAPABILITY-01", {}).get("status")
        if current_capabilities and capability_status not in {"physical", "release", "release-channel", "production"}:
            errors.append("current capabilities require physical-or-better COMP-CAPABILITY-01 evidence")
        release_status = evidence_by_id.get("COMP-RELEASE-01", {}).get("status")
        if release_status not in {"release", "release-channel", "production"}:
            errors.append("completed packet requires release-level COMP-RELEASE-01 evidence")

    def walk(value: Any, path: str = "root") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                key_text = str(key).lower()
                if any(part in key_text for part in SENSITIVE_KEY_PARTS) and child not in SAFE_REDACTED_VALUES:
                    errors.append(f"{path}.{key} contains a non-redacted sensitive value")
                walk(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}[{index}]")
        elif isinstance(value, str) and SECRET_RE.search(value):
            errors.append(f"{path} looks like a credential")

    walk(data)
    return sorted(set(errors))


def main() -> int:
    args = parse_args()
    packet = args.packet.resolve()
    if not packet.is_file():
        print(f"ERROR packet not found: {packet}", file=sys.stderr)
        return 2
    try:
        data = yaml.safe_load(packet.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 2
    errors = validate_packet(data)
    if errors:
        print(f"INVALID compatibility_packet={packet}")
        for error in errors:
            print(f"  ERROR {error}")
        return 1
    target = data["target"]
    print(
        f"OK compatibility_packet={packet} status={data['status']} "
        f"route={target['route']} generation={target['generation_label']} "
        f"capabilities={len(data['capabilities'])} evidence_rows={len(data['evidence'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
