#!/usr/bin/env python3
"""Unfamiliar-stack Invariant Brief evaluation helpers.

This module freezes evaluation materials and summarizes already-scored receipts.
It deliberately does not dispatch models or decide whether a review finding is true.
"""

import hashlib
import json
import math
from pathlib import Path


class ManifestError(ValueError):
    """The frozen evaluation manifest is unsafe or inconsistent."""


def _load_manifest(manifest_path):
    path = Path(manifest_path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"manifest unreadable: {exc.__class__.__name__}") from exc
    if not isinstance(data, dict):
        raise ManifestError("manifest must be a JSON object")
    return path, data


def _material_path(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ManifestError("material path must be a non-empty relative path")
    candidate = root / relative
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root.resolve())
    except (OSError, ValueError) as exc:
        raise ManifestError(f"material path escapes or is missing: {relative}") from exc
    if candidate.is_symlink() or not resolved.is_file():
        raise ManifestError(f"material path must be a regular non-symlink file: {relative}")
    return resolved


def verify_manifest(manifest_path):
    path, data = _load_manifest(manifest_path)
    cases = data.get("cases")
    if not isinstance(cases, list):
        raise ManifestError("manifest cases must be a list")
    root = path.parent
    seen = set()
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("id"), str) or not case["id"]:
            raise ManifestError("each case needs a non-empty id")
        if case["id"] in seen:
            raise ManifestError(f"duplicate case id: {case['id']}")
        seen.add(case["id"])
        _case_metadata(case)
        files = case.get("files")
        if not isinstance(files, list) or not files:
            raise ManifestError(f"case {case['id']} needs frozen files")
        for item in files:
            if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
                raise ManifestError(f"case {case['id']} file entry must contain path and sha256")
            material = _material_path(root, item["path"])
            actual = hashlib.sha256(material.read_bytes()).hexdigest()
            if actual != item["sha256"]:
                raise ManifestError(f"sha256 mismatch: {item['path']}")
    return data


def _case_metadata(case):
    for field in ("language", "primary_defect", "normal_counterexample"):
        if not isinstance(case.get(field), str) or not case[field].strip():
            raise ManifestError(f"case needs {field}")
    oracle = case.get("oracle")
    if not isinstance(oracle, dict) or not oracle.get("expected"):
        raise ManifestError("case needs oracle expected results")
    if not (oracle.get("command") or oracle.get("command_template")):
        raise ManifestError("case needs oracle command")


def _dispatch_materials(case):
    # Declared allowlist is reviewed with S3; filenames are not a semantic oracle.
    common, brief = case.get("dispatch_common"), case.get("dispatch_brief")
    if not isinstance(common, list) or not common or not all(isinstance(p, str) for p in common):
        raise ManifestError("case needs dispatch_common materials")
    if not isinstance(brief, str) or brief in common or len(set(common)) != len(common):
        raise ManifestError("case needs distinct dispatch_brief materials")
    frozen = {item["path"] for item in case["files"]}
    if not set([*common, brief]) <= frozen:
        raise ManifestError("dispatch materials must be frozen in this case")
    for path in [*common, brief]:
        name = Path(path).name.lower()
        if any(word in name for word in ("fixed", "answer-key", "answer_key", "oracle")):
            raise ManifestError("grader-only materials cannot be dispatched")
    return common, brief


def _session_fields(session):
    if not isinstance(session, dict):
        raise ManifestError("each session must be an object")
    model, effort = session.get("model"), session.get("effort")
    if not isinstance(model, str) or not model or not isinstance(effort, str) or not effort:
        raise ManifestError("each session needs model and effort")
    materials = session.get("materials")
    if not isinstance(materials, list) or not all(isinstance(item, str) for item in materials):
        raise ManifestError("session materials must be a list of paths")
    if any("answer-key" in item.lower() or "answer_key" in item.lower() for item in materials):
        raise ManifestError("answer key must not appear in dispatched materials")
    if not isinstance(session.get("case_id"), str) or not isinstance(session.get("arm"), str):
        raise ManifestError("session case and arm must be strings")
    return model, effort


