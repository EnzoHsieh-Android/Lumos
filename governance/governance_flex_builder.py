#!/usr/bin/env python3
"""把 AI 治理調研 JSON 轉成 LINE Flex Message（單張直式長卡）broadcast body"""
import json
import re
import sys


def text(t, **kw):
    return {"type": "text", "text": t, "wrap": True, **kw}


def sep(margin="lg"):
    return {"type": "separator", "margin": margin}


def section_title(t):
    return text(t, weight="bold", size="sm", color="#0F3D3E", margin="lg")


raw = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r"\{.*\}", raw, re.S)
if not m:
    sys.exit("調研 JSON 解析失敗：輸出中找不到 JSON")
r = json.loads(m.group(0))

body = [
    text("今日總覽", weight="bold", size="sm", color="#88AAAA"),
    text(r["overview"], size="sm", margin="sm"),
]

if r.get("loop_lens"):
    body.append(text("🔄 迴圈工程透鏡：" + r["loop_lens"], size="xs", color="#0F6B6E", margin="md"))

body.append(sep())
body.append(section_title("📄 今日精選"))
for i, a in enumerate(r.get("articles", [])[:6]):
    if i:
        body.append(sep("md"))
    body.append(text(a["title"], weight="bold", size="sm", margin="md"))
    body.append(text("來源：" + a.get("source", "未註明"), size="xxs", color="#999999"))
    body.append(text(a["summary"], size="xs", color="#555555", margin="sm"))
    body.append(text("💡 " + a["relevance"], size="xs", color="#0F6B6E", margin="sm"))

ins = r.get("inspirations", [])[:4]
if ins:
    body.append(sep())
    body.append(section_title("💡 可借鏡的靈感"))
    for i, s in enumerate(ins):
        body.append(text(f"{i + 1}. {s}", size="xs", color="#333333", margin="sm"))

gaps = r.get("gaps", [])[:3]
if gaps:
    body.append(sep())
    body.append(section_title("🛠 打磨建議（對照現有不足）"))
    for g in gaps:
        body.append(text("• " + g["weakness"], size="xs", weight="bold", color="#7A3030", margin="md"))
        body.append(text("↳ " + g["suggestion"], size="xs", color="#555555"))

if r.get("watch"):
    body.append(sep())
    body.append(text("👀 持續追蹤：" + r["watch"], size="xxs", color="#999999", margin="lg"))

bubble = {
    "type": "bubble",
    "size": "giga",
    "header": {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": "#0F3D3E",
        "paddingAll": "16px",
        "contents": [
            text(f"🔍 AI 治理調研 {r['date']}", weight="bold", color="#FFFFFF", size="md"),
            text("graph-as-contract × loop engineering 的每日打磨", size="xxs", color="#88AAAA", margin="sm"),
        ],
    },
    "body": {"type": "box", "layout": "vertical", "paddingAll": "16px", "contents": body},
}

payload = {
    "messages": [{
        "type": "flex",
        "altText": f"🔍 AI 治理調研 {r['date']}",
        "contents": bubble,
    }]
}
print(json.dumps(payload, ensure_ascii=False))
