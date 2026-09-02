#!/usr/bin/env python3
"""規矩成對衝突的字面級初篩(Projects/世界repo掃描2026-09-02_調研 第 4 點;arXiv 2608.02639:遵循率崩跌主因是規則成對衝突)。

做法(純字串,不用模型;產出是給人/乾淨 agent 覆核的候選,不是判決):
  1. 掃 CLAUDE.md + skills/lumos-*/**/*.md + scripts/templates/*.md,切句(。;!?與換行)。
  2. 只留帶「指令性」字眼的句子(必須/一律/不要/不得/禁止/先…再/才准/上限/預設…)。
  3. 每句抽「談的是什麼」的關鍵詞:lumos 子指令、工具名、流程名、數字常數。
  4. 同一個關鍵詞底下,若同時有「正向要求」與「負向禁止」,或出現不同的數字常數 → 列為候選群。
輸出 markdown:每群列 file:line + 原句,人再判是真衝突、還是同一條規矩的兩面。

用法: governance/eval/rule_conflict_scan.py [--out 報告.md] [--min-group 2]
"""
import argparse, re, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DIRECTIVE = re.compile(r"必須|一律|不要|不得|禁止|不准|嚴禁|不能|不可|別再|別把|要先|先.{1,12}再|才准|才算|才能|預設|上限|至少|最多|不許|不應|應該|一定要|絕不|永遠|恆")
NEG = re.compile(r"不要|不得|禁止|不准|嚴禁|不能|不可|別再|別把|不許|不應|絕不|不算|不擋|不做|不推|不抄|不跑|不派|不開|不動")
POS = re.compile(r"必須|一律|要先|才准|才算|才能|一定要|應該|預設|永遠|恆|先.{1,12}再")
NUM = re.compile(r"(?<![A-Za-z])(\d+(?:\.\d+)?)\s*(pp|%|秒|分|輪|席|題|次|天|字元|行|步|K|k★|美元|\$)?")

# 「談的是什麼」:lumos 子指令、工具、流程、常見治理物件
TERMS = [
    r"lumos [a-z][a-z-]+", r"\bgrep\b", r"\brg\b", r"\bRead\b", r"\bEdit\b", r"\bWrite\b", r"\bAgent\b", r"\bSkill\b",
    r"WebSearch", r"Explore", r"git add", r"commit", r"push", r"pre-commit", r"pre-push", r"design-loop", r"code-loop",
    r"canary", r"K=\d", r"處置閘", r"Codex", r"Gemini", r"opus", r"sonnet", r"haiku", r"辯方", r"外家", r"REVISIT",
    r"doctor", r"\blint\b", r"impact", r"contracts", r"decision-add", r"regen", r"frontmatter", r"開頭欄位", r"summary",
    r"wikilink", r"合約", r"★INVARIANT★", r"\[test:\]", r"\[audit:\]", r"引句", r"quote-check", r"refcheck", r"seat-check",
    r"上限", r"cap", r"輪", r"席", r"探針", r"scenario", r"PRIOR-ART", r"白話", r"術語", r"file:line", r"沙盒", r"sandbox",
    r"--no-verify", r"LUMOS_SKIP", r"headless", r"claude -p", r"tier", r"high", r"blocker", r"major", r"minor", r"severity",
]
TERM_RE = re.compile("|".join(f"(?:{t})" for t in TERMS), re.I)


def iter_files():
    yield ROOT / "CLAUDE.md"
    for p in sorted((ROOT / "skills").glob("lumos-*/**/*.md")):
        yield p
    for p in sorted((ROOT / "scripts" / "templates").glob("*.md")):
        yield p


def sentences(text):
    """回 [(行號, 句子)];以句號/分號/驚嘆/問號/換行切,保留行號(取句子起點所在行)。"""
    out = []
    for ln_no, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if not s or s.startswith(("|--", "```", "<!--")):
            continue
        for part in re.split(r"[。;!?！？]", s):
            part = part.strip(" -*>|#\t")
            if len(part) >= 8:
                out.append((ln_no, part))
    return out


def scan(min_group=2):
    groups = defaultdict(list)   # term -> [(file, line, sentence, polarity, numbers)]
    total_directive = 0
    for f in iter_files():
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue   # r1 邊界席:非法 UTF-8(UnicodeDecodeError 是 ValueError 不是 OSError)也跳過,別讓一顆壞檔炸掉整支掃描
        rel = str(f.relative_to(ROOT))
        for ln, s in sentences(text):
            if not DIRECTIVE.search(s):
                continue
            total_directive += 1
            pol = ("neg" if NEG.search(s) else "") + ("pos" if POS.search(s) else "")
            nums = sorted({m.group(0).strip() for m in NUM.finditer(s) if m.group(1)})
            for t in {m.group(0).lower() for m in TERM_RE.finditer(s)}:
                groups[t].append((rel, ln, s, pol or "n/a", nums))
    cands = []
    for term, rows in groups.items():
        if len(rows) < min_group:
            continue
        pols = {r[3] for r in rows}
        has_neg = any("neg" in p for p in pols)
        has_pos = any("pos" in p for p in pols)
        numsets = {tuple(r[4]) for r in rows if r[4]}
        reason = []
        if has_neg and has_pos:
            reason.append("同一詞底下同時有正向要求與負向禁止")
        if len(numsets) >= 2:
            reason.append(f"出現 {len(numsets)} 組不同數字常數")
        if reason:
            cands.append((term, reason, rows))
    cands.sort(key=lambda c: -len(c[2]))
    return total_directive, cands


def render(total, cands):
    lines = ["# 規矩成對衝突字面級初篩", "",
             f"掃 CLAUDE.md + skills/lumos-* + scripts/templates;指令性句子 {total} 句;候選群 {len(cands)} 個(同詞下正負並存或數字不一致)。",
             "★這只是候選,大多會是同一條規矩的兩面(例:「必須先 X」與「不要跳過 X」)。要人或乾淨 agent 逐群判:真衝突 / 同面 / 不同對象。★", ""]
    for term, reason, rows in cands:
        lines.append(f"## `{term}` — {len(rows)} 句 — {';'.join(reason)}")
        for rel, ln, s, pol, nums in rows[:40]:
            tag = {"neg": "禁", "pos": "要", "negpos": "禁+要", "n/a": "—"}.get(pol, pol)
            lines.append(f"- [{tag}] `{rel}:{ln}` {s[:180]}" + (f"  〔數字 {' '.join(nums)}〕" if nums else ""))
        if len(rows) > 40:
            lines.append(f"- …另 {len(rows) - 40} 句略")
        lines.append("")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="")
    ap.add_argument("--min-group", type=int, default=2)
    a = ap.parse_args()
    total, cands = scan(a.min_group)
    md = render(total, cands)
    if a.out:
        Path(a.out).write_text(md, encoding="utf-8")
        print(f"指令性句子 {total};候選群 {len(cands)} → {a.out}")
    else:
        sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
