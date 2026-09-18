#!/usr/bin/env python3
"""收工點名的情境產生器:造一份假的對話紀錄餵給 hook,比對「實際改幾支」與「它說幾支」。

用法: python3 probe_sync.py <repo根> [情境名...]
不帶情境名就全跑。只讀 hook、不改被檢查的 repo 任何檔;假紀錄寫在本腳本所在目錄。
"""
import json, os, re, subprocess, sys
from pathlib import Path

HOOK = Path.home() / ".claude/hooks/check-graph-sync.py"
HERE = Path(__file__).resolve().parent


def tool_use(name, inp):
    return {"type": "assistant", "message": {"role": "assistant",
            "content": [{"type": "tool_use", "id": "t", "name": name, "input": inp}]}}


def scenarios(root):
    """每個情境:(名稱, 這輪實際改了幾支 code 檔, 該輪的工具呼叫序列)"""
    a = root + "/scripts/lumos"
    b = root + "/scripts/test_lumos.py"
    c = root + "/scripts/hooks/pre-push"
    heredoc = "cat > " + c + " <<'EOF'\n#!/bin/sh\nEOF"
    return {
        # 現況就會過的兩個(對照組,證明儀器本身有在動)
        "write":    (1, [tool_use("Write", {"file_path": a, "content": "x"})]),
        "cp":       (1, [tool_use("Bash", {"command": "cp /tmp/a.py " + a})]),
        # 現況會漏的三種主流寫法
        "redirect": (1, [tool_use("Bash", {"command": 'echo "# x" > ' + a})]),
        "sed":      (1, [tool_use("Bash", {"command": "sed -i '' 's/a/b/' " + a})]),
        "heredoc":  (1, [tool_use("Bash", {"command": heredoc})]),
        # 方案「沒列舉過」的手法——S1 要求這些也不能漏,這三個是修對了沒的真考題
        "tee":      (1, [tool_use("Bash", {"command": "printf x | tee " + a})]),
        "python1":  (1, [tool_use("Bash", {"command": 'python3 -c "open(\'' + a + '\',\'w\').write(\'x\')"'})]),
        "shwrap":   (1, [tool_use("Bash", {"command": "sh -c 'echo x > " + a + "'"})]),
        # 混用:一支走編輯工具、兩支走 shell。這一列是整件事的核心症狀
        "mixed":    (3, [tool_use("Write", {"file_path": a, "content": "x"}),
                         tool_use("Bash", {"command": "sed -i '' 's/a/b/' " + b}),
                         tool_use("Bash", {"command": heredoc})]),
    }


def run(name, expect, rows, root):
    tpath = HERE / ("probe-" + name + ".jsonl")
    body = [{"type": "user", "message": {"role": "user", "content": "改一下"}}, *rows]
    tpath.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in body), encoding="utf-8")
    payload = {"session_id": "probe-" + name, "transcript_path": str(tpath),
               "cwd": root, "hook_event_name": "Stop"}
    env = dict(os.environ, LUMOS_STOP_BLOCK_OFF="1")
    r = subprocess.run(["/opt/homebrew/bin/python3", str(HOOK), "--budget", "40"],
                       input=json.dumps(payload), capture_output=True, text=True,
                       cwd=root, env=env)
    out = (r.stderr or "") + (r.stdout or "")
    m = re.search(r"這一輪改了 (\d+) 個程式碼檔", out)
    said = int(m.group(1)) if m else 0
    listed = len(re.findall(r"^\s+• ", out, re.M))
    degraded = ("可能" in out) and (("不是這輪" in out) or ("不完整" in out))
    ok = (said == expect)
    mark = "OK  " if ok else "FAIL"
    extra = ",有降級提示" if degraded else ""
    print("  %s %-9s 實際改 %d 支 / 它說 %d 支(清單列了 %d 項%s)" % (mark, name, expect, said, listed, extra))
    return ok


def main():
    root = sys.argv[1]
    want = sys.argv[2:]
    sc = scenarios(root)
    names = want or list(sc)
    print("對照 hook: %s" % HOOK)
    print("repo 根  : %s" % root)
    results = [run(n, sc[n][0], sc[n][1], root) for n in names]
    bad = sum(1 for x in results if not x)
    print("\n%d 個情境,%d 個不符預期" % (len(results), bad))
    sys.exit(1 if bad else 0)


main()
