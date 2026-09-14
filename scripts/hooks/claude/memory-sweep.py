#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 Enzo Hsieh
# SPDX-License-Identifier: MIT
# MIT licensed. Full text: scripts/lumos header, or LICENSE at
# https://github.com/EnzoHsieh-Android/Lumos
"""記憶過期清掃(SessionStart hook 版)。

會腐爛的記憶不是「舊的」,是「講當下狀態」的:某某還沒推、某某還沒裝、目前沒有某某。
這種宣稱會被任何事情推翻,而推翻它的那件事不會回來改那個檔——所以用時間當判準抓不到
(實測:記憶檔最後修改的中位數只有 6 天,它們常被改)。

做法借 memanto 的形狀、換掉觸發條件:每一條這種宣稱在開頭欄位自己帶一行可以跑的檢查,

    verify:
      - claim: 這篇宣稱的那句話
        cmd: 一行 shell;exit 0 代表宣稱★仍然成立★

清掃跑那些檢查,對不上的當場蓋章(status/stale_at/stale_by + 正文一行警告)。
★不刪內容、可復原;條件回復成立時下次清掃自己撤掉章。★

    memory-sweep.py                    只看,不動檔
    memory-sweep.py --write            蓋章
    memory-sweep.py --write --quiet --budget 8    hook 用:沒事就完全不出聲
    memory-sweep.py --restore <檔名>   撤掉某一篇的章
"""
import argparse
import datetime as dt
import os
import pathlib
import re
import subprocess
import sys
import time

MARK = "> ⚠ 這篇有宣稱已經對不上了（"

# ── 內層預算 ────────────────────────────────────────────────────────────────
# 外層天花板寫在註冊表、內層自己算。★內層一定要明顯小於外層★:內層 ≥ 外層的話,
# 「逾時就好好收尾」那條路結構上永遠跑不到——外面會先 SIGKILL,繞過所有 try/except。
# 這支的收尾動作是印出「還有幾條沒驗到」,跑不到就等於默默假裝驗過了。
_T0 = time.monotonic()
_OUTER = None


def _inner_budget(elapsed=None, default=10.0):
    """從現在到預算用完還剩幾秒(外層 × 0.7 − 已耗)。下限 1 秒。
    ★這是「還剩多少」不是「每段配額」★——連續呼叫兩次拿到的數字不該相加。"""
    total = (_OUTER if _OUTER else default) * 0.7
    used = elapsed if elapsed is not None else (time.monotonic() - _T0)
    return max(1.0, total - used)
PER_CMD_CAP = 15.0          # 單條檢查最多跑這麼久


# ── 影子副本偵測 ─────────────────────────────────────────────────────────────
# 這個專案有知識圖譜的話,「某某做到哪、推了沒」本來就該住在圖譜裡(那邊有狀態欄位、
# 回頭條件、健檢、提交前的閘)。記憶又抄一份=第二份真相,而且是沒有閘守的那一份。
# ★而且記憶是開場自動塞進視野的、圖譜要主動去查★——所以錯的那份反而先被讀到。
# 2026-09-14 實測:76 篇記憶裡 34 篇點名了圖譜節點,其中 30 篇是專案狀態。
_STATUS_WORDS = re.compile(
    r"(還沒推|未推|沒推|還沒裝|沒有裝|未裝|尚未|還沒做|目前沒有|進行中|建置中|待裁|未修|未解|未開工|交付狀態)")
# ★分隔符要列全★(2026-09-14 實踩):原本只排除空白/反引號/頓號/右括號/右方括號,
# 於是分號、引號、左括號都被當成節點名的一部分,吐出「…實作;09-15」這種查無的假壞指標。
# 一份有假陽性的清單沒人會信,跟沒有一樣。另外要求至少兩個字,排掉裸寫的 `Issues/`。
_NODE_REF = re.compile(
    r"(?:Projects|Systems|Issues|Verification)/([^\s`。,、;；:：()（）\[\]\"'／|]{2,})")


def graph_stems(start):
    """找這個專案的圖譜。回 (根目錄, 節點名集合);找不到回 (None, None)。"""
    d = pathlib.Path(start).resolve()
    for cand in [d] + list(d.parents):
        for g in sorted((cand / "docs").glob("*knowledge*")) if (cand / "docs").is_dir() else []:
            if g.is_dir():
                return g, {f.stem for f in g.rglob("*.md")}
        if (cand / ".git").exists():
            break
    return None, None


