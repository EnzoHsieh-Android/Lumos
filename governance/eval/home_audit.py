#!/usr/bin/env python3
"""家的品質抽查(Projects/推筆記認家_計劃 [S14])。

白話:「每支檔有家」只驗路徑對不對,不驗那篇是不是真的在講這支檔。認家上線之後,家一定會被推到
改檔的人眼前——填錯的家就等於把無關的筆記推上來。這支腳本把「檔 → 家」的配對抽出來、排好,
讓審查員逐對判「這篇是不是在講這支檔負責的事」,再由人過目算錯誤率。

兩個子指令:

  sample --vault <圖譜資料夾> --seed <數字> [--n <幾對>] [--out <檔>]
      抽出配對,每對附那篇的摘要 KEY 行、那支檔開頭 40 行。同一個種子抽出同一批。
      不給 --n 就是全部配對。輸出 JSON(給審查員讀、也給 tally 讀)。

  tally <判定檔> [--ruling <人裁檔>]
      判定檔 = sample 的輸出再填上每對的 verdict(是 / 否 / 判不準)。
      照「否、判不準、是」排序印成人裁清單(一對一行)。
      給了人裁檔就另外算錯誤率:人裁確認判錯的配對 ÷ 總配對。人裁檔是 JSON,
      {"wrong": ["<配對 id>", …]} 或 {"<配對 id>": "wrong|ok", …} 都吃。

零依賴,家對照表直接呼叫 lumos 裡那支唯一的算法([S1]),不另寫一份。
"""
import argparse
import importlib.util
import json
import random
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LUMOS = ROOT / "scripts" / "lumos"
HEAD_LINES = 40
ORDER = {"否": 0, "判不準": 1, "是": 2}


def load_lumos(path=None):
    """載入主程式。★--lumos 只收專案內的路徑★——這支腳本會把它當程式執行,
    收任意路徑等於多開一條「執行外面的檔」的口子(代碼審 r1 資安席);這裡收窄成縱深防禦。"""
    if path is not None:
        inside = safe_under(ROOT, Path(path))
        if inside is None or not inside.is_file():
            print(f"--lumos 只能指專案裡的檔,而且要存在:{path}", file=sys.stderr)
            raise SystemExit(2)
        path = inside
    p = str(path or LUMOS)
    spec = importlib.util.spec_from_file_location("lm_home_audit", p, loader=SourceFileLoader("lm_home_audit", p))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def key_line(summary):
    """那篇摘要裡的 KEY 行(沒有就退回摘要第一行);審查員靠它一眼看出這篇在講什麼。"""
    lines = [l.strip() for l in str(summary or "").splitlines() if l.strip()]
    for l in lines:
        if l.startswith("KEY:"):
            return l
    return lines[0] if lines else ""


def head_of(path, n=HEAD_LINES):
    """那支檔的開頭 n 行。★不要用 next(fh) 配生成式★:不到 n 行的檔會丟 StopIteration,
    而生成式裡的 StopIteration 從 Python 3.7 起會變成 RuntimeError 整支腳本掛掉——
    圖譜裡短檔很多,第一次真跑就踩到。islice 沒有這個問題。"""
    from itertools import islice
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return "".join(islice(fh, n))
    except OSError as e:
        return f"(讀不到:{e.__class__.__name__})"


def collect_pairs(vault, lumos_path=None):
    """圖譜裡所有「檔 → 家」配對,照檔名、節點名排序(抽樣前的順序固定,種子才有意義)。

    ★用主程式那支唯一的家對照表函式★:第一版自己包了一層轉接器繞去另一個入口,
    等於同一件事開了第二條路——代碼審 r1 架構席判 major。
    """
    m = load_lumos(lumos_path)
    env = m.Env(Path(vault))
    homes, _own = m._impact_home_map(env)
    out = []
    for f in sorted(homes):
        for node in sorted(homes[f]):
            out.append({"file": f, "node": node})
    return out, env


def safe_under(repo, rel):
    """rel 解出來還在 repo 裡才回絕對路徑,否則回 None。

    ★圖譜筆記的 about_code 不是可信輸入★:那是 .md 檔裡的一行字,手改就能寫成 `../../..` 或絕對路徑。
    寫入端(lumos 的指令)有擋,讀取端只做字面正規化——這支腳本會把讀到的內容原樣寫進會被提交的 JSON,
    所以讀之前要自己再驗一次(代碼審 r1 資安席實測:能讀到 repo 外的檔並外洩進版控)。
    """
    try:
        base = Path(repo).resolve()
        p = (base / rel).resolve()
        p.relative_to(base)
        return p
    except (ValueError, OSError):
        return None


