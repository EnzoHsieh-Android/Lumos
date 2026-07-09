"""風險分級器(risk-tiered-review):關鍵詞 → tier(high/standard)。
零依賴、純函數、二值確定性(無權重/計分/閾值)。量的是「表面類別」非難度——
分級是 proxy,漏網靠 canary/cross-family/人工 review 兜底(設計 doc 天花板 1)。
設計:docs/design/2026-07-03-risk-tiered-review.md。"""
import re

RISK_CLASSES = {
    "payment": ["金流", "payment", "stripe", "billing", "退款", "refund", "扣款"],
    "external-send": ["寄送", "送出", r"\bsend\b", "webhook", "notify",
                      "LINE 推送", r"\bmail\b", "簡訊", "對外"],
    "prod-irreversible": [r"\bprod\b", "production", "遷移", "migration",
                          "不可逆", "DROP TABLE", "DELETE FROM", "上架"],
    "self-governance": ["錨點", "anchor verify", "收斂判準", "canary",
                        "審計閘", "pre-push hook"],
}
_COMPILED = {cls: [re.compile(p, re.IGNORECASE) for p in pats]
             for cls, pats in RISK_CLASSES.items()}

_BLACKLIST = ("方案評比", "canary 相容性", "誠實天花板", "審計修正紀錄")
_INLINE_CODE = re.compile(r"`[^`\n]*`")
_FILENAME = re.compile(r"[\w\-./]+\.(?:md|py|sh|json|yml|yaml|txt)\b")


def assess(text):
    """任一類命中 → high;每類記首個命中(class/pattern/excerpt)。"""
    hits = []
    for cls, pats in _COMPILED.items():
        for pat in pats:
            m = pat.search(text)
            if m:
                s = max(0, m.start() - 20)
                hits.append({"class": cls, "pattern": pat.pattern,
                             "excerpt": text[s:m.end() + 20].replace("\n", " ")})
                break
    return {"tier": "high" if hits else "standard", "hits": hits}


def assess_spec(md_text):
    """spec 文本入口:## 切分 → 黑名單剝除樣板節(其餘含前提節一律保留)→
    防呆回退 → 剝 inline-code 與檔名 → assess。剝除方向=偏嚴(over-fire)。"""
    parts = re.split(r"(?m)^(## .*)$", md_text)
    kept = [parts[0]] if parts and parts[0].strip() else []
    n_sections = 0
    i = 1
    while i + 1 <= len(parts):
        title, body = parts[i], parts[i + 1]
        if not any(b in title for b in _BLACKLIST):
            kept.append(title + body)
            n_sections += 1
        i += 2
    corpus = "\n".join(kept)
    if n_sections < 2 or len(corpus) < 200:
        print("⚠ assess_spec: 剝除後餘文近空(節數<2 或字元<200),回退全文 assess(偏嚴)")
        corpus = md_text
    corpus = _INLINE_CODE.sub(" ", corpus)
    corpus = _FILENAME.sub(" ", corpus)
    return assess(corpus)


def params(tier):
    """high 的 maxr 語意=下限 8(max(維運 MAXR, 8) 由 wrapper 端整數比較實現)。
    panel_width(loop 三輪壓縮):tier 驅動平行審計員數(high=5/standard=3);
    既有 need/maxr 消費端多一鍵不受影響。"""
    return ({"need": 3, "maxr": 8, "panel_width": 5} if tier == "high"
            else {"need": 2, "maxr": 6, "panel_width": 3})