def shadow_copies(here, stems):
    """回 [(檔名, 點到的圖譜節點)]:點名了真的存在的圖譜節點、而且自己也在講狀態的。"""
    out = []
    for f in sorted(here.glob("*.md")):
        if f.name == "MEMORY.md":
            continue
        t = f.read_text(encoding="utf-8")
        body = t.split("---", 2)[2] if t.count("---") >= 2 else t
        # ★要能明說豁免★:一份永遠歸不了零的清單注定被當背景噪音(這個 repo 的空轉週報
        # 喊了 70 天沒人理就是這樣)。判過不是影子副本的,寫一行 shadow_ok 註明理由就下架,
        # 理由留在檔案裡供人反駁——不是靜靜消失。
        m_ok = re.search(r"(?m)^shadow_ok:[ \t]*(.+)$", t)
        if m_ok and len(m_ok.group(1).strip()) >= 4:
            continue
        words = sorted(set(_STATUS_WORDS.findall(body)))
        if not words:
            continue
        hit = sorted({_stem(n) for n in _NODE_REF.findall(t)} & stems)
        if hit:
            # ★要印出是哪個字觸發的★:只給檔名不給理由的話,看的人得自己重讀整篇找,
            # 成本一高就沒人動——今天早上那份空轉週報就是這樣躺了 70 天。
            out.append((f.name, hit[:2], words[:4]))
    return out


# ── 指標健康與狀態打架 ──────────────────────────────────────────────────────
# 業界做法(Oracle 兩層模式 / CoALA 語意記憶歸真相層):記憶是衍生層,只能回答「去哪裡查」,
# 不能回答「是什麼」。衍生層的兩種壞法都要能被機械抓到:
#   ① 壞指標——指到一個已經不存在(或改名)的圖譜節點。指標壞了,記憶就變成孤立的斷言。
#   ② 狀態打架——記憶說「還沒做」而那個節點 status 已經是 done(或反過來)。
#      ★衝突要浮上來,不要靜靜挑一個★:這支只喊,不替任何一邊決定誰對。
_LINKED_REF = re.compile(r"\[\[([^\]|#]+)\]\]")

def _stem(name):
    """去掉結尾的 .md。★不能用 rstrip(".md")★——那是「刪掉結尾所有屬於 . m d 的字元」,
    會把 shared-worktree-git-add-hazard 削成 …hazar(2026-09-14 實踩,吐出一串查無的假壞指標)。"""
    return name[:-3] if name.endswith(".md") else name

_DONE_WORDS = re.compile(r"(還沒做|未開工|進行中|建置中|尚未|還沒推|未推|沒推)")
_LIVE_WORDS = re.compile(r"(已交付|全交付|已完成|已收案|落地完成)")


def node_status(graph_root, stem):
    """讀某個圖譜節點開頭欄位的 status;讀不到回 None。"""
    for f in graph_root.rglob(stem + ".md"):
        head = f.read_text(encoding="utf-8", errors="replace")[:1200]
        m = re.search(r"(?m)^status:[ \t]*([A-Za-z_-]+)", head)
        return m.group(1) if m else None
    return None


def pointer_problems(here, graph_root, stems):
    """回 [(檔名, 種類, 細節)]:壞指標與狀態打架。"""
    out = []
    mem_stems = {p.stem for p in here.glob("*.md")}
    for f in sorted(here.glob("*.md")):
        if f.name == "MEMORY.md":
            continue
        t = f.read_text(encoding="utf-8")
        body = t.split("---", 2)[2] if t.count("---") >= 2 else t
        named = {_stem(n) for n in _NODE_REF.findall(t)}
        # ★壞指標只認寫成 [[…]] 的★:散文裡順口提到「像 Issues/金額計算 那種」不是承諾,
        # 拿它當壞指標就會製造假陽性,而一份有假陽性的清單沒人會信。
        linked = {_stem(n.split("/")[-1]) for n in _LINKED_REF.findall(t)}
        # ★記憶之間也用 [[…]] 互連★(2026-09-14 第三次修這支偵測):扣掉記憶檔自己的名字,
        # 否則每一條「相關:[[某篇記憶]]」都會被報成壞指標——整份清單瞬間全是雜訊。
        dead = sorted(n for n in linked if n not in stems and n not in mem_stems)
        if dead:
            out.append((f.name, "指到不存在的節點", "、".join(dead[:3])))
        for n in sorted(named & stems):
            st = node_status(graph_root, n)
            if st == "done" and _DONE_WORDS.search(body):
                out.append((f.name, "說還沒做,但節點已 done", n))
            elif st in ("doing", "open") and _LIVE_WORDS.search(body):
                out.append((f.name, "說已交付,但節點還是 " + st, n))
    return out


