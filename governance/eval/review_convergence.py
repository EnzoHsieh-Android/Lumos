"""Readonly, bounded evidence collection and paired review convergence evaluation."""

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys


class DataError(ValueError):
    pass


def read_bytes(path, limit=16 * 1024 * 1024):
    try:
        path = Path(path)
        if path.is_symlink():
            raise DataError("symlink-input")
        fd = os.open(
            path,
            os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise DataError("nonregular-input")
            stream = os.fdopen(fd, "rb")
        except BaseException:
            os.close(fd)
            raise
        with stream as f:
            raw = f.read(limit + 1)
        if len(raw) > limit:
            raise DataError("input-too-large")
        return raw
    except DataError:
        raise
    except (OSError, ValueError) as exc:
        raise DataError("input-unreadable") from exc


def decode(raw):
    try:
        return raw.decode("utf-8")
    except UnicodeError as exc:
        raise DataError("input-encoding") from exc


def parse(text):
    try:

        def bad_constant(_):
            raise ValueError("nonfinite")

        def finite_float(value):
            result = float(value)
            if not math.isfinite(result):
                raise ValueError("nonfinite")
            return result

        def unique(pairs):
            out = {}
            for k, v in pairs:
                if k in out:
                    raise ValueError("duplicate-key")
                out[k] = v
            return out

        result = json.loads(
            text,
            parse_constant=bad_constant,
            parse_float=finite_float,
            object_pairs_hook=unique,
        )
        validate_unicode(result)
        return result
    except (ValueError, RecursionError) as exc:
        raise DataError("input-json") from exc


def validate_unicode(value):
    pending = [value]
    while pending:
        x = pending.pop()
        if isinstance(x, str):
            x.encode("utf-8")
        elif isinstance(x, dict):
            pending.extend(x.keys())
            pending.extend(x.values())
        elif isinstance(x, list):
            pending.extend(x)


def render_json(value):
    rendered = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)
    controls = [
        *range(0x7F, 0xA0),
        0x61C,
        0x200E,
        0x200F,
        0x2028,
        0x2029,
        *range(0x202A, 0x202F),
        *range(0x2066, 0x206A),
    ]
    for point in controls:
        rendered = rendered.replace(chr(point), "\\u" + format(point, "04x"))
    return rendered


def read_json(path, limit=256 * 1024):
    return parse(decode(read_bytes(path, limit)))


def parse_jsonl(raw):
    rows = []
    for match in re.finditer(r"[^\r\n]+", decode(raw)):
        line = match.group()
        if not line.strip():
            continue
        if len(rows) >= 100000:
            raise DataError("input-record-limit")
        rows.append(parse(line))
    return rows


def read_ledger(path):
    rows = parse_jsonl(read_bytes(path))
    if any(not isinstance(x, dict) for x in rows):
        raise DataError("ledger-nonobject")
    return rows


def number(x):
    return type(x) in (int, float) and 0 <= x <= 10**15 and math.isfinite(x)


def integer(x):
    return type(x) is int and x >= 0


def json_equal(left, right):
    pending = [(left, right)]
    while pending:
        left, right = pending.pop()
        left_type, right_type = type(left), type(right)
        if left_type in (int, float) and right_type in (int, float):
            if left != right:
                return False
        elif left_type is not right_type:
            return False
        elif left_type is dict:
            if left.keys() != right.keys():
                return False
            pending.extend((left[key], right[key]) for key in left)
        elif left_type is list:
            if len(left) != len(right):
                return False
            pending.extend(zip(left, right))
        elif left != right:
            return False
    return True