def preflight_run(manifest_path, output_dir):
    output = Path(output_dir)
    if output.exists():
        raise ManifestError(f"output directory already exists: {output}")
    data = verify_manifest(manifest_path)
    cases = data.get("cases")
    sessions = data.get("sessions")
    if len(cases) != 5:
        raise ManifestError("experiment requires exactly five cases")
    if not isinstance(sessions, list) or len(sessions) != 10:
        raise ManifestError("experiment requires exactly ten sessions")
    case_ids = {case["id"] for case in cases}
    allowed = {case["id"]: _dispatch_materials(case) for case in cases}
    expected = {(case_id, arm) for case_id in case_ids for arm in ("control", "brief")}
    observed = set()
    models, efforts = set(), set()
    for session in sessions:
        model, effort = _session_fields(session)
        pair = (session.get("case_id"), session.get("arm"))
        if pair not in expected or pair in observed:
            raise ManifestError("sessions must contain one control and one brief arm per case")
        common, brief = allowed[pair[0]]
        if session["materials"] != common + ([brief] if pair[1] == "brief" else []):
            raise ManifestError("session materials must match the frozen arm allowlist")
        observed.add(pair)
        models.add(model)
        efforts.add(effort)
    if observed != expected:
        raise ManifestError("sessions must contain one control and one brief arm per case")
    if len(models) != 1:
        raise ManifestError("all sessions must use the same model")
    if len(efforts) != 1:
        raise ManifestError("all sessions must use the same effort")
    return data


def _receipt_invalid_reason(row):
    for field in ("valid", "primary_hit", "evidence_grounded", "normal_counterexample_harmed"):
        if type(row[field]) is not bool:
            return f"{field} must be boolean"
    for field in ("false_positives", "tokens"):
        if type(row[field]) is not int or row[field] < 0:
            return f"{field} must be a non-negative integer"
    elapsed = row["elapsed_seconds"]
    if (type(elapsed) not in (int, float) or elapsed < 0
            or (type(elapsed) is float and not math.isfinite(elapsed))):
        return "elapsed_seconds must be finite and non-negative"
    if not row["valid"]:
        return row.get("invalid_reason") or "session marked invalid"
    if row["familiarity"] != "unfamiliar":
        return "reviewer is not unfamiliar with this stack"
    return None


def summarize_receipts(receipts):
    if not isinstance(receipts, list):
        raise ManifestError("receipts must be a list")
    expected = {(f"U{number}", arm) for number in range(1, 6) for arm in ("control", "brief")}
    by_pair = {}
    seen = set()
    invalid = []
    required = {
        "case_id", "arm", "valid", "primary_hit", "evidence_grounded", "false_positives",
        "normal_counterexample_harmed", "familiarity", "elapsed_seconds", "tokens",
    }
    for index, row in enumerate(receipts):
        if not isinstance(row, dict) or not required <= set(row):
            invalid.append({"index": index, "reason": "missing receipt fields"})
            continue
        pair = (row["case_id"], row["arm"])
        if not all(isinstance(value, str) for value in pair) or pair not in expected:
            invalid.append({"index": index, "reason": "unknown case or arm"})
            continue
        if pair in seen:
            invalid.append({"index": index, "reason": "duplicate case arm"})
            continue
        seen.add(pair)
        reason = _receipt_invalid_reason(row)
        if reason:
            invalid.append({"index": index, "reason": reason})
        else:
            by_pair[pair] = row
    for pair in sorted(expected - seen):
        invalid.append({"case_id": pair[0], "arm": pair[1], "reason": "missing session"})

    def confirmed(row):
        return bool(row and row["valid"] and row["familiarity"] == "unfamiliar"
                    and row["primary_hit"] and row["evidence_grounded"])

    per_case = []
    additional = 0
    for number in range(1, 6):
        case_id = f"U{number}"
        control = by_pair.get((case_id, "control"))
        brief = by_pair.get((case_id, "brief"))
        control_hit, brief_hit = confirmed(control), confirmed(brief)
        additional += int(brief_hit and not control_hit)
        per_case.append({"case_id": case_id, "control": control, "brief": brief,
                         "control_confirmed_hit": control_hit, "brief_confirmed_hit": brief_hit})
    control_hits = sum(row["control_confirmed_hit"] for row in per_case)
    brief_hits = sum(row["brief_confirmed_hit"] for row in per_case)
    brief_fp = sum(row.get("false_positives", 0) for (case_id, arm), row in by_pair.items() if arm == "brief")
    control_fp = sum(row.get("false_positives", 0) for (case_id, arm), row in by_pair.items() if arm == "control")
    brief_harms = sum(bool(row.get("normal_counterexample_harmed")) for (case_id, arm), row in by_pair.items() if arm == "brief")
    control_harms = sum(bool(row.get("normal_counterexample_harmed")) for (case_id, arm), row in by_pair.items() if arm == "control")
    decision = "incomplete" if invalid else (
        "proceed-to-historical"
        if additional >= 2 and brief_fp <= control_fp + 1 and brief_harms <= control_harms
        else "stop"
    )
    return {
        "decision": decision,
        "control_primary_hits": control_hits,
        "brief_primary_hits": brief_hits,
        "additional_primary_hits": additional,
        "control_false_positives": control_fp,
        "brief_false_positives": brief_fp,
        "control_normal_counterexample_harms": control_harms,
        "brief_normal_counterexample_harms": brief_harms,
        "invalid_sessions": invalid,
        "per_case": per_case,
        "raw_receipts": receipts,
    }