def memory_dir(explicit=None):
    """找這個專案的記憶目錄。Claude Code 的慣例=絕對路徑把 / 換成 -。"""
    if explicit:
        return pathlib.Path(explicit).expanduser()
    slug = str(pathlib.Path.cwd().resolve()).replace("/", "-")
    return pathlib.Path.home() / ".claude" / "projects" / slug / "memory"


def verify_blocks(text):
    m = re.search(r"(?m)^verify:\n((?:[ ]+.*\n)+)", text)   # 同上:不可開 DOTALL
    if not m:
        return []
    out, claim = [], None
    for line in m.group(1).splitlines():
        s = line.strip()
        if s.startswith("- claim:"):
            claim = s[len("- claim:"):].strip()
        elif s.startswith("cmd:") and claim is not None:
            out.append((claim, s[len("cmd:"):].strip()))
            claim = None
    return out


def run_check(cmd, timeout):
    """exit 0 = 宣稱仍成立。逾時/壞命令回 None=驗不了,★不判死★。"""
    if timeout <= 0:
        return None
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, timeout=timeout)
    except (subprocess.TimeoutExpired, OSError):
        return None
    return r.returncode == 0


def stamp(text, failed, today):
    text = re.sub(r"(?m)^  (status|stale_at|stale_by): .*\n", "", text)
    # ★不要錨在 modified 上★(2026-09-14 實踩):手寫的記憶檔沒有那一欄,錨不到就整段不插,
    # 但正文那行警告照樣加——章只蓋一半,而撤章看的是開頭欄位,於是永遠撤不掉。
    fields = "  status: stale\n  stale_at: %s\n  stale_by: %s\n" % (
        today, "｜".join(c[:40] for c in failed))
    # ★只能開 MULTILINE,不能開 DOTALL★(2026-09-14 實踩):開了 DOTALL 的話 .* 會吃換行,
    # 這段會一路吃到檔尾,欄位就被插到檔案最後面——正文的警告有、開頭的章沒有,又是半套。
    m = re.search(r"(?m)^metadata:[ \t]*\n((?:[ ]+.*\n)*)", text)
    if m:
        text = text[:m.end()] + fields + text[m.end():]
    else:
        i = text.index("---", text.index("---") + 3)
        text = text[:i] + fields + text[i:]
    body_at = text.index("---", text.index("---") + 3) + 3
    head, body = text[:body_at], text[body_at:]
    body = re.sub(r"(?m)^%s.*\n\n?" % re.escape(MARK), "", body)
    warn = (MARK + today + "）：**" + "**、**".join(failed)
            + "**。內容留著沒刪，但引用之前先自己查一次。\n\n")
    return head + "\n" + warn + body.lstrip("\n")


def is_stamped(text):
    """這篇有沒有被蓋過章。★只認行首的欄位與行首的警告行★——用子字串比對的話,
    「說明這個機制」的那篇記憶正文裡寫到 status: stale 這幾個字就會被當成蓋過章,
    於是它永遠處在「原本蓋過章、現在又成立了」的狀態,每次開場都吵一次(2026-09-14 實踩)。"""
    return bool(re.search(r"(?m)^  status: stale[ \t]*$", text)
                or re.search(r"(?m)^%s" % re.escape(MARK), text))