def build_cohort(rows):
    groups = {}
    seen_tokens = {}
    conflicts = set()
    for row in rows:
        token = row.get("token")
        if isinstance(token, str) and token and row.get("kind") != "spec-gate":
            if token in seen_tokens and not json_equal(seen_tokens[token], row):
                conflicts.add(token)
            seen_tokens[token] = row
    for row in rows:
        loop = row.get("loop")
        if (
            isinstance(loop, str)
            and loop.startswith("code-")
            and row.get("kind") != "spec-gate"
        ):
            groups.setdefault(loop, []).append(row)
    loops = []
    for loop, source in sorted(groups.items()):
        unique, tokens, duplicate = [], {}, 0
        conflict = any(
            row.get("token") in conflicts
            for row in source
            if isinstance(row.get("token"), str)
        )
        for row in source:
            token = row.get("token")
            if isinstance(token, str) and token:
                if token in tokens:
                    duplicate += 1
                    continue
                tokens[token] = row
            unique.append(row)
        rounds = list(
            dict.fromkeys(
                x["round"]
                for x in unique
                if isinstance(x.get("round"), str) and x["round"]
            )
        )
        sequence = [x.get("round") for x in unique]
        blocks = [r for i, r in enumerate(sequence) if i == 0 or r != sequence[i - 1]]
        invalid_rounds = any(not isinstance(r, str) or not r for r in sequence) or len(
            blocks
        ) != len(set(blocks))
        cost = [x.get("tokens") for x in unique]
        known = [x for x in cost if number(x)]
        loops.append(
            {
                "loop": loop,
                "records": len(source),
                "duplicate_records": duplicate,
                "conflicting_tokens": conflict,
                "round_sequence_anomalous": invalid_rounds,
                "rounds": rounds,
                "round_count": len(rounds)
                if all(isinstance(x.get("round"), str) and x["round"] for x in unique)
                and not conflict
                and not invalid_rounds
                else None,
                "tokens": {
                    "total": sum(known)
                    if len(known) == len(cost) and not conflict and not invalid_rounds
                    else None,
                    "known_records": len(known),
                },
                "converged": None,
            }
        )
    return {
        "version": 1,
        "observed_code_loops": len(loops),
        "loops": loops,
        "limits": [
            "observed loop IDs are not independent tasks",
            "closure and severity do not prove convergence",
            "retrospective categories do not establish fix causality",
        ],
    }


def split_for(group):
    return (
        "held"
        if int(hashlib.sha256(group.encode()).hexdigest(), 16) % 5 == 0
        else "train"
    )


def case_template(loop):
    if not text_field(loop) or not loop.startswith("code-"):
        raise DataError("case-loop")
    return {
        "id": None,
        "group": None,
        "split": None,
        "loop": loop,
        "finding": None,
        "start_commit": None,
        "case_sha256": None,
        "grader_sha256": None,
        "environment_sha256": None,
    }


def sha(value, length):
    return (
        isinstance(value, str)
        and re.fullmatch("[0-9a-f]{" + str(length) + "}", value) is not None
    )


