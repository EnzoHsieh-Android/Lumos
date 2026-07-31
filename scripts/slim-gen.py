#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""slim-gen.py — 從單檔 CLI 生成「只留白名單指令」的精簡版(stdlib only)

★移除謂詞不是「cmd_ 前綴」★(lint-watch 實作叫 _lint_watch_mode、保留的 doctor
叫 run_doctor)——正解是「保留指令 dispatch 的 AST 可達性閉包之補集」。

★root 集合必須含 module-level 語句與 class body★,否則 `_SKILLS = _skills_list()`
這種模組層賦值會讓 helper 落進補集,產物 import 期就 NameError 全滅。
"""
import argparse
import ast
import re
import sys
from pathlib import Path

DEFAULT_KEEP = """append archive backlinks context contracts decision-add decision-reindex
decision-supersede decisions doctor export guard links lint map new recent
rel-cascade search set show stale stats sync-verified-by""".split()


def _called(node, universe):
    out = set()
    for c in ast.walk(node):
        if isinstance(c, ast.Call) and isinstance(c.func, ast.Name):
            out.add(c.func.id)
        elif isinstance(c, ast.Name) and isinstance(c.ctx, ast.Load) and c.id in universe:
            out.add(c.id)            # 函式當一級物件傳遞
    return out & universe


def _is_args_cmd(node):
    return (isinstance(node, ast.Attribute) and node.attr == "cmd"
            and isinstance(node.value, ast.Name) and node.value.id == "args")


def _cmd_names(test):
    """從 dispatch if 條件抽出『真正被比較的指令名』:只認 args.cmd == "x" /
    args.cmd in ("x","y") 這兩種形狀。
    ★不能撿條件裡出現的任何字串常數★——像
    `if args.cmd == "loop" and args.lcmd == "capture-counts":` 這種混了巢狀
    dest(args.lcmd)的複合條件,若把 "capture-counts" 也當指令名撿進來,會讓
    「條件裡的指令名全部屬移除清單才砍」的判準失真(多一個不相干字串,ns 不
    再是 removed 子集,該砍的分支砍不掉,留下呼叫已被砍函式的 dangling handler)。"""
    out = set()
    for n in ast.walk(test):
        if not isinstance(n, ast.Compare) or len(n.ops) != 1:
            continue
        left, op, right = n.left, n.ops[0], n.comparators[0]
        if not _is_args_cmd(left):
            continue
        if isinstance(op, ast.Eq) and isinstance(right, ast.Constant) and isinstance(right.value, str):
            out.add(right.value)
        elif isinstance(op, ast.In) and isinstance(right, (ast.Tuple, ast.List, ast.Set)):
            out |= {e.value for e in right.elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)}
    return out


def build(src_text, keep):
    tree = ast.parse(src_text)
    funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    main = funcs.get("main")
    if main is None:
        raise SystemExit("ERROR: 找不到 main()")

    roots = set()
    # root ①:保留指令的 dispatch 分支
    for node in ast.walk(main):
        if isinstance(node, ast.If):
            ns = _cmd_names(node.test)
            if ns and (ns & set(keep)):
                for st in node.body:
                    roots |= _called(st, set(funcs))
    # root ②:module-level 語句與 class body(★不可省★)
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            roots |= _called(node, set(funcs))
    # root ③:main() 內、dispatch if 鏈以外的『必經』頂層陳述式(★不可省★)——
    # 例如 `vault = args.vault or find_vault(...)` / `env = Env(vault)`:這兩行
    # 夾在 dispatch if 之間、對「所有」指令都會跑,但既不在任何保留分支的 If.body
    # 底下(root①漏)、也不是 module-level(root②漏)。漏了這條,find_vault/Env
    # 這類共用 spine 函式會被判定不可達而砍掉,產物在跑實際指令時
    # NameError——而且 --help 測不到(argparse 印完 help 就退出,根本沒跑到這裡),
    # dangling-handler 檢查也測不到(它們不是 cmd_/run_/_ 前綴)。
    for node in main.body:
        if isinstance(node, ast.If) and _cmd_names(node.test):
            continue   # dispatch 分支,由 root① 依 keep 篩選,這裡不重複收
        roots |= _called(node, set(funcs))
    roots |= _called(main, set(funcs)) & {"main"}
    roots.add("main")

    # ★main 不可進閉包展開的 stack★:main() body 內含「全部指令」的 dispatch if
    # (包含要移除的分支),若對 main 本身跑無限制的 _called(整函式 ast.walk),
    # 會把移除分支裡呼叫的 handler 一併撿回 roots——root①的限縮形同虛設。
    # main 呼叫誰"該留"已由 root①(僅掃保留分支)精準決定,這裡只需讓 main
    # 自己留在 seen(輸出仍要它),不需要、也不能再展開它。
    seen = set(roots)
    stack = [r for r in roots if r != "main"]
    while stack:
        f = stack.pop()
        for g in _called(funcs[f], set(funcs)):
            if g not in seen:
                seen.add(g); stack.append(g)
    drop = set(funcs) - seen
    return tree, funcs, seen, drop


def _first_const(e):
    """迴圈註冊元素 ('name','help') → 'name';非此形狀回 None。"""
    if isinstance(e, ast.Tuple) and e.elts and isinstance(e.elts[0], ast.Constant):
        v = e.elts[0].value
        return v if isinstance(v, str) else None
    if isinstance(e, ast.Constant) and isinstance(e.value, str):
        return e.value
    return None


def _is_registration_loop(n, top_var=None):
    """for 迴圈的 body 是不是真的呼叫 <receiver>.add_parser(<迴圈目標變數>, ...)。
    ★不能只看 iter 是不是常數字串 tuple★:12000 行檔案裡一堆商業邏輯也長
    `for key in ("verified_by","plan_refs","core_refs"):` 這種形狀(單純迭代
    欄位名,body 完全不碰 argparse)。沒有這道 gate,那種迴圈會被誤判成「指
    令迴圈註冊」,連帶把 "verified_by" 這種欄位名算進 removed 指令集,砍穿
    別的保留函式內的 if 分支、刪出語法洞(實測案例:cmd_sync_verified_by 的
    try/except 被砍空)。

    ★top_var 限定同樣重要(2026-07-31 審查揪出的缺陷)★:receiver 必須是頂層
    subparsers 變數(top_var),不然一個被保留的指令若用迴圈註冊「自己的」巢狀
    子指令(例如 `osub = p2.add_subparsers(...)` 後 `for n,h in (...):
    osub.add_parser(n, help=h)`),body 形狀跟頂層迴圈註冊一模一樣、但迭代出來
    的是巢狀子指令名(不在頂層 keep 名單裡)。若不限 receiver,呼叫端會把這種
    巢狀迴圈也判成「頂層指令迴圈」,拿巢狀子指令名去跟頂層 keep 比對——當然
    找不到,於是整段迴圈被砍空,即使外層指令本身在保留清單裡。
    top_var=None 時退回不限 receiver(舊行為,供未持有 top_var 語境時使用)。"""
    targets = set()
    if isinstance(n.target, ast.Name):
        targets.add(n.target.id)
    elif isinstance(n.target, ast.Tuple):
        for e in n.target.elts:
            if isinstance(e, ast.Name):
                targets.add(e.id)
    if not targets:
        return False
    for c in ast.walk(n):
        if (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                and c.func.attr == "add_parser" and c.args
                and isinstance(c.args[0], ast.Name) and c.args[0].id in targets):
            if top_var is not None:
                if not (isinstance(c.func.value, ast.Name) and c.func.value.id == top_var):
                    continue
            return True
    return False


def _add_parser_name(node, top_var=None):
    """Assign/Expr 是不是 <top_var>.add_parser("<cmd>", ...);是則回 cmd。
    top_var=None 時不限 receiver(舊行為,供內部 allc 掃描以外的用途)。
    ★top_var 限定很重要★:guard/canary/testmap/... 底下的巢狀子指令也是
    `xxx.add_parser("list", ...)` 這個形狀,若不限 receiver 必須是"頂層
    subparsers 物件",會把巢狀子指令名(如 "list"/"check")誤認成一級指令,
    連帶把它們算進 removed、砍出語法洞或誤刪保留指令的巢狀選項。"""
    c = node.value if isinstance(node, (ast.Assign, ast.Expr)) else None
    if (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
            and c.func.attr == "add_parser" and c.args
            and isinstance(c.args[0], ast.Constant)
            and isinstance(c.args[0].value, str)):
        if top_var is not None:
            if not (isinstance(c.func.value, ast.Name) and c.func.value.id == top_var):
                return None
        return c.args[0].value
    return None


def _top_subparsers_var(main):
    """找出 main() 內『頂層』subparsers 物件的變數名——即 dest="cmd" 那個
    (dispatch if 都測 args.cmd,故用同一個 dest 字面值鎖定,與巢狀的
    dest="gcmd"/"ccmd"/... 區分開)。找不到回 None(呼叫端退回不限 receiver)。"""
    for n in main.body:
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call):
            call = n.value
            if isinstance(call.func, ast.Attribute) and call.func.attr == "add_subparsers":
                for kw in call.keywords:
                    if (kw.arg == "dest" and isinstance(kw.value, ast.Constant)
                            and kw.value.value == "cmd"):
                        if len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                            return n.targets[0].id
    return None


def collect_edits(tree, funcs, drop, keep, removed):
    """回傳 (dels, inserts)。
    dels    = [(起行, 迄行)] 1-based inclusive,整行刪除
    inserts = [(行號, 文字)] 在該行位置插入(用於混合迴圈註冊的重寫)
    ★只記行號範圍,不重建任何保留的程式碼——註解與格式因此原字保留★
    """
    dels, inserts = [], []
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name in drop:
            start = min([n.lineno] + [d.lineno for d in n.decorator_list])
            dels.append((start, n.end_lineno))

    main = funcs["main"]
    top_var = _top_subparsers_var(main)

    # subparser 註冊採「區塊」刪除,不是單行:一支指令的註冊常是
    # `p = sub.add_parser("x", ...)` 後面接一串 `p.add_argument(...)`,
    # 甚至巢狀子指令(`gsub = g.add_subparsers(...)` 再展開一層)。這些
    # 後續行不會匹配 `_add_parser_name(top_var=...)`(receiver 不是頂層
    # subparsers 變數),必須整段跟著該指令的區塊一起刪,否則刪掉宣告行
    # 留下引用未定義變數的殘行 → 產物 NameError / SyntaxError。
    # 區塊邊界:下一個頂層 `x = <top_var>.add_parser(...)`、"頂層" for 迴圈註冊、
    # 或 `args = <top_var 的來源> .parse_args()`(註冊區結束,進入 dispatch)。
    # ★只有 receiver 是 top_var 的迴圈才算「頂層」邊界★(2026-07-31 修正):
    # 保留指令自己巢狀註冊子指令的迴圈(receiver 是它自己的 add_subparsers
    # 產物,不是 top_var)不算邊界——它跟前後的 `p2 = sub.add_parser(...)` /
    # `osub = p2.add_subparsers(...)` 一樣,屬於「當前正在累積的區塊」的一部
    # 分,該跟著區塊一起去留(区块被删就跟着删、区块保留就跟着留),不能被剥离
    # 出去丟給下面那段只認頂層 keep 名單的 ast.walk 迴圈處理(那段會拿巢狀子
    # 指令名去跟頂層 keep 比對,永遠比不中,导致整段迴圈被誤砍空)。
    block_name, block_stmts = None, []

    def _flush_block():
        nonlocal block_name, block_stmts
        if block_name is not None and block_name in removed:
            dels.append((block_stmts[0].lineno, block_stmts[-1].end_lineno))
        block_name, block_stmts = None, []

    registration_done = False
    for n in main.body:
        if registration_done:
            break
        if (isinstance(n, ast.For) and isinstance(n.iter, ast.Tuple)
                and _is_registration_loop(n, top_var=top_var)):
            _flush_block()
            continue  # 頂層迴圈註冊,由下面獨立的 ast.walk 統一處理(含重排例外)
        if (isinstance(n, ast.Assign) and isinstance(n.value, ast.Call)
                and isinstance(n.value.func, ast.Attribute)
                and n.value.func.attr == "parse_args"):
            _flush_block()
            registration_done = True  # 註冊區結束,其後是 dispatch if 鏈
            continue
        nm = _add_parser_name(n, top_var=top_var) if isinstance(n, (ast.Assign, ast.Expr)) else None
        if nm is not None:
            _flush_block()
            block_name, block_stmts = nm, [n]
            continue
        if block_name is not None:
            block_stmts.append(n)
    _flush_block()

    for n in ast.walk(tree):
        # dispatch 分支:條件裡的指令名全部屬移除清單才砍
        if isinstance(n, ast.If):
            ns = _cmd_names(n.test)
            if ns and ns <= removed:
                dels.append((n.lineno, n.end_lineno))
                continue
        # 迴圈註冊(★須 _is_registration_loop 把關★,含 top_var receiver 限定,
        # 見該函式說明——沒有這道限定,保留指令自己的巢狀迴圈註冊會被誤砍)
        if (isinstance(n, ast.For) and isinstance(n.iter, ast.Tuple)
                and _is_registration_loop(n, top_var=top_var)):
            names = [_first_const(e) for e in n.iter.elts]
            if names and all(x is not None for x in names):
                kept = [e for e, x in zip(n.iter.elts, names) if x in keep]
                if not kept:
                    dels.append((n.lineno, n.end_lineno))          # 全砍
                elif len(kept) != len(n.iter.elts):
                    # ★唯一允許重排的小塊★:整塊刪掉,改插入過濾後的等價迴圈
                    node2 = ast.For(target=n.target,
                                    iter=ast.Tuple(elts=kept, ctx=ast.Load()),
                                    body=n.body, orelse=n.orelse, type_comment=None)
                    ast.fix_missing_locations(node2)
                    indent = " " * n.col_offset
                    txt = "\n".join(indent + ln for ln in ast.unparse(node2).splitlines())
                    dels.append((n.lineno, n.end_lineno))
                    inserts.append((n.lineno, txt))
    return dels, inserts


def apply_edits(text, dels, inserts):
    lines = text.splitlines(keepends=True)
    kill = [False] * (len(lines) + 2)
    for a, b in dels:
        for i in range(a, b + 1):
            if i < len(kill):
                kill[i] = True
    ins = {}
    for ln, txt in inserts:
        ins.setdefault(ln, []).append(txt)
    out = []
    for i, ln in enumerate(lines, 1):
        for txt in ins.get(i, []):
            out.append(txt + "\n")
        if not kill[i]:
            out.append(ln)
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent
    ap.add_argument("--src", default=str(here / "lumos"))
    ap.add_argument("--outfile", default=str(here.parent / "dist" / "scripts" / "lumos"))
    ap.add_argument("--keep", nargs="*", default=None, help="覆蓋預設保留清單(測試用)")
    ap.add_argument("--emit-manifest", action="store_true")
    a = ap.parse_args()

    keep = set(a.keep) if a.keep is not None else set(DEFAULT_KEEP)
    text = Path(a.src).read_text(encoding="utf-8")
    tree, funcs, seen, drop = build(text, keep)

    # 移除清單真值:從『頂層』subparser 註冊掃出全部一級指令名,減去 keep(不硬編)。
    # ★top_var 限定★:不然 guard/canary/... 底下巢狀子指令(list/check/...)
    # 會被誤當一級指令收進來,見 _add_parser_name 的說明。
    top_var = _top_subparsers_var(funcs["main"])
    allc = set()
    for n in ast.walk(tree):
        nm = _add_parser_name(n, top_var=top_var) if isinstance(n, (ast.Assign, ast.Expr)) else None
        if nm:
            allc.add(nm)
        if (isinstance(n, ast.For) and isinstance(n.iter, ast.Tuple)
                and _is_registration_loop(n, top_var=top_var)):
            for e in n.iter.elts:
                x = _first_const(e)
                if x:
                    allc.add(x)
    removed = allc - keep

    dels, inserts = collect_edits(tree, funcs, drop, keep, removed)
    new_text = apply_edits(text, dels, inserts)

    # 產物必須自己 parse 得過(行級手術最容易壞的地方就是刪出語法洞)
    try:
        ast.parse(new_text)
    except SyntaxError as e:
        print(f"ERROR: 產物語法壞了(行級手術刪出洞): {e}", file=sys.stderr)
        return 1

    out = Path(a.outfile)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(new_text, encoding="utf-8")
    out.chmod(0o755)

    kept_comments = sum(1 for ln in new_text.splitlines() if ln.lstrip().startswith("#"))
    if a.emit_manifest:
        import json
        print(json.dumps({"keep_funcs": sorted(seen), "drop_funcs": sorted(drop),
                          "removed_cmds": sorted(removed), "kept_comment_lines": kept_comments},
                         ensure_ascii=False))
    else:
        print(f"✓ 生成 {out}  保留 {len(seen)} 函式 / 移除 {len(drop)} / 保住 {kept_comments} 行註解")

    # 組交付包:slim/ 的內容原樣複製進 dist/
    import shutil
    pkg_src = here.parent / "slim"
    pkg_dst = out.parent.parent
    if pkg_src.is_dir():
        for item in ("install.sh", "get.sh", "uninstall.sh", "README.md", "skills"):
            s = pkg_src / item
            if s.is_dir():
                shutil.copytree(s, pkg_dst / item, dirs_exist_ok=True)
            elif s.is_file():
                shutil.copy2(s, pkg_dst / item)
        for exe in ("install.sh", "get.sh", "uninstall.sh"):
            p = pkg_dst / exe
            if p.is_file():
                p.chmod(0o755)
        print(f"✓ 交付包: {pkg_dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