def unstamp(text):
    text = re.sub(r"(?m)^  (status|stale_at|stale_by): .*\n", "", text)
    # ★只吃掉警告那一行,不要連後面的空行一起吃★:吃掉的話撤章之後開頭欄位跟正文之間
    # 就沒有空行了,蓋章→撤章不是原樣還原。這種小失真每次來回都會累積。
    return re.sub(r"(?m)^%s.*\n" % re.escape(MARK), "", text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="沒有任何變化就完全不出聲(hook 用)")
    ap.add_argument("--budget", type=float, default=0, help="整支最多跑幾秒;0=不限")
    ap.add_argument("--dir", help="指定記憶目錄(預設從目前目錄推出來)")
    ap.add_argument("--restore", metavar="檔名")
    # 安裝器對 Codex 那一家會多帶 --harness codex;不認得的旗標會讓 argparse 直接死,
    # hook 就整支失敗了。收下但不用它——這支對兩家做的事一樣。
    ap.add_argument("--harness", default="claude")
    a = ap.parse_args()
    here = memory_dir(a.dir)
    if not here.is_dir():
        return 0                                   # 這個專案沒有記憶目錄,安靜退出
    today = dt.date.today().isoformat()

    if a.restore:
        f = here / a.restore
        f.write_text(unstamp(f.read_text(encoding="utf-8")), encoding="utf-8")
        print("撤掉蓋章:" + a.restore)
        return 0

    global _OUTER
    _OUTER = a.budget or None
    deadline = (time.monotonic() + _inner_budget()) if a.budget else None
    lines, newly_stale, recovered, unknown_n, skipped, checked = [], 0, 0, 0, 0, 0
    for f in sorted(here.glob("*.md")):
        if f.name == "MEMORY.md":
            continue
        text = f.read_text(encoding="utf-8")
        blocks = verify_blocks(text)
        if not blocks:
            continue
        failed, unknown = [], []
        for claim, cmd in blocks:
            left = (deadline - time.monotonic()) if deadline else PER_CMD_CAP
            if deadline and left <= 0:
                skipped += 1
                continue
            checked += 1
            ok = run_check(cmd, min(left, PER_CMD_CAP))
            if ok is None:
                unknown.append(claim); unknown_n += 1
            elif not ok:
                failed.append(claim)
        # ★只認行首的欄位與行首的警告行★(2026-09-14 實踩):用子字串比對的話,
        # 「說明這個機制」的那篇記憶正文裡寫到 status: stale 這幾個字,就會被當成蓋過章。
        was = is_stamped(text)
        if failed:
            if not was:
                newly_stale += 1
            lines.append("✗ %s" % f.name)
            for c in failed:
                lines.append("    對不上了:%s" % c)
            if a.write:
                f.write_text(stamp(text, failed, today), encoding="utf-8")
        elif was and not unknown:
            recovered += 1
            lines.append("✓ %s(原本蓋過章,現在又成立了,已撤掉)" % f.name)
            if a.write:
                f.write_text(unstamp(text), encoding="utf-8")
        for c in unknown:
            lines.append("? %s 這條驗不了(命令壞了或逾時):%s" % (f.name, c))

    shadows = []
    graph_root, stems = graph_stems(pathlib.Path.cwd())
    ptr = []
    if stems:
        shadows = shadow_copies(here, stems)
        ptr = pointer_problems(here, graph_root, stems)
    if ptr:
        lines.append("★記憶跟圖譜對不上(衝突只喊、不替任何一邊決定誰對)★:")
        for n, kind, detail in ptr:
            lines.append("    %s  %s:%s" % (n, kind, detail))
    if shadows:
        lines.append("★下面這幾篇在記狀態,而圖譜裡已經有一份(記憶該指路,不該抄)★:")
        for n, nodes, words in shadows:
            lines.append("    %s  (踩到:%s) → %s" % (n, "、".join(words), "、".join(nodes)))

    changed = newly_stale or recovered or unknown_n or skipped or shadows or ptr
    if a.quiet and not changed:
        return 0
    if lines:
        print("記憶過期清掃:")
        for l in lines:
            print("  " + l)
    if skipped:
        print("  ★時間預算用完,還有 %d 條沒驗到——沒驗到不等於成立。★" % skipped)
    if not a.quiet:
        print("跑了 %d 條檢查%s。" % (checked, "(已蓋章)" if a.write else "(只看)"))
    return 0                                        # hook 不因為有過期就讓 session 失敗


if __name__ == "__main__":
    sys.exit(main())