def text_field(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 128:
        return False
    try:
        value.encode("utf-8")
    except UnicodeError:
        return False
    return True


def validate_manifest(m):
    if (
        not isinstance(m, dict)
        or type(m.get("version")) is not int
        or m["version"] != 1
    ):
        raise DataError("manifest-version")
    cases, arms, repeats = m.get("cases"), m.get("arms"), m.get("repeats")
    if (
        not isinstance(cases, list)
        or not 1 <= len(cases) <= 100
        or not integer(repeats)
        or not 1 <= repeats <= 20
    ):
        raise DataError("manifest-size")
    if not isinstance(arms, dict) or set(arms) != {"baseline", "candidate"}:
        raise DataError("manifest-arms")
    validate_arms(arms)
    validate_cases(cases)
    return m


def validate_arms(arms):
    for a in arms.values():
        if (
            not isinstance(a, dict)
            or not text_field(a.get("model"))
            or any(
                not sha(a.get(k), 64) for k in ("workflow_sha256", "dispatch_sha256")
            )
        ):
            raise DataError("manifest-arm-pin")
    if arms["baseline"]["model"] != arms["candidate"]["model"]:
        raise DataError("manifest-model-confounded")


def validate_cases(cases):
    ids = set()
    for c in cases:
        if not isinstance(c, dict) or any(
            not text_field(c.get(k)) for k in ("id", "group", "loop", "finding")
        ):
            raise DataError("case-incomplete")
        if c["id"] in ids or not c["loop"].startswith("code-"):
            raise DataError("case-id")
        ids.add(c["id"])
        if c.get("split") != split_for(c["group"]):
            raise DataError("case-group-split")
        if not sha(c.get("start_commit"), 40) or any(
            not sha(c.get(k), 64)
            for k in ("case_sha256", "grader_sha256", "environment_sha256")
        ):
            raise DataError("case-pin")


def slot(record):
    if (
        not isinstance(record, dict)
        or not text_field(record.get("case_id"))
        or record.get("arm") not in ("baseline", "candidate")
        or not integer(record.get("repeat"))
    ):
        return None
    return (record["case_id"], record["arm"], record["repeat"])


def check_trial(record, m, root, cases_by_id=None):
    try:
        key = slot(record)
        case_index = (
            cases_by_id if cases_by_id is not None else {c["id"]: c for c in m["cases"]}
        )
        c = case_index.get(key[0]) if key else None
        if c is None or not 1 <= key[2] <= m["repeats"]:
            raise DataError("trial-slot")
        d = load_receipt(record, root)
        for k in ("case_id", "arm", "repeat"):
            if type(d.get(k)) is not type(record[k]) or d[k] != record[k]:
                raise DataError("receipt-slot")
        for k in ("start_commit", "case_sha256", "grader_sha256", "environment_sha256"):
            if d.get(k) != c[k]:
                raise DataError("receipt-" + k)
        for k, v in m["arms"][key[1]].items():
            if d.get(k) != v:
                raise DataError("receipt-" + k)
        if (
            not sha(d.get("result_commit"), 40)
            or d.get("loaded_start_commit") != c["start_commit"]
            or d.get("loaded_result_commit") != d["result_commit"]
        ):
            raise DataError("loaded-source")
        validate_outcome(d)
        fields = (
            "case_id",
            "arm",
            "repeat",
            "repair",
            "preserve",
            "new_defects",
            "rounds",
            "tokens",
            "wall_seconds",
            "quality_pass",
        )
        return {k: d.get(k) for k in fields}, None
    except DataError as exc:
        return None, str(exc)


def load_receipt(record, root):
    ref = record.get("receipt")
    if (
        not isinstance(ref, dict)
        or not isinstance(ref.get("path"), str)
        or not sha(ref.get("sha256"), 64)
    ):
        raise DataError("receipt-reference")
    if "\0" in ref["path"]:
        raise DataError("receipt-path")
    rel = Path(ref["path"])
    if rel.anchor or ".." in rel.parts or not rel.parts:
        raise DataError("receipt-path")
    base = Path(root).resolve()
    p = base
    for part in rel.parts:
        p = p / part
        if p.is_symlink():
            raise DataError("receipt-path")
    raw = read_bytes(p, 256 * 1024)
    if hashlib.sha256(raw).hexdigest() != ref["sha256"]:
        raise DataError("receipt-hash")
    d = parse(decode(raw))
    if not isinstance(d, dict):
        raise DataError("receipt-object")
    return d


def validate_outcome(d):
    if d.get("status") != "completed":
        raise DataError("trial-status-" + str(d.get("status"))[:40])
    if (
        type(d.get("repair")) is not bool
        or type(d.get("preserve")) is not bool
        or not integer(d.get("new_defects"))
        or d["new_defects"] > 1000000
    ):
        raise DataError("outcome-unknown")
    if not integer(d.get("rounds")) or not 1 <= d["rounds"] <= 1000000:
        raise DataError("rounds-unknown")
    for field in ("tokens", "wall_seconds"):
        value = d.get(field)
        if value is not None and not number(value):
            raise DataError("cost-" + field)
    d["quality_pass"] = d["repair"] and d["preserve"] and d["new_defects"] == 0


def summarize(valid, cases, repeats):
    lookup = {(d["case_id"], d["arm"], d["repeat"]): d for d in valid}
    pairs = [
        (lookup[(c["id"], "baseline", r)], lookup[(c["id"], "candidate", r)])
        for c in cases
        for r in range(1, repeats + 1)
        if all((c["id"], a, r) in lookup for a in ("baseline", "candidate"))
    ]
    joint = [(b, c) for b, c in pairs if b["quality_pass"] and c["quality_pass"]]
    arms = {}
    for arm in ("baseline", "candidate"):
        ds = [d for d in valid if d["arm"] == arm]
        summary = {
            "valid": len(ds),
            "quality_passes": sum(d["quality_pass"] for d in ds),
            "repair_passes": sum(d["repair"] for d in ds),
            "preserve_passes": sum(d["preserve"] for d in ds),
            "new_defect_trials": sum(d["new_defects"] > 0 for d in ds),
            "new_defects_total": sum(d["new_defects"] for d in ds),
        }
        for field in ("tokens", "wall_seconds"):
            xs = [d[field] for d in ds if number(d.get(field))]
            summary[field + "_known"] = len(xs)
            summary[field + "_mean"] = (
                sum(xs) / len(xs)
                if xs and len(xs) == len(ds) == len(cases) * repeats
                else None
            )
        arms[arm] = summary
    return {
        "valid_trials": len(valid),
        "expected_trials": len(cases) * repeats * 2,
        "paired_trials": len(pairs),
        "arms": arms,
        "quality_delta": sum(
            int(c["quality_pass"]) - int(b["quality_pass"]) for b, c in pairs
        )
        / len(pairs)
        if pairs
        else None,
        "round_delta_on_joint_success": sum(c["rounds"] - b["rounds"] for b, c in joint)
        / len(joint)
        if joint
        else None,
        "joint_success_pairs": len(joint),
    }


def compare(m, records, root):
    validate_manifest(m)
    counts = Counter(k for r in records if (k := slot(r)) is not None)
    expected = {
        (c["id"], a, i)
        for c in m["cases"]
        for a in m["arms"]
        for i in range(1, m["repeats"] + 1)
    }
    valid, invalid = [], []
    cases_by_id = {c["id"]: c for c in m["cases"]}
    for i, r in enumerate(records):
        k = slot(r)
        if k is not None and counts[k] > 1:
            invalid.append({"record": i, "reason": "duplicate-slot"})
            continue
        d, err = check_trial(r, m, root, cases_by_id)
        if err:
            invalid.append({"record": i, "reason": err})
        else:
            valid.append(d)
    out = summarize(valid, m["cases"], m["repeats"])
    out.update(
        {
            "version": 1,
            "missing_slots": len(expected - set(counts)),
            "duplicate_slots": sum(n > 1 for n in counts.values()),
            "invalid_records": invalid,
            "by_split": {},
            "limits": [
                "receipt consistency is not independent execution proof",
                "joint-success efficiency is conditional; examine paired quality and missing trials first",
            ],
        }
    )
    for split in sorted({c["split"] for c in m["cases"]}):
        cases = [c for c in m["cases"] if c["split"] == split]
        ids = {c["id"] for c in cases}
        out["by_split"][split] = summarize(
            [d for d in valid if d["case_id"] in ids], cases, m["repeats"]
        )
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    q = sub.add_parser("cohort")
    q.add_argument("ledger", type=Path)
    q = sub.add_parser("template")
    q.add_argument("loop")
    q = sub.add_parser("compare")
    q.add_argument("manifest", type=Path)
    q.add_argument("trials", type=Path)
    q.add_argument("--receipts", required=True, type=Path)
    args = p.parse_args()
    try:
        if args.command == "cohort":
            raw = read_bytes(args.ledger)
            rows = parse_jsonl(raw)
            if any(not isinstance(x, dict) for x in rows):
                raise DataError("ledger-nonobject")
            out = build_cohort(rows)
            out["source_sha256"] = hashlib.sha256(raw).hexdigest()
        elif args.command == "template":
            out = case_template(args.loop)
        else:
            raw = read_bytes(args.manifest, 1024 * 1024)
            trials = read_bytes(args.trials)
            out = compare(
                parse(decode(raw)),
                parse_jsonl(trials),
                args.receipts,
            )
            out["manifest_sha256"] = hashlib.sha256(raw).hexdigest()
            out["trials_sha256"] = hashlib.sha256(trials).hexdigest()
        print(render_json(out))
        return 0
    except DataError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
