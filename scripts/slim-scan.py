#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""slim-scan.py — 交付文字懸空引用掃描器(stdlib only)

掃 README/SKILL.md/reference.md,找出提及「精簡版已移除的指令」或「不交付的 skill」
的句子,輸出候選清單交人逐條裁。

★C1(2026-07-31 終審):也要掃產物 CLI 自己★——交付的不只是文件,`dist/scripts/lumos`
裡 warn()/print() 的字串常數一樣會叫接手者去跑不存在的指令(如「跑 lumos update 修
復」)。這類字串用 `--python` 旗標走 ast 模式:只掃 `ast.Constant` 的 str,不掃程式碼
識別字/註解——後者雜訊極高(實測純文字逐行掃全檔會把 `# [code-loop r1 ...]` 這類內部
審查註記也算命中,41 條裡 15 條是這種假陽性;ast 模式收斂到 11 條真信號)。產物檔名
(`lumos`)沒有 `.py` 副檔名,無法單靠副檔名自動判斷,故用明確旗標而非自動偵測。

★不是自動改寫器★:裸 token 形態必然有假陽性(export/set/show/loop/impact 等本身
是常見英文詞),故只出候選、不動檔案。

rc: 0=無候選 / 1=有候選 / 2=參數錯
"""
import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

# 不交付的 skill(含不帶 lumos- 前綴的簡稱)
DROP_SKILLS = ("lumos-design-loop", "lumos-code-loop", "lumos-core-knowledge",
               "lumos-pitfalls-gapfill", "design-loop", "code-loop",
               "core-knowledge", "pitfalls-gapfill")

KEEP = set("""append archive backlinks context contracts decision-add decision-reindex delguard query
decision-supersede decisions doctor export guard links lint map new recent
rel-cascade search set show stale stats sync-verified-by""".split())


def all_commands(lumos: Path):
    """真值取 --help 的 choices,不硬編。"""
    r = subprocess.run([sys.executable, str(lumos), "--help"],
                       capture_output=True, text=True)
    m = re.search(r"\{([a-z0-9,\-]+)\}", r.stdout)
    if not m:
        print("ERROR: 無法從 --help 解析指令全集", file=sys.stderr)
        sys.exit(2)
    return set(m.group(1).split(","))


def scan_line(line, removed):
    """回傳 [(token, form, pos), ...]。同一行可命中多種形態。

    ★pos 語意(2026-07-31 代碼審第二輪 minor-1)★:pos 是「觸發該規則的那個位置」,
    由判定邏輯本身回報,不是事後用 `.find(token)` 在整段文字裡重找。原本
    `_windowed_text()` 自己 `.find(token)` 猜位置的問題是:那是「找 token 第一次
    出現的子字串」,不是「scan_line 實際判定命中的位置」——token 常是別的詞的字首
    (如 install/update/init 常是 installer/updated/initial 的字首),那個「別的
    詞」若排在真命中詞前面就會誤導開窗,而且間距一拉大視窗就完全罩不到真命中詞。
    改成 scan_line 找到命中的當下就把位置一併回報,呼叫端不必也不該重猜。"""
    hits = []
    # 形態 1:帶前綴 —— pos = 被捕獲的 token 本身在 line 中的起點
    for m in re.finditer(r"(?:python3\s+)?(?:scripts/)?lumos\s+([a-z0-9\-]+)", line):
        if m.group(1) in removed:
            hits.append((m.group(1), "prefixed", m.start(1)))
    # 形態 2/4:backtick span —— 取首 token 比對(涵蓋「裸 token」與「帶參數」兩種)
    #   pos:token 只在反引號內的短 span 裡找,範圍夠小,.find() 在此不會重現
    #   「跨整段文字誤中別的詞」的那個 bug——再加上 m.start(1) 的偏移換回 line 座標。
    for m in re.finditer(r"`([^`]+)`", line):
        content = m.group(1)
        span = content.strip()
        first = span.split()[0] if span.split() else ""
        first = first.lstrip("/")
        if first in removed:
            off = content.find(first)
            pos = m.start(1) + (off if off != -1 else 0)
            hits.append((first, "bare-token" if span == first else "span-with-args", pos))
    # 形態 3:skill 名(含簡稱) —— pos = 該名稱在 line 中第一次出現的位置
    #   (判定條件本身就是「s in line」,第一次出現的位置就是觸發規則的位置,
    #   不存在「判定位置」與「.find() 找到的位置」不一致的問題)
    for s in DROP_SKILLS:
        if s in line:
            hits.append((s, "skill-name", line.find(s)))
            break
    # 形態 5:裸散文型 —— 無 backtick、無前綴,直接嵌在句子裡
    #   只認「有明確詞邊界」的出現,且該 token 不是保留指令
    #   ★邊界排除必須含路徑分隔與副檔名★:原本只排反引號/字母/連字號,
    #   `./install.sh`(前接 `/`)、`scripts/install-hooks.sh`(後接 `.sh`)這種
    #   「檔名」會被誤判成對指令 `install` 的散文引用——那是檔名不是指令引用。
    #   前瞻多加 `(?!\.\w)`(後接「.字母」=副檔名),後顧多加排 `/`(前接路徑分隔)。
    #   pos = re.search() 回報的 m.start() —— 就是判定條件本身命中的位置。
    for cmd in removed:
        if len(cmd) < 4:          # 太短的詞(如 gov)誤報率過高,交給形態 1/2
            continue
        m = re.search(r"(?<![`\w\-/])" + re.escape(cmd) + r"(?![\w\-])(?!\.\w)", line)
        if m and not any(h[0] == cmd for h in hits):
            hits.append((cmd, "prose", m.start()))
    return hits


def _windowed_text(norm, idx, token, width=120):
    """回傳以呼叫端已知的實際命中位置(idx,在 norm 座標系下)為中心的窗口。

    ★不得自己重猜命中位置★(2026-07-31 代碼審第二輪 minor-1):idx 必須是
    `scan_line()` 判定命中時回報的真實位置,經與 `norm`(即比對時用的正規化字串)
    對齊座標系傳入——本函式不再用 `.find(token)` 事後在 `norm` 裡重找,因為那會
    鎖到「token 第一次以子字串出現」的位置,不保證是實際觸發規則的那個位置(例:
    token 是另一個詞的字首,那個詞排在真命中詞前面就會誤導開窗)。"""
    if idx is None or idx < 0 or idx >= len(norm):
        return norm[:width]
    half = max(20, (width - len(token)) // 2)
    start = max(0, idx - half)
    end = min(len(norm), idx + len(token) + half)
    snippet = norm[start:end]
    if start > 0:
        snippet = "…" + snippet
    if end < len(norm):
        snippet = snippet + "…"
    return snippet[:width + 2]


def scan_python_file(fp, path: Path, removed):
    """ast 模式:只掃 `ast.Constant` 的 str(warn()/print() 訊息等),不掃程式碼識別
    字或註解——套用與 markdown 相同的 scan_line() 形態比對。多行字串常數(docstring)
    整段當一行餵給 scan_line(),行號取該常數的起始行(node.lineno);近似值,候選清單
    本來就是交人逐條裁,不要求精確到物理行。

    ★先正規化再掃描(2026-07-31 代碼審第二輪 minor-1)★:比對(scan_line)與開窗
    (_windowed_text)必須用同一份字串、同一套座標系——這裡先把 docstring 正規化
    (壓平空白)一次,拿正規化後的字串去比對,scan_line 回報的 pos 自然就是正規化
    座標系下的位置,直接餵給 _windowed_text,不必也不該再各自 strip()/重找。"""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            norm_val = " ".join(node.value.split())
            for tok, form, pos in scan_line(norm_val, removed):
                text = _windowed_text(norm_val, pos, tok)
                out.append({"file": fp, "line": node.lineno, "token": tok,
                            "form": form, "text": text})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--lumos", default=str(Path(__file__).resolve().parent / "lumos"))
    ap.add_argument("--python", action="store_true",
                     help="以 ast 模式掃檔案(只認 ast.Constant 的 str);"
                          "產物(如 dist/scripts/lumos)沒有 .py 副檔名,"
                          "無法自動判斷,須明講此旗標。.py 副檔名的檔案自動走此模式")
    a = ap.parse_args()

    removed = all_commands(Path(a.lumos)) - KEEP
    out = []
    for fp in a.files:
        p = Path(fp)
        if not p.is_file():
            print(f"ERROR: 檔案不存在: {fp}", file=sys.stderr)
            return 2
        if a.python or p.suffix == ".py":
            out.extend(scan_python_file(fp, p, removed))
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            norm_line = " ".join(line.split())
            for tok, form, pos in scan_line(norm_line, removed):
                out.append({"file": fp, "line": n, "token": tok, "form": form,
                            "text": _windowed_text(norm_line, pos, tok)})

    if a.json:
        print(json.dumps({"candidates": out, "total": len(out)}, ensure_ascii=False))
    else:
        for c in out:
            print(f"{c['file']}:{c['line']}  [{c['form']}] {c['token']}\n    {c['text']}")
        print(f"\n候選 {len(out)} 條 —— ★這是候選不是判決,裸 token 與散文型必有假陽性,請逐條裁★")
    return 1 if out else 0


if __name__ == "__main__":
    sys.exit(main())