def cmd_sample(args):
    pairs, env = collect_pairs(args.vault, args.lumos)
    if not pairs:
        print("這個圖譜裡沒有任何「檔 → 家」配對——about_code 都是空的?", file=sys.stderr)
        return 2
    if args.n is not None and args.n < 0:
        print(f"--n 要是 0 以上的整數(0 或不給=全部),你給的是 {args.n}", file=sys.stderr)
        return 2
    picked = list(pairs)
    if args.n and args.n < len(picked):
        picked = random.Random(args.seed).sample(picked, args.n)
        picked.sort(key=lambda p: (p["file"], p["node"]))
    repo = Path(args.repo) if args.repo else Path(args.vault).resolve().parents[1]
    rows, outside = [], []
    for i, p in enumerate(picked, 1):
        note = env.notes.get(p["node"])
        target = safe_under(repo, p["file"])
        if target is None:
            outside.append(f"{p['node']} ← {p['file']}")
            head = "(這一項的路徑跑出專案外面,沒有讀它——請去那篇把 about_code 改對)"
        else:
            head = head_of(target)
        rows.append({"id": f"p{i:03d}", "file": p["file"], "node": p["node"],
                     "key": key_line(note.fields.get("summary") if note else ""),
                     "head": head,
                     "verdict": ""})
    out = {"seed": args.seed, "vault": str(args.vault), "total_pairs": len(pairs),
           "注意": "每一對的 head 是那支檔開頭幾行的原文。這份檔會被人讀、也常被提交進版控——"
                   "存檔前自己看一眼有沒有把不該外流的東西抄進來。",
           "pairs": rows}
    text = json.dumps(out, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(f"抽了 {len(rows)} 對(全部 {len(pairs)} 對,種子 {args.seed}),寫到 {args.out}")
        print("審查員逐對填 verdict:是 / 否 / 判不準,填完跑 tally。")
        print("這份檔帶著各支檔開頭幾行的原文,提交前自己看一眼有沒有抄到不該外流的東西。")
    else:
        print(text)
    # ★警告走 stderr,報告照印★——第一版把這段的 else 接到了 outside 上,結果只要有一對越界,
    # 整份報告(含其餘合法配對)就從 stdout 消失、退出碼還是 0,人看不到也不知道不見了(代碼審 r2 正確性席)。
    if outside:
        print(f"⚠ 有 {len(outside)} 對的路徑跑出專案外面,沒有讀它們的內容(其餘照常抽):", file=sys.stderr)
        for x in outside[:10]:
            print(f"    {x}", file=sys.stderr)
        print("  那幾篇的 about_code 寫錯了(或被人動過手腳),去那篇改對:", file=sys.stderr)
        print("    lumos remove <節點> about_code <那個路徑>", file=sys.stderr)
    return 0


def _ruling_wrong(path):
    """人裁檔 → 判錯的配對 id 集合。吃兩種寫法:{"wrong":[…]} 或 {id: "wrong|ok"}。"""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("wrong"), list):
        return {str(x) for x in data["wrong"]}
    return {str(k) for k, v in data.items() if str(v).strip() in ("wrong", "否", "判錯")}


def cmd_tally(args):
    data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    rows = data.get("pairs", [])
    if not rows:
        print("判定檔裡沒有配對", file=sys.stderr)
        return 2
    missing = [r["id"] for r in rows if str(r.get("verdict", "")).strip() not in ORDER]
    rows.sort(key=lambda r: (ORDER.get(str(r.get("verdict", "")).strip(), 3), r["file"], r["node"]))
    counts = {k: 0 for k in ORDER}
    for r in rows:
        v = str(r.get("verdict", "")).strip()
        if v in counts:
            counts[v] += 1
    print(f"審查員判完 {len(rows) - len(missing)}/{len(rows)} 對:"
          f"判「否」{counts['否']} 對、判「不準」{counts['判不準']} 對、判「是」{counts['是']} 對。")
    if missing:
        print(f"還有 {len(missing)} 對沒填判定:{'、'.join(missing[:10])}{' …' if len(missing) > 10 else ''}")
    print("下面照「否、判不準、是」排,人從上往下看(一對一行):")
    wrong = _ruling_wrong(args.ruling) if args.ruling else None
    if wrong is not None:
        ids = {r["id"] for r in rows}
        stray = sorted(wrong - ids)
        if stray:
            print(f"擋下:人裁檔裡有 {len(stray)} 個編號不在這批配對裡:{'、'.join(stray[:10])}"
                  f"{' …' if len(stray) > 10 else ''}", file=sys.stderr)
            print("  最常見的原因是人裁檔跟判定檔不是同一輪抽的——那樣算出來的錯誤率會超過 100%,"
                  "看起來卻像個正常數字。確認兩份是同一批再跑一次。", file=sys.stderr)
            return 2
    for r in rows:
        mark = "" if wrong is None else ("  ← 人裁:判錯" if r["id"] in wrong else "")
        print(f"  [{str(r.get('verdict', '')).strip() or '未填'}] {r['id']}  {r['file']}  ←  "
              f"{r['node']}  {r.get('key', '')[:60]}{mark}")
    if wrong is not None:
        rate = len(wrong) / len(rows)
        print(f"錯誤率 = 人裁確認判錯的 {len(wrong)} 對 ÷ 總共 {len(rows)} 對 = {rate:.1%}"
              f"({'超過一成,先修家再上線' if rate > 0.10 else '沒超過一成'})。")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="家的品質抽查(檔 → 家 的配對要不要人裁)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample", help="抽出配對給審查員判")
    s.add_argument("--vault", required=True, help="圖譜資料夾(docs/*-knowledge)")
    s.add_argument("--seed", type=int, required=True, help="抽樣種子:同一個種子抽出同一批")
    s.add_argument("--n", type=int, default=None, help="抽幾對(不給=全部)")
    s.add_argument("--out", default=None, help="寫到哪個檔(不給=印出來)")
    s.add_argument("--repo", default=None, help="程式檔的根(不給=圖譜往上兩層)")
    s.add_argument("--lumos", default=None, help="lumos 主程式路徑(測試用)")
    s.set_defaults(func=cmd_sample)
    t = sub.add_parser("tally", help="讀審查員的判定,排成人裁清單")
    t.add_argument("file", help="填好 verdict 的判定檔")
    t.add_argument("--ruling", default=None, help="人裁檔:哪幾對確認判錯")
    t.set_defaults(func=cmd_tally)
    a = ap.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
