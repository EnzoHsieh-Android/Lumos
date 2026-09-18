#!/usr/bin/env python3
"""收工點名的情境產生器:造一個真的現場,餵給 hook,比對「實際改幾支」與「它說幾支」。

用法: python3 probe_sync.py [對照的 hook 路徑]
  不帶參數就用已部署的那份(~/.claude/hooks/check-graph-sync.py)——★那才是實際會跑的★。

★現場一定要真的改檔★(2026-09-18 實地踩到):第一版只在對話紀錄裡「宣稱」改過檔、
沒有真的動檔案。清單來源改成問版本控制之後,工作樹乾淨它就正確地回答「沒有」——
於是九個情境全 FAIL,而每一個 FAIL 其實都是新行為的正確表現。
這支工具是撤除條件依賴的儀器,壞掉的話那個判準會永遠成立、等於被自己的儀器架空。

它不改被檢查的 repo:每個情境都在自己的臨時倉庫裡跑完就丟。
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_HOOK = Path.home() / ".claude/hooks/check-graph-sync.py"


def _mk_repo():
    """造一個臨時倉庫:有一個提交、有圖譜目錄、有兩支程式碼檔(一支有副檔名、一支沒有)。"""
    root = Path(tempfile.mkdtemp(prefix="probe-sync-"))
    (root / "scripts").mkdir()
    (root / "docs" / "t-knowledge" / "Systems").mkdir(parents=True)
    (root / "scripts" / "keep.py").write_text("x = 1\n", encoding="utf-8")
    (root / "scripts" / "tool").write_text("#!/usr/bin/env python3\ny = 1\n", encoding="utf-8")
    (root / "docs" / "t-knowledge" / "Systems" / "s.md").write_text(
        "---\ntype: system\nstatus: doing\ncreated: 2026-09-18\n---\n# s\n\n說明。\n",
        encoding="utf-8")
    for args in (["init", "-q"], ["add", "-A"],
                 ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base"]):
        subprocess.run(["git", "-C", str(root)] + args, capture_output=True)
    return root


def _turn(*tools):
    rows = [{"type": "user", "message": {"role": "user", "content": "改一下"}}]
    for name, inp in tools:
        rows.append({"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "id": "t", "name": name, "input": inp}]}})
    return rows


# 每個情境:(說明, 真的怎麼改, 對話紀錄裡的工具呼叫, 應該報幾支)
# ★前三個是修之前就會過的對照組★——它們證明儀器本身在動,不是全部一起壞。
# ★中間五個是修之前會完全沒輸出的★,其中後三個是設計時沒有列舉過的手法。
# ★最後一個是核心症狀★:混用時修之前只報一支。
def _cases(root):
    keep = root / "scripts" / "keep.py"
    tool = root / "scripts" / "tool"
    newf = root / "scripts" / "brand_new.py"
    pkg = root / "scripts" / "newpkg"

    def edit_keep(v):
        return lambda: keep.write_text("x = %d\n" % v, encoding="utf-8")

    return [
        ("write", edit_keep(2), _turn(("Write", {"file_path": str(keep), "content": "x = 2\n"})), 1),
        ("cp", edit_keep(3), _turn(("Bash", {"command": "cp /tmp/a.py scripts/keep.py"})), 1),
        ("delete", lambda: tool.unlink(), _turn(("Bash", {"command": "rm scripts/tool"})), 1),
        ("redirect", edit_keep(4), _turn(("Bash", {"command": "echo 'x = 4' > scripts/keep.py"})), 1),
        ("sed", edit_keep(5), _turn(("Bash", {"command": "sed -i '' 's/1/5/' scripts/keep.py"})), 1),
        ("heredoc", lambda: newf.write_text("z = 1\n", encoding="utf-8"),
         _turn(("Bash", {"command": "cat > scripts/brand_new.py <<'EOF'\nz = 1\nEOF"})), 1),
        ("tee", edit_keep(6), _turn(("Bash", {"command": "printf 'x = 6' | tee scripts/keep.py"})), 1),
        ("python1", edit_keep(7),
         _turn(("Bash", {"command": "python3 -c \"open('scripts/keep.py','w').write('x = 7')\""})), 1),
        ("shwrap", edit_keep(8), _turn(("Bash", {"command": "sh -c 'echo x = 8 > scripts/keep.py'"})), 1),
        ("newdir", lambda: (pkg.mkdir(), (pkg / "a.py").write_text("a = 1\n", encoding="utf-8"),
                            (pkg / "b.py").write_text("b = 1\n", encoding="utf-8")),
         _turn(("Bash", {"command": "mkdir scripts/newpkg && echo a > scripts/newpkg/a.py"})), 2),
        ("mixed", lambda: (keep.write_text("x = 9\n", encoding="utf-8"),
                           newf.write_text("z = 2\n", encoding="utf-8"),
                           tool.unlink()),
         _turn(("Write", {"file_path": str(keep), "content": "x = 9\n"}),
               ("Bash", {"command": "echo z = 2 > scripts/brand_new.py"}),
               ("Bash", {"command": "rm scripts/tool"})), 3),
    ]


def main():
    hook = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_HOOK
    if not hook.is_file():
        print("找不到要對照的 hook:%s" % hook)
        sys.exit(2)
    print("對照 hook: %s" % hook)
    print("現場    : ★每個情境都真的改檔★,各自在臨時倉庫裡跑完就丟\n")
    root_for_cases = _mk_repo()
    names = [c[0] for c in _cases(root_for_cases)]
    shutil.rmtree(root_for_cases, ignore_errors=True)
    results = []
    for name in names:
        # 每個情境重新造現場(_cases 綁在各自的 root 上)
        root = _mk_repo()
        case = next(c for c in _cases(root) if c[0] == name)
        home = Path(tempfile.mkdtemp(prefix="probe-home-"))
        try:
            case[1]()
            tp = home / "t.jsonl"
            tp.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in case[2]),
                          encoding="utf-8")
            env = dict(os.environ, HOME=str(home), LUMOS_STOP_BLOCK_OFF="1")
            r = subprocess.run([sys.executable, str(hook), "--budget", "40"],
                               input=json.dumps({"session_id": "probe-" + name,
                                                 "transcript_path": str(tp), "cwd": str(root),
                                                 "hook_event_name": "Stop"}),
                               capture_output=True, text=True, cwd=str(root), env=env)
            out = (r.stdout or "") + (r.stderr or "")
            m = re.search(r"有 (\d+) 個程式碼檔還沒提交", out)
            said = int(m.group(1)) if m else 0
            listed = len(re.findall(r"^\s+• ", out, re.M))
            ok = (said == case[3])
            results.append(ok)
            print("  %s %-9s 實際改 %d 支 / 它說 %d 支(清單列了 %d 項)"
                  % ("OK  " if ok else "FAIL", name, case[3], said, listed))
        finally:
            shutil.rmtree(root, ignore_errors=True)
            shutil.rmtree(home, ignore_errors=True)
    bad = sum(1 for x in results if not x)
    print("\n%d 個情境,%d 個不符預期" % (len(results), bad))
    sys.exit(1 if bad else 0)


main()
