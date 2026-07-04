#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_lumos.py — lumos 行為鎖定測試(stdlib only,零依賴)

跑法: python3 scripts/test_lumos.py
退出碼: 0 全過 / 1 有失敗(CI 可用)

涵蓋 2026-06-13 Sonnet 對抗審計找到的 bug + 核心讀寫行為。每個 fixture 對應一條
[[2026-06-13_lumos審計與測試套件]] 列出的優先案例。
"""
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")   # cp950 印 ✓/✗ 會 UnicodeEncodeError
except Exception:
    pass

GRAPHCTL = str(Path(__file__).resolve().parent / "lumos")
PASS, FAIL = 0, 0


def run(vault, *args, expect_rc=None):
    r = subprocess.run([sys.executable, GRAPHCTL, "--vault", str(vault), *args],
                       capture_output=True, text=True)
    if expect_rc is not None and r.returncode != expect_rc:
        raise AssertionError(f"rc={r.returncode} 預期 {expect_rc}\n{r.stdout}\n{r.stderr}")
    return r


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✓ {name}")
    else:
        FAIL += 1
        print(f"  ✗ {name}  {detail}")


def mkvault():
    d = Path(tempfile.mkdtemp(prefix="gctl-test-"))
    for sub in ("Systems", "Verification", "Projects", "MOC"):
        (d / sub).mkdir(parents=True)
    (d / "MOC" / "idx.md").write_bytes("---\ntype: moc\n---\n# idx\n".encode("utf-8"))
    return d


def write(vault, rel, fm, body="# x\n"):
    p = vault / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(f"---\n{fm}\n---\n{body}".encode("utf-8"))
    return p


def read(p):
    return p.read_text(encoding="utf-8")


def _mk_gate_fixture():
    """gate 測試三件套:vault(canary-log 落 vault.parent)+ repo(scripts/real.py)+ 好/壞 spec。"""
    vault = mkvault()
    repo = Path(tempfile.mkdtemp(prefix="gctl-gate-repo-"))
    (repo / "scripts").mkdir()
    (repo / "scripts" / "real.py").write_text("L1\nL2\nL3\n", encoding="utf-8")
    spec_ok = repo / "spec-ok.md"
    spec_ok.write_text("# s\n見 `scripts/real.py:2`。\n", encoding="utf-8")
    spec_bad = repo / "spec-bad.md"
    spec_bad.write_text("# s\n見 `scripts/ghost.py` 實作。\n", encoding="utf-8")
    return vault, repo, spec_ok, spec_bad


def t_canary_findings():
    import json as _json
    vault = mkvault()
    run(vault, "canary", "record", "caught", "--loop", "cf", "--severity", "minor",
        "--findings", "3", expect_rc=0)
    run(vault, "canary", "record", "caught", "--loop", "cf", "--severity", "clean", expect_rc=0)
    lines = [_json.loads(l) for l in
             (vault.parent / ".canary-log.jsonl").read_text(encoding="utf-8").splitlines()]
    check("findings: --findings 3 寫入", lines[0].get("findings") == 3, str(lines[0]))
    check("findings: 不給則鍵不存在", "findings" not in lines[1], str(lines[1]))
    r = run(vault, "canary", "record", "caught", "--loop", "cf", "--findings", "abc")
    check("findings: 非整數 rc!=0", r.returncode != 0, f"rc={r.returncode}")


def t_loop_gate():
    vault, repo, spec_ok, spec_bad = _mk_gate_fixture()

    def rec(loop, sev, f=None, kind="caught"):
        args = ["canary", "record", kind, "--loop", loop, "--severity", sev]
        if f is not None:
            args += ["--findings", str(f)]
        run(vault, *args, expect_rc=0)

    def gate(loop, spec=None, need="2"):
        return run(vault, "loop", "status", loop, "--need", need,
                   "--gate", "--spec", str(spec or spec_ok), "--repo", str(repo))

    rec("g3", "minor", 2); rec("g3", "clean", 0)
    r = gate("g3")
    check("gate 案3: [2,0] 全過 rc=0", r.returncode == 0, r.stdout)

    rec("g4", "minor", 2); rec("g4", "minor", 1)
    r = gate("g4")
    check("gate 案4: [2,1] 殘餘正向 rc=0", r.returncode == 0, r.stdout)

    rec("g5", "minor", 2); rec("g5", "minor", 3)
    r = gate("g5")
    check("gate 案5: [2,3] 非枯竭 rc=1 指 G2", r.returncode == 1 and "G2" in r.stdout, r.stdout)

    rec("g6", "minor", 3); rec("g6", "minor", 2)
    r = gate("g6")
    check("gate 案6: 末輪 2>1 rc=1", r.returncode == 1 and "G2" in r.stdout, r.stdout)

    rec("g7", "minor", 1); rec("g7", "minor", 1)
    r = gate("g7")
    check("gate 案7: [1,1] 恆定涓流 rc=1", r.returncode == 1 and "G2" in r.stdout, r.stdout)

    rec("g8", "minor", 2); rec("g8", "minor", 1); rec("g8", "minor", 1)
    r = gate("g8", need="3")
    check("gate 案8: K=3 [2,1,1] 尾涓流 rc=1", r.returncode == 1 and "G2" in r.stdout, r.stdout)

    rec("g9a", "minor", 1)
    r = gate("g9a", need="1")
    check("gate 案9a: K=1 [1] rc=1", r.returncode == 1, r.stdout)
    rec("g9b", "clean", 0)
    r = gate("g9b", need="1")
    check("gate 案9b: K=1 [0] rc=0(不得 IndexError)", r.returncode == 0, f"{r.stdout}\n{r.stderr}")

    rec("g10a", "clean", 1); rec("g10a", "clean", 0)
    r = gate("g10a")
    check("gate 案10a: clean 卻 findings=1 互證矛盾 rc=1", r.returncode == 1 and "互證" in r.stdout, r.stdout)
    rec("g10b", "minor", 2); rec("g10b", "minor", 0)
    r = gate("g10b")
    check("gate 案10b: minor 卻 findings=0 互證矛盾 rc=1", r.returncode == 1 and "互證" in r.stdout, r.stdout)

    rec("g11", "minor", 2); rec("g11", "clean", 0)
    r = gate("g11", spec=spec_bad)
    check("gate 案11: 壞引用 rc=1 指 G1 且列 ghost",
          r.returncode == 1 and "G1" in r.stdout and "scripts/ghost.py" in r.stdout, r.stdout)

    run(vault, "canary", "record", "caught", "--loop", "g12", "--findings", "0", expect_rc=0)
    rec("g12", "clean", 0)
    r = gate("g12")
    check("gate 案12: 缺 severity 輪斷在 K-streak(歸因回歸)",
          r.returncode == 1 and "K-streak" in r.stdout, r.stdout)

    rec("g2f", "minor"); rec("g2f", "clean")
    r = gate("g2f")
    check("gate: 缺 findings 欄位 fail-closed 且提示 --findings",
          r.returncode == 1 and "--findings" in r.stdout, r.stdout)

    # 案 13:回歸——不帶 --gate 行為與現行為一致(舊判準不看 findings)
    r = run(vault, "loop", "status", "g3")
    check("gate 案13a: 不帶 --gate CONVERGED rc=0", r.returncode == 0 and "CONVERGED" in r.stdout, r.stdout)
    r = run(vault, "loop", "status", "g5")
    check("gate 案13b: g5 無 gate 仍 CONVERGED(舊判準)", r.returncode == 0, r.stdout)

    r = run(vault, "loop", "status", "g3", "--need", "2", "--gate", "--repo", str(repo))
    check("gate 案14(新契約): 缺 --spec → G1 skip,g3 收斂 rc 0",
          r.returncode == 0 and "skipped" in r.stdout, f"rc={r.returncode}\n{r.stdout}")


def t_loop_gate_need3():
    vault, repo, spec_ok, _ = _mk_gate_fixture()
    for sev, f in (("minor", 2), ("clean", 0)):
        run(vault, "canary", "record", "caught", "--loop", "k3",
            "--severity", sev, "--findings", str(f), expect_rc=0)
    r = run(vault, "loop", "status", "k3", "--need", "3",
            "--gate", "--spec", str(spec_ok), "--repo", str(repo))
    check("gate K=3: 僅 2 筆合格輪 rc=1(斷在 K-streak)",
          r.returncode == 1 and "K-streak" in r.stdout, r.stdout)


def t_loop_gate_no_spec():
    vault, repo, _spec_ok, _spec_bad = _mk_gate_fixture()
    def rec(loop, sev, f):
        run(vault, "canary", "record", "caught", "--loop", loop, "--severity", sev,
            "--findings", str(f), expect_rc=0)
    # 未枯竭 [2,3]:即使 G1 skip,G2 仍擋
    rec("ns1", "minor", 2); rec("ns1", "minor", 3)
    r = run(vault, "loop", "status", "ns1", "--need", "2", "--gate", "--repo", str(repo))
    check("gate no-spec: G1 skip 但 G2 未枯竭 → rc 1",
          r.returncode == 1 and "skipped" in r.stdout and "G2" in r.stdout, r.stdout)


def t_write_lf_roundtrip():
    import subprocess
    proj = Path(tempfile.mkdtemp(prefix="gctl-lf-"))
    (proj / "Systems").mkdir(parents=True); (proj / "MOC").mkdir()
    (proj / "MOC" / "idx.md").write_bytes(b"---\ntype: moc\n---\n# idx\n")
    write(proj, "Systems/S.md", "type: system\nstatus: doing")     # 經 write() helper
    raw = (proj / "Systems" / "S.md").read_bytes()
    check("write helper 寫 LF(無 CRLF)", b"\r\n" not in raw, f"got {raw[:40]!r}")
    r = subprocess.run([sys.executable, GRAPHCTL, "set", str(proj / "Systems" / "S.md"),
                        "status", "done"], capture_output=True, text=True)
    raw2 = (proj / "Systems" / "S.md").read_bytes()
    check("atomic_write_verify 寫回 LF", b"\r\n" not in raw2, f"rc={r.returncode} {r.stderr}")


# ── Task 1: 平台 helper + 安裝原語(scaffold / skills / hooks)──
def t_scaffold_project():
    import subprocess, sys
    proj = Path(tempfile.mkdtemp(prefix="gctl-scaf-"))
    r = subprocess.run([sys.executable, GRAPHCTL, "init", "--name", "demo", "--no-hooks"],
                       cwd=str(proj), capture_output=True, text=True)
    kg = proj / "docs" / "demo-knowledge"
    for d in ("Systems", "Verification", "Projects", "Issues", "Sessions", "MOC"):
        check(f"scaffold: 建 {d} 夾", (kg / d).is_dir(), f"rc={r.returncode} {r.stderr}")
    check("scaffold: MOC/index.md", (kg / "MOC" / "index.md").exists(), "")
    check("scaffold: .gitignore", (kg / ".gitignore").exists(), "")


def t_install_skills_unix():
    if sys.platform == "win32":
        check("skills: Windows 分支留 Task 7 手動驗", True); return
    import subprocess
    r = subprocess.run([sys.executable, GRAPHCTL, "install", "--force"], capture_output=True, text=True)
    dst = Path.home() / ".claude" / "skills" / "lumos-project-notes"
    check("skills: ~/.claude/skills/lumos-project-notes 連結存在", dst.exists(), r.stderr)


def t_install_includes_skills():
    if sys.platform == "win32":
        check("install+skills: Windows 留 Task 7 手動驗", True); return
    import subprocess
    subprocess.run([sys.executable, GRAPHCTL, "install", "--force"], capture_output=True, text=True)
    g = Path.home() / ".local" / "bin" / "lumos"
    sk = Path.home() / ".claude" / "skills" / "lumos-design-loop"
    check("install: 全域 lumos 在", g.exists(), "")
    check("install: 連帶 skills 也在", sk.exists(), "")


def t_install_hooks_py():
    """hermetic:temp root + git init + temp HOME,只斷言 core.hooksPath。
    完整 settings 斷言留 Task 3。"""
    import subprocess, os
    root = Path(tempfile.mkdtemp(prefix="gctl-hooks-"))
    fake = Path(tempfile.mkdtemp(prefix="gctl-home-"))
    subprocess.run(["git", "-C", str(root), "init"], capture_output=True, text=True)
    # lumos 無 .py 副檔名 → spec_from_file_location 推不出 loader,顯式給 SourceFileLoader
    code = ("import importlib.util,sys;from pathlib import Path;"
            "from importlib.machinery import SourceFileLoader;"
            "spec=importlib.util.spec_from_file_location('m',sys.argv[1],"
            "loader=SourceFileLoader('m',sys.argv[1]));"
            "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);"
            "m._install_hooks_py(Path(sys.argv[2]))")
    r = subprocess.run([sys.executable, "-c", code, GRAPHCTL, str(root)],
                       env=dict(os.environ, HOME=str(fake), USERPROFILE=str(fake)),
                       capture_output=True, text=True)
    hp = subprocess.run(["git", "-C", str(root), "config", "core.hooksPath"],
                        capture_output=True, text=True)
    check("hooks: core.hooksPath == scripts/hooks",
          hp.stdout.strip() == "scripts/hooks", f"got {hp.stdout!r} stderr={r.stderr}")


def t_hooks_python_fallback():
    import pathlib
    repo = pathlib.Path(GRAPHCTL).resolve().parent.parent
    for h in ("post-commit", "pre-push"):
        t = (repo / "scripts" / "hooks" / h).read_text(encoding="utf-8")
        check(f"{h}: 有 python3||python fallback",
              "command -v python3 || command -v python" in t, "缺 fallback")


# ── BUG-1: append dedup 前綴衝突 — X 不該因 X_v2 存在被誤判 ──
def t_append_prefix_collision():
    v = mkvault()
    p = write(v, "Systems/S.md",
              "type: system\nstatus: done\nverified_by:\n  - \"[[Projects/A_v2]]\"")
    run(v, "append", "S", "verified_by", "[[A]]", expect_rc=0)
    txt = read(p)
    check("BUG-1 append 前綴衝突: [[A]] 真的被加入(非被 A_v2 誤判 no-op)",
          "[[A]]" in txt and "[[Projects/A_v2]]" in txt, txt)


# ── append 精確 dedup — 同 basename 再 append 應 no-op ──
def t_append_exact_dedup():
    v = mkvault()
    p = write(v, "Systems/S.md",
              "type: system\nstatus: done\nverified_by:\n  - \"[[V1]]\"")
    run(v, "append", "S", "verified_by", "[[V1]]", expect_rc=0)
    check("append 精確 dedup: 同 basename 不重複加",
          read(p).count("[[V1]]") == 1, read(p))


# ── BUG-2: Check 3 前綴 — System 連 V 但 verified_by 只有 V_v2,doctor 應報漏 ──
def t_check3_prefix_no_false_pass():
    # Check 3 看 Verification→System 方向:topic 連 S,但 S.verified_by 只有 topic_v2。
    # 精確比對下 topic != topic_v2 → 應報漏;舊子字串碼會誤判已同步。
    v = mkvault()
    write(v, "Systems/S.md",
          "type: system\nstatus: done\nverified_by:\n  - \"[[2026-01-01_topic_v2]]\"",
          body="# S\n")
    write(v, "Verification/2026-01-01_topic.md", "type: verification\nstatus: pass\ndate: 2026-01-01",
          body="# topic\n驗 [[S]]\n")
    write(v, "Verification/2026-01-01_topic_v2.md", "type: verification\nstatus: pass\ndate: 2026-01-02",
          body="# topic_v2\n驗 [[S]]\n")
    r = run(v, "doctor", "--ci")
    # 精確解析「漏:」行的 token,避免 topic 是 topic_v2 子字串的歧義
    missed_tokens = set()
    for line in r.stdout.splitlines():
        if "漏:" in line:
            missed_tokens |= {t.strip() for t in line.split("漏:", 1)[1].split("|")}
    check("BUG-2 Check3 前綴: topic 漏寫被報(非被 topic_v2 子字串誤判已同步)",
          r.returncode == 1 and "2026-01-01_topic" in missed_tokens,
          f"missed={missed_tokens}\n{r.stdout}")


# ── BUG-6: cmd_new 路徑逃脫 ──
def t_new_path_traversal():
    v = mkvault()
    r = run(v, "new", "system", "../../../tmp/injected")
    check("BUG-6 new 路徑逃脫被拒(exit 2)", r.returncode == 2, r.stderr)
    check("BUG-6 未在 vault 外建檔", not (v.parent.parent.parent / "tmp" / "injected.md").exists())


def t_new_teaches_tags():
    # new 在執行當下教標籤規則:stdout 含合約鏈提示,檔案骨架含完整符號行
    v = mkvault()
    r = run(v, "new", "system", "AcctSvc", expect_rc=0)
    check("new system: stdout 教 ★INVARIANT★ + [test:] 合約鏈",
          "★INVARIANT★" in r.stdout and "[test:" in r.stdout, r.stdout)
    check("new system: stdout 提示寫完跑 doctor", "lumos doctor" in r.stdout, r.stdout)
    txt = read(v / "Systems" / "AcctSvc.md")
    check("new system: summary 骨架含 FLOW/KEY/DEP/TEST 符號行",
          all(s in txt for s in ("FLOW:", "KEY:", "DEP:", "TEST:")), txt)
    r2 = run(v, "new", "issue", "BadState", expect_rc=0)
    t2 = read(v / "Issues" / "BadState.md")
    check("new issue: 骨架含 FLAG/DECISION/KEY", all(s in t2 for s in ("FLAG:", "DECISION:", "KEY:")), t2)
    # 骨架本身要過 doctor(空符號行不該觸發 lint)
    rd = run(v, "doctor", "--ci")
    check("new 骨架 doctor 不報問題", rd.returncode == 0, rd.stdout)


# ── BUG-7: fmt_scalar YAML 型別劫持 ──
def t_set_boolean_guard():
    v = mkvault()
    p = write(v, "Systems/S.md", "type: system\nstatus: doing")
    run(v, "set", "S", "status", "true", expect_rc=0)
    check("BUG-7 set status true → 引號保護(status: \"true\")",
          'status: "true"' in read(p), read(p))


# ── set 日期 bare 不加引號(污染指紋防護的反向:正常日期不該被引號) ──
def t_set_date_bare():
    v = mkvault()
    p = write(v, "Systems/S.md", "type: system\nstatus: done\nupdated: 2026-01-01")
    run(v, "set", "S", "updated", "2026-06-13", expect_rc=0)
    check("set 日期 bare(updated: 2026-06-13 無引號)",
          "updated: 2026-06-13" in read(p) and '"2026-06-13"' not in read(p), read(p))


# ── set 最小 diff:只動目標行 ──
def t_set_minimal_diff():
    v = mkvault()
    fm = "type: system\nstatus: doing\ncreated: 2026-01-01\nsummary: |-\n  FLOW:A→B\n  KEY:keep"
    p = write(v, "Systems/S.md", fm)
    run(v, "set", "S", "status", "done", expect_rc=0)
    txt = read(p)
    check("set 最小 diff: summary block 逐字保留",
          "FLOW:A→B" in txt and "KEY:keep" in txt and "status: done" in txt, txt)


# ── append 全新 list(key 不存在) ──
def t_append_new_list():
    v = mkvault()
    p = write(v, "Systems/S.md", "type: system\nstatus: done")
    run(v, "append", "S", "plan_refs", "[[某計劃]]", expect_rc=0)
    txt = read(p)
    check("append 全新 list 建立(plan_refs:\\n  - \"[[某計劃]]\")",
          "plan_refs:" in txt and '- "[[某計劃]]"' in txt, txt)


# ── BUG-5: list 後接 sub-mapping(decisions)時,append verified_by 不插進 decisions ──
def t_append_with_nested_decisions():
    v = mkvault()
    fm = ("type: system\nstatus: done\n"
          "verified_by:\n  - \"[[V1]]\"\n"
          "decisions:\n  - content: 決策一\n    decided: 2026-01-01\n    valid: true")
    p = write(v, "Systems/S.md", fm)
    run(v, "append", "S", "verified_by", "[[V2]]", expect_rc=0)
    txt = read(p)
    # V2 應緊接 V1 後、在 decisions 之前;decisions 結構完整
    vi, di = txt.index("[[V2]]"), txt.index("decisions:")
    check("BUG-5 append 不插進 decisions 區塊(V2 在 decisions 前)", vi < di, txt)
    check("BUG-5 decisions 結構保留", "content: 決策一" in txt and "valid: true" in txt, txt)


# ── archive 前綴安全 + 移檔:archive X 不該動 X_v2 ──
def t_archive_prefix_and_move():
    # X 老(歸檔)、X_v2 近期(不歸檔):archive X 只動 X 的連結,X_v2 路徑連結+檔案不動
    v = mkvault()
    write(v, "Verification/2020-01-01_X.md", "type: verification\nstatus: pass\ncreated: 2020-01-01")
    write(v, "Verification/2090-01-01_X_v2.md", "type: verification\nstatus: pass\ncreated: 2090-01-01")
    s = write(v, "Systems/S.md", "type: system\nstatus: done",
              body="連 [[Verification/2020-01-01_X]] 與 [[Verification/2090-01-01_X_v2]]\n")
    run(v, "archive", "--days", "30", "--apply", expect_rc=0)
    txt = read(s)
    check("archive X 移到 Archive/2020-01/",
          (v / "Verification/Archive/2020-01/2020-01-01_X.md").exists())
    check("archive 前綴安全: X 連結正規化成 basename",
          "[[2020-01-01_X]]" in txt and "[[Verification/2020-01-01_X]]" not in txt)
    check("archive 前綴安全: 未歸檔的 X_v2 路徑連結+檔案不動",
          "[[Verification/2090-01-01_X_v2]]" in txt
          and (v / "Verification/2090-01-01_X_v2.md").exists(), txt)


# ── doctor 乾淨基線 ──
def t_doctor_clean():
    v = mkvault()
    write(v, "Systems/S.md", "type: system\nstatus: done\nverified_by:\n  - \"[[V1]]\"",
          body="# S\n")
    write(v, "Verification/V1.md", "type: verification\nstatus: pass\ndate: 2026-01-01",
          body="# V1\n驗 [[S]]\n")
    r = run(v, "doctor", "--ci")
    check("doctor 乾淨 vault → exit 0", r.returncode == 0, r.stdout)


# ══ 第二輪審計回歸 ══

# ── NEW-A: 跨資料夾同 basename append 不該誤 dedup / 不該 rc=2 ──
def t_append_cross_folder_same_basename():
    v = mkvault()
    write(v, "Systems/X.md", "type: system\nstatus: done")  # 另一篇,同 basename X
    p = write(v, "Systems/S.md",
              "type: system\nstatus: done\nverified_by:\n  - \"[[Verification/X]]\"")
    r = run(v, "append", "S", "verified_by", "[[Systems/X]]")
    check("NEW-A 跨資料夾同名 append 成功(非 rc=2 自驗失敗)", r.returncode == 0, r.stderr)
    check("NEW-A [[Systems/X]] 真的被加(與 [[Verification/X]] 並存)",
          "[[Systems/X]]" in read(p) and "[[Verification/X]]" in read(p), read(p))


# ── append path 式 vs basename 式同篇 → 視為重複(dedup) ──
def t_append_path_vs_basename_dedup():
    v = mkvault()
    p = write(v, "Systems/S.md",
              "type: system\nstatus: done\nverified_by:\n  - \"[[Verification/X]]\"")
    # 注意: link_target 保留路徑,故 [[X]] 與 [[Verification/X]] target 不同字串 →
    # 會新增(可接受的冗餘,非錯誤)。本案僅鎖定「完全相同 target 不重複」。
    run(v, "append", "S", "verified_by", "[[Verification/X]]", expect_rc=0)
    check("完全相同 target 不重複加", read(p).count("[[Verification/X]]") == 1, read(p))


# ── NEW-B: Check 3 跨資料夾同 basename 不該假通過 ──
def t_check3_cross_folder_no_false_pass():
    v = mkvault()
    write(v, "Systems/S.md",
          "type: system\nstatus: done\nverified_by:\n  - \"[[Projects/MyV]]\"")
    write(v, "Projects/MyV.md", "type: project\nstatus: done")  # 不同篇,同 basename
    write(v, "Verification/MyV.md", "type: verification\nstatus: pass\ndate: 2026-01-01",
          body="# MyV\n驗 [[S]]\n")
    r = run(v, "doctor", "--ci")
    missed = set()
    for line in r.stdout.splitlines():
        if "漏:" in line:
            missed |= {t.strip() for t in line.split("漏:", 1)[1].split("|")}
    check("NEW-B Check3 跨資料夾: Verification/MyV 漏寫被報(非被 Projects/MyV 同 basename 誤判)",
          r.returncode == 1 and "MyV" in missed, f"missed={missed}\n{r.stdout}")


# ── Check 3 path 式 vs basename 式同篇 → 視為已同步(不誤報漏) ──
def t_check3_path_basename_equiv():
    v = mkvault()
    # verified_by 用 path 式,Verification 也在 Verification/ → 同篇,不該報漏
    write(v, "Systems/S.md",
          "type: system\nstatus: done\nverified_by:\n  - \"[[Verification/MyV]]\"")
    write(v, "Verification/MyV.md", "type: verification\nstatus: pass\ndate: 2026-01-01",
          body="# MyV\n驗 [[S]]\n")
    r = run(v, "doctor", "--ci")
    check("Check3 path 式 verified_by 視為已同步(不誤報漏)", r.returncode == 0, r.stdout)


# ── archive CRLF 檔跳過 rewrite(不靜默正規化)──
def t_archive_crlf_skip():
    v = mkvault()
    write(v, "Verification/2020-01-01_Z.md", "type: verification\nstatus: pass\ncreated: 2020-01-01")
    # CRLF 檔,body 含 path 式連結
    p = v / "Systems/S.md"
    p.write_bytes("---\r\ntype: system\r\nstatus: done\r\n---\r\n連 [[Verification/2020-01-01_Z]]\r\n"
                  .encode("utf-8"))
    run(v, "archive", "--days", "30", "--apply", expect_rc=0)
    # Z 仍移檔,但 CRLF 檔的連結未被 rewrite(仍 path 式 + 仍 CRLF)
    txt = p.read_bytes()
    check("archive CRLF 檔跳過 rewrite(連結保留 path 式)",
          b"[[Verification/2020-01-01_Z]]" in txt and b"\r\n" in txt)


# ── archive 活守衛護欄:綁定測試仍存在的 Verification 不按年齡歸檔 ──
def t_archive_live_guard_protected():
    # 需要 docs/ 父層(repo_root 偵測)+ 一個含 [Fact] 方法的 .cs(discover_test_methods)
    root = Path(tempfile.mkdtemp(prefix="gctl-repo-"))
    (root / "Tests").mkdir()
    (root / "Tests" / "GuardTests.cs").write_bytes(
        "public class GuardTests {\n  [Fact]\n  public void MyLiveGuard() { }\n}\n".encode("utf-8"))
    vault = root / "docs" / "kg"
    for sub in ("Systems", "Verification", "MOC"):
        (vault / sub).mkdir(parents=True)
    (vault / "MOC" / "idx.md").write_bytes("---\ntype: moc\n---\n# idx\n".encode("utf-8"))
    # ★INVARIANT★ 綁定存活測試
    (vault / "Systems" / "S.md").write_bytes(
        ("---\ntype: system\nstatus: done\nsummary: |-\n"
        "  KEY:★INVARIANT★ 某載重宣稱 [test:MyLiveGuard]\n---\n# S\n").encode("utf-8"))
    # 老 Verification:提到存活測試 → 應保留
    (vault / "Verification" / "2020-01-01_guarded.md").write_bytes(
        ("---\ntype: verification\nstatus: pass\ncreated: 2020-01-01\n"
        "valid_under:\n  - MyLiveGuard\n---\n# guarded\n").encode("utf-8"))
    # 老 Verification:沒提到任何存活測試 → 應照舊歸檔
    (vault / "Verification" / "2020-01-01_plain.md").write_bytes(
        "---\ntype: verification\nstatus: pass\ncreated: 2020-01-01\n---\n# plain\n".encode("utf-8"))
    r = run(vault, "archive", "--days", "30", "--apply", expect_rc=0)
    check("活守衛護欄: 綁定測試仍存在的 Verification 保留不歸檔",
          (vault / "Verification/2020-01-01_guarded.md").exists()
          and not (vault / "Verification/Archive/2020-01/2020-01-01_guarded.md").exists(), r.stdout)
    check("活守衛護欄: 未提及存活測試的 Verification 照舊歸檔",
          (vault / "Verification/Archive/2020-01/2020-01-01_plain.md").exists(), r.stdout)


def t_archive_live_guard_multiplatform():
    """T4:活守衛護欄跨 repo。後端 C# 守衛(在 sibling repo)存活 → 提及它的老 Verification 保留。"""
    import shutil
    root = Path(tempfile.mkdtemp(prefix="gctl-arcmp-"))
    main = root / "app"
    be = root / "backend"
    (be / "App.Tests").mkdir(parents=True)
    (be / "App.Tests" / "G.cs").write_bytes(
        "using Xunit;\npublic class G {\n  [Fact]\n  public void CsGuard() { }\n}\n".encode("utf-8"))
    vault = main / "docs" / "kg"
    for sub in ("Systems", "Verification", "MOC"):
        (vault / sub).mkdir(parents=True)
    (vault / "MOC" / "idx.md").write_bytes("---\ntype: moc\n---\n# idx\n".encode("utf-8"))
    (main / ".lumos").mkdir(parents=True)
    (main / ".lumos" / "config.json").write_bytes(
        ('{"default_platform":"backend","platforms":{'
        '"backend":{"profile":"csharp-xunit","root":"../backend"}}}\n').encode("utf-8"))
    (vault / "Systems" / "S.md").write_bytes(
        ("---\ntype: system\nstatus: done\nsummary: |-\n"
        "  KEY:★INVARIANT★ 後端載重 [test:backend:CsGuard]\n---\n# S\n").encode("utf-8"))
    (vault / "Verification" / "2020-01-01_guarded.md").write_bytes(
        ("---\ntype: verification\nstatus: pass\ncreated: 2020-01-01\n"
        "valid_under:\n  - CsGuard\n---\n# guarded\n").encode("utf-8"))
    try:
        r = run(vault, "archive", "--days", "30", "--apply", expect_rc=0)
        check("活守衛護欄跨 repo: 後端 C# 守衛存活 → 提及它的 Verification 保留不歸檔",
              (vault / "Verification/2020-01-01_guarded.md").exists()
              and not (vault / "Verification/Archive/2020-01/2020-01-01_guarded.md").exists(), r.stdout)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── archive 守衛被刪(測試不在 code)→ 該 Verification 恢復可歸檔 ──
def t_archive_dead_guard_archivable():
    root = Path(tempfile.mkdtemp(prefix="gctl-repo-"))
    (root / "Tests").mkdir()  # 無任何 .cs 測試方法 → 綁定名不存在於 code
    vault = root / "docs" / "kg"
    for sub in ("Systems", "Verification", "MOC"):
        (vault / sub).mkdir(parents=True)
    (vault / "MOC" / "idx.md").write_bytes("---\ntype: moc\n---\n# idx\n".encode("utf-8"))
    (vault / "Systems" / "S.md").write_bytes(
        ("---\ntype: system\nstatus: done\nsummary: |-\n"
        "  KEY:★INVARIANT★ 某載重宣稱 [test:GoneGuard]\n---\n# S\n").encode("utf-8"))
    (vault / "Verification" / "2020-01-01_g.md").write_bytes(
        ("---\ntype: verification\nstatus: pass\ncreated: 2020-01-01\n"
        "valid_under:\n  - GoneGuard\n---\n# g\n").encode("utf-8"))
    run(vault, "archive", "--days", "30", "--apply", expect_rc=0)
    check("守衛已死(測試不在 code): Verification 恢復按年齡可歸檔",
          (vault / "Verification/Archive/2020-01/2020-01-01_g.md").exists())


# ── negative: append 到 block key 應拒 ──
def t_append_block_key_rejected():
    v = mkvault()
    write(v, "Systems/S.md", "type: system\nstatus: done\nsummary: |-\n  FLOW:A")
    # summary 不在 append 白名單 → 應 rc=2
    r = run(v, "append", "S", "summary", "x")
    check("negative: append 非白名單 key(summary)被拒", r.returncode == 2, r.stderr)


# ── negative: set 非法日期應拒 ──
def t_set_bad_date_rejected():
    v = mkvault()
    write(v, "Systems/S.md", "type: system\nstatus: done\nupdated: 2026-01-01")
    r = run(v, "set", "S", "updated", "not-a-date")
    check("negative: set updated 非法日期被拒", r.returncode == 2, r.stderr)


# ══ 第三輪審計回歸 ══

# ── export 逸出節點名中的 " (R3 latent bug) ──
def t_export_quote_escape():
    if sys.platform == "win32":
        check("export quote: NTFS 禁 \" 字元,Windows skip", True)
        return
    v = mkvault()
    write(v, 'Systems/A"B.md', "type: system\nstatus: done")
    rm = run(v, "export", "--format", "mermaid", "--folders", "Systems", expect_rc=0)
    check('export mermaid: " 逸出成 &quot;(不破語法)',
          '&quot;' in rm.stdout and 'A"B"]' not in rm.stdout, rm.stdout)
    rd = run(v, "export", "--format", "dot", "--folders", "Systems", expect_rc=0)
    check('export dot: " 逸出成 \\"(不破語法)',
          '\\"' in rd.stdout, rd.stdout)


# ── search 全文搜尋 ──
def t_search():
    v = mkvault()
    write(v, "Systems/A.md", "type: system\nstatus: done", body="# A\nServiceType 代碼說明\n")
    write(v, "Verification/B.md", "type: verification\nstatus: pass\ndate: 2026-01-01",
          body="# B\n無關內容\n")
    r = run(v, "search", "ServiceType", "--files-only", expect_rc=0)
    check("search 命中 A 不命中 B", "Systems/A.md" in r.stdout and "Verification/B.md" not in r.stdout, r.stdout)
    r2 = run(v, "search", "servicetype", "--files-only", expect_rc=0)
    check("search 大小寫不敏感", "Systems/A.md" in r2.stdout, r2.stdout)
    r3 = run(v, "search", "ServiceType", "--path", "Verification", "--files-only", expect_rc=0)
    check("search --path 限定資料夾(Systems 命中被排除)", "Systems/A.md" not in r3.stdout, r3.stdout)
    r4 = run(v, "search", "Service.*代碼", "--regex", "--files-only", expect_rc=0)
    check("search --regex", "Systems/A.md" in r4.stdout, r4.stdout)


# ── search 尊重標籤哲學: 排除 code block + 標記區域(option A) ──
def t_search_structure_aware():
    v = mkvault()
    write(v, "Systems/C.md",
          "type: system\nstatus: done\nsummary: |-\n  KEY:★INVARIANT★ widget 不可改",
          body="# C\n正文提到 widget\n```\nwidget in code block\n```\n")
    # 預設排除 code block: 只命中 frontmatter ★INVARIANT★ + body 正文,不含 code 那行
    r = run(v, "search", "widget", expect_rc=0)
    check("search 排除 code block(預設)", "widget in code block" not in r.stdout, r.stdout)
    check("search 區域標記 ★INVARIANT★", "[★INVARIANT★]" in r.stdout, r.stdout)
    check("search 區域標記 body", "[body]" in r.stdout, r.stdout)
    # --code 才含 code block 那行
    rc = run(v, "search", "widget", "--code", expect_rc=0)
    check("search --code 含 code block 內容", "widget in code block" in rc.stdout, rc.stdout)


# ══ T3 巢狀決策手術 ══

def _vault_with_decisions():
    v = mkvault()
    write(v, "Systems/X.md",
          "type: system\nstatus: done\n"
          "decisions:\n"
          "  - content: 舊方案用樂觀鎖\n"
          "    alternatives_considered:\n"
          '      - "Redis:要基礎設施"\n'
          "    why_chosen: 不增依賴\n"
          "    decided: 2026-04-01\n"
          "    valid: true\n"
          "  - content: 第二條不動\n"
          "    decided: 2026-04-02\n"
          "    valid: true")
    return v, v / "Systems/X.md"


def t_decision_supersede():
    v, p = _vault_with_decisions()
    r = run(v, "decision-supersede", "X", "樂觀鎖", "--by", "改用 Redis", "--ended", "2026-06-13")
    check("decision-supersede rc=0", r.returncode == 0, r.stderr)
    txt = read(p)
    check("supersede: 第一條 valid:false + superseded_by",
          "valid: false" in txt and "superseded_by: 改用 Redis" in txt, txt)
    check("supersede: 巢狀 alternatives_considered 子清單未被動",
          '"Redis:要基礎設施"' in txt, txt)
    check("supersede: 第二條 valid:true 未被動",
          "第二條不動\n    decided: 2026-04-02\n    valid: true" in txt, txt)


def t_decision_supersede_notfound():
    v, p = _vault_with_decisions()
    before = read(p)
    r = run(v, "decision-supersede", "X", "不存在的決策", "--by", "Y")
    check("decision-supersede 找不到 → rc=2", r.returncode == 2, r.stderr)
    check("decision-supersede 找不到 → 原檔不動", read(p) == before)


def t_decision_add():
    v, p = _vault_with_decisions()
    r = run(v, "decision-add", "X", "新決策含冒號: 測試", "--decided", "2026-06-13", "--why", "超越")
    check("decision-add rc=0", r.returncode == 0, r.stderr)
    txt = read(p)
    check("decision-add: content 含冒號自動引號",
          '"新決策含冒號: 測試"' in txt, txt)
    check("decision-add: valid:true + why_chosen", "why_chosen: 超越" in txt and txt.count("valid: true") >= 2, txt)


def t_decision_add_no_existing():
    v = mkvault()
    p = write(v, "Systems/Y.md", "type: system\nstatus: done")
    run(v, "decision-add", "Y", "首條決策", "--decided", "2026-06-13", expect_rc=0)
    txt = read(p)
    check("decision-add 無 decisions 時建立", "decisions:" in txt and "首條決策" in txt, txt)


# ══ T3 第三輪審計回歸:複雜巢狀案例 ══

def _complex_decisions_vault():
    """複雜 fixture: block scalar content + 巢狀子清單 + 多條 + decisions 後接 verified_by。"""
    v = mkvault()
    write(v, "Systems/Z.md",
          "type: system\nstatus: done\n"
          "decisions:\n"
          "  - content: |-\n"
          "      多行決策第一行\n"
          "      第二行補充說明含冒號: 細節\n"
          "    context: 當時痛點\n"
          "    alternatives_considered:\n"
          '      - "Redis:要基礎設施"\n'
          '      - "悲觀鎖:卡連線池"\n'
          "    why_chosen: 不增依賴\n"
          "    decided: 2026-04-01\n"
          "    valid: true\n"
          "  - content: 第二條短決策\n"
          "    decided: 2026-04-02\n"
          "    valid: true\n"
          "verified_by:\n"
          '  - "[[V1]]"',
          body="# Z\n")
    write(v, "Verification/V1.md", "type: verification\nstatus: pass\ndate: 2026-01-01",
          body="# V1\n驗 [[Z]]\n")  # 讓 verified_by 解析得到,fixture 本身乾淨
    return v, v / "Systems/Z.md"


def t_complex_supersede_block_scalar():
    v, p = _complex_decisions_vault()
    before = read(p)
    r = run(v, "decision-supersede", "Z", "多行決策第一行", "--by", "新方案", "--ended", "2026-06-13")
    check("複雜:block scalar content supersede rc=0", r.returncode == 0, r.stderr)
    txt = read(p)
    check("複雜:block scalar 多行 content 逐字未動",
          "多行決策第一行" in txt and "第二行補充說明含冒號: 細節" in txt, txt)
    check("複雜:巢狀子清單未動", '"Redis:要基礎設施"' in txt and '"悲觀鎖:卡連線池"' in txt, txt)
    check("複雜:why_chosen/context 未動", "why_chosen: 不增依賴" in txt and "context: 當時痛點" in txt, txt)
    check("複雜:第二條決策 valid:true 未動",
          "第二條短決策\n    decided: 2026-04-02\n    valid: true" in txt, txt)
    check("複雜:decisions 後的 verified_by 未動", '- "[[V1]]"' in txt, txt)
    check("複雜:只插了 superseded_by + ended(無重複 valid)", txt.count("valid: false") == 1, txt)


def t_complex_supersede_repeat_rejected():
    v, p = _complex_decisions_vault()
    run(v, "decision-supersede", "Z", "多行決策第一行", "--by", "第一次", expect_rc=0)
    before = read(p)
    r = run(v, "decision-supersede", "Z", "多行決策第一行", "--by", "第二次")
    check("複雜:重複 supersede → rc=2", r.returncode == 2, r.stderr)
    check("複雜:重複 supersede 原檔不動(無重複 superseded_by)",
          read(p) == before and read(p).count("superseded_by") == 1, read(p))


def t_complex_add_then_parse():
    v, p = _complex_decisions_vault()
    run(v, "decision-add", "Z", "第三條新決策", "--decided", "2026-06-13", "--why", "超越", expect_rc=0)
    # decisions 指令應讀回全部 3 條(結構沒被 add 破壞)
    r = run(v, "decisions", "Z", expect_rc=0)
    check("複雜:add 後 decisions 讀回 3 條",
          "多行決策第一行" in r.stdout and "第二條短決策" in r.stdout and "第三條新決策" in r.stdout, r.stdout)
    # add 不該插進 verified_by 之後或子清單
    txt = read(p)
    zi, vi = txt.index("第三條新決策"), txt.index("verified_by:")
    check("複雜:新決策插在 decisions 內(verified_by 之前)", zi < vi, txt)


def t_complex_consecutive_ops():
    v, p = _complex_decisions_vault()
    run(v, "decision-supersede", "Z", "第二條短決策", "--by", "翻盤2", expect_rc=0)
    run(v, "decision-add", "Z", "連續新增", "--decided", "2026-06-13", expect_rc=0)
    r = run(v, "doctor", "--vault", str(v), "--ci") if False else run(v, "doctor", "--ci")
    check("複雜:連續 supersede+add 後 doctor 仍乾淨", r.returncode == 0, r.stdout)
    r2 = run(v, "decisions", "Z", expect_rc=0)
    check("複雜:連續操作後 3 條讀回(第二條已翻盤)",
          "翻盤2" in r2.stdout and "連續新增" in r2.stdout, r2.stdout)


def t_complex_add_bad_date():
    v, p = _complex_decisions_vault()
    before = read(p)
    r = run(v, "decision-add", "Z", "壞日期決策", "--decided", "not-a-date")
    check("複雜:decision-add 非日期 → rc=2 原檔不動", r.returncode == 2 and read(p) == before, r.stderr)


def t_export_html():
    import tempfile
    v = mkvault()
    write(v, "Systems/A.md",
          "type: system\nstatus: done\nsummary: |-\n  KEY:★INVARIANT★ x\nverified_by:\n  - \"[[V1]]\"",
          body="# A\n連 [[V1]]\n含危險 </script> 字串\n")
    write(v, "Verification/V1.md", "type: verification\nstatus: stale\ndate: 2026-01-01", body="# V1\n驗 [[A]]\n")
    out = str(Path(tempfile.mkdtemp()) / "g.html")
    r = run(v, "export", "--format", "html", "--output", out, expect_rc=0)
    html = Path(out).read_text(encoding="utf-8")
    check("export html: 產出檔含 DATA + 3D 引擎(ForceGraph3D)", "const DATA" in html and "ForceGraph3D" in html, r.stdout)
    check("export html: 筆記內 </script> 被轉義成 <\\/script>", "<\\/script>" in html, "escape")
    check("export html: 結尾完整、單一 </html>(未被內文提早關閉)",
          html.rstrip().endswith("</html>") and html.count("</html>") == 1, "structure")


def t_invariant_test_binding():
    # Check T 牙齒:裸 ★INVARIANT★(無 [test:])→ doctor 擋(載重宣稱沒綁可執行證據)
    v = mkvault()
    write(v, "Systems/Naked.md",
          "type: system\nstatus: done\nsummary: |-\n  KEY:★INVARIANT★ 自動型只派 V",
          body="# Naked\n")
    r = run(v, "doctor", "--ci")
    check("Check T: 裸 ★INVARIANT★(無 test 綁定)被 doctor 擋",
          r.returncode == 1 and "裸 ★INVARIANT★" in r.stdout, r.stdout)
    # 綁了 [test:X] → 不再算裸合約(沙盒無 repo root,存在性檢查跳過)
    v2 = mkvault()
    write(v2, "Systems/Bound.md",
          "type: system\nstatus: done\nsummary: |-\n  KEY:★INVARIANT★ 自動型只派 V [test:SomeGuardTest]",
          body="# Bound\n")
    r2 = run(v2, "doctor", "--ci")
    check("Check T: 綁了 [test:] 的 ★INVARIANT★ 不算裸合約",
          "裸 ★INVARIANT★" not in r2.stdout, r2.stdout)


def t_invariant_audit_binding():
    # Check T 牙齒:綁了 [test:] 但無 [audit:] → doctor 報「未經獨立審計」(maker/checker 破口)
    v = mkvault()
    write(v, "Systems/Bound.md",
          "type: system\nstatus: done\nsummary: |-\n"
          "  KEY:★INVARIANT★ 點數不足必須擋 [test:SomeGuard]",
          body="# Bound\n")
    r = run(v, "doctor", "--ci")
    check("Check T: 綁測試但未經獨立審計 → doctor 擋(rc1)",
          r.returncode == 1 and "未經獨立審計" in r.stdout, r.stdout)
    # 加上 [audit:模型/日期] → 不再報未審
    v2 = mkvault()
    write(v2, "Systems/Aud.md",
          "type: system\nstatus: done\nsummary: |-\n"
          "  KEY:★INVARIANT★ 點數不足必須擋 [test:SomeGuard] [audit:sonnet/2026-06-18]",
          body="# Aud\n")
    r2 = run(v2, "doctor", "--ci")
    check("Check T: 有 [audit:] 留痕 → 不再報未審", "未經獨立審計" not in r2.stdout, r2.stdout)
    # 裸合約(連 [test:] 都沒)不應被未審項誤報(naked 先擋,audit 不雙重計)
    v3 = mkvault()
    write(v3, "Systems/Naked.md",
          "type: system\nstatus: done\nsummary: |-\n  KEY:★INVARIANT★ 沒綁測試的",
          body="# Naked\n")
    r3 = run(v3, "doctor", "--ci")
    check("Check T: 裸合約只報裸、不報未審(不雙重計)",
          "未經獨立審計" not in r3.stdout and "裸 ★INVARIANT★" in r3.stdout, r3.stdout)


def t_guard_audit():
    # guard audit:把 [audit:模型/日期] 留痕寫回 KEY 行,保留 [test:],重審覆蓋舊留痕
    v = mkvault()
    p = write(v, "Systems/S.md",
              "type: system\nstatus: done\nsummary: |-\n"
              "  KEY:★INVARIANT★ 點數不足必須擋 [test:SomeGuard]",
              body="# S\n")
    r = run(v, "guard", "audit", "Systems/S", "點數不足", "--date", "2026-06-18")
    txt = read(p)
    check("guard audit: [audit:] 寫回 KEY 行", "[audit:sonnet/2026-06-18]" in txt, r.stdout + r.stderr)
    check("guard audit: [test:] 綁定不受影響", "[test:SomeGuard]" in txt, txt)
    # 重審(換模型/日期)→ 覆蓋,不重複留痕
    run(v, "guard", "audit", "Systems/S", "點數不足", "--date", "2026-07-01", "--model", "opus")
    txt2 = read(p)
    check("guard audit: 重審覆蓋舊留痕(新日期生效)",
          "[audit:opus/2026-07-01]" in txt2 and "2026-06-18" not in txt2, txt2)
    check("guard audit: 不累積(只一個 audit 標記)", txt2.count("[audit:") == 1, txt2)
    # 找不到子字串 → rc2
    r3 = run(v, "guard", "audit", "Systems/S", "不存在的合約")
    check("guard audit: 子字串找不到 KEY 行 → rc2", r3.returncode == 2, r3.stdout + r3.stderr)


def t_lint():
    # 單檔快檢:乾淨節點過、各種寫入當下的錯被抓
    v = mkvault()
    # 乾淨 system(無合約)→ 0 問題
    write(v, "Systems/Clean.md",
          "type: system\nstatus: doing\nsummary: |-\n  FLOW:a→b\n  KEY:某關鍵", body="# Clean\n")
    r = run(v, "lint", "Systems/Clean")
    check("lint: 乾淨節點 rc0", r.returncode == 0 and "0 問題" in r.stdout, r.stdout)
    # 裸 ★INVARIANT★ → error rc1
    write(v, "Systems/Naked.md",
          "type: system\nstatus: doing\nsummary: |-\n  KEY:★INVARIANT★ 沒綁測試的", body="# N\n")
    r = run(v, "lint", "Systems/Naked")
    check("lint: 裸合約 → rc1 error", r.returncode == 1 and "裸 ★INVARIANT★" in r.stdout, r.stdout)
    # ★INVARIANT★ 沒當 KEY 前綴(放 FLOW 行)→ 格式 error
    write(v, "Systems/BadMark.md",
          "type: system\nstatus: doing\nsummary: |-\n  FLOW:★INVARIANT★ 放錯行", body="# B\n")
    r = run(v, "lint", "Systems/BadMark")
    check("lint: ★ 非 KEY 前綴 → rc1(格式錯,contracts 抓不到)",
          r.returncode == 1 and "必須是 KEY 行前綴" in r.stdout, r.stdout)
    # 綁測試但未審 → error
    write(v, "Systems/Unaud.md",
          "type: system\nstatus: doing\nsummary: |-\n  KEY:★INVARIANT★ 擋下 [test:G]", body="# U\n")
    r = run(v, "lint", "Systems/Unaud")
    check("lint: 綁測試未審 → rc1", r.returncode == 1 and "未獨立審計" in r.stdout, r.stdout)
    # 綁測試 + 已審 → 0 問題
    write(v, "Systems/Good.md",
          "type: system\nstatus: doing\nsummary: |-\n  KEY:★INVARIANT★ 擋下 [test:G] [audit:sonnet/2026-06-18]",
          body="# G\n")
    r = run(v, "lint", "Systems/Good")
    check("lint: 綁測試+已審 → rc0", r.returncode == 0, r.stdout)
    # system 缺 summary → error
    write(v, "Systems/NoSum.md", "type: system\nstatus: doing", body="# NS\n")
    r = run(v, "lint", "Systems/NoSum")
    check("lint: system 缺 summary → rc1", r.returncode == 1 and "summary" in r.stdout, r.stdout)
    # ghost trap(單字串多 wikilink)→ error(複用 frontmatter 指紋)
    write(v, "Systems/Ghost.md",
          "type: system\nstatus: doing\nrelated: \"[[A]], [[B]]\"\nsummary: |-\n  KEY:x", body="# Gh\n")
    r = run(v, "lint", "Systems/Ghost")
    check("lint: 單字串多 wikilink ghost trap → rc1", r.returncode == 1 and "ghost" in r.stdout.lower(), r.stdout)
    # symbol typo → warning(不阻擋 rc0)
    write(v, "Systems/Typo.md",
          "type: system\nstatus: doing\nsummary: |-\n  KYE:打錯的符號\n  KEY:正常", body="# T\n")
    r = run(v, "lint", "Systems/Typo")
    check("lint: 符號 typo → warning 不阻擋(rc0)",
          r.returncode == 0 and "非標準符號行" in r.stdout, r.stdout)
    # 找不到節點 → rc2
    r = run(v, "lint", "Systems/NoSuchNode")
    check("lint: 找不到節點 → rc2", r.returncode == 2, r.stdout + r.stderr)


def t_guard():
    """guard list/scaffold/bind — 對談驅動守衛 scaffold(2026-06-15)。
    需 repo_root + 真 .cs(discover_test_methods),故自建 docs/ 結構而非 mkvault。"""
    import shutil
    root = Path(tempfile.mkdtemp(prefix="gctl-guard-"))
    vault = root / "docs" / "demo-knowledge"
    for sub in ("Systems", "Verification", "Projects", "MOC"):
        (vault / sub).mkdir(parents=True)
    (vault / "MOC" / "idx.md").write_bytes("---\ntype: moc\n---\n# idx\n".encode("utf-8"))
    (vault / "Systems" / "Demo.md").write_bytes(
        ("---\ntype: system\nstatus: done\nsummary: |-\n"
        "  KEY:★INVARIANT★ 已綁的合約 [test:RealGuardX]\n"
        "  KEY:★INVARIANT★ 還沒綁的合約\n"
        "---\n# Demo\n").encode("utf-8"))
    td = root / "Demo.IntegrationTests"
    td.mkdir()
    (td / "RealGuard.cs").write_bytes(
        "using Xunit;\npublic class RealGuard {\n  [Fact]\n  public void RealGuardX() { }\n}\n"
        .encode("utf-8"))
    tpl = root / ".lumos" / "guard-templates"
    tpl.mkdir(parents=True)
    (tpl / "behavioral.tmpl").write_bytes(
        ("// {{NODE}} | {{INVARIANT}} | {{CLAIM}} | {{PREFIX}}\n"
        "public class {{CLASS}} {\n  public void {{METHOD}}() "
        "{ Assert.Fail(\"unfilled\"); }\n}\n").encode("utf-8"))
    try:
        r = run(vault, "guard", "list")
        check("guard list: real/naked 分類", "真綁 1" in r.stdout and "裸 1" in r.stdout, r.stdout)
        r = run(vault, "guard", "list", "--unbound")
        check("guard list --unbound: 列裸不列 real",
              "還沒綁的合約" in r.stdout and "已綁的合約" not in r.stdout, r.stdout)
        outd = root / "out"
        outd.mkdir()
        r = run(vault, "guard", "scaffold", "--node", "Systems/Demo", "--invariant", "還沒綁",
                "--method", "NewGuardX", "--type", "behavioral", "--claim", "具體可驗斷言",
                "--out", str(outd))
        f = outd / "NewGuardXTests.cs"
        txt = f.read_text(encoding="utf-8") if f.exists() else ""
        check("guard scaffold: 產出檔", f.exists(), r.stdout + r.stderr)
        check("guard scaffold: 預設紅燈 Assert.Fail", "Assert.Fail" in txt, txt)
        check("guard scaffold: placeholder 全替換", "{{" not in txt, txt)
        r = run(vault, "guard", "scaffold", "--node", "Systems/Demo", "--invariant", "還沒綁",
                "--method", "1bad", "--type", "behavioral", "--claim", "x", "--out", str(outd))
        check("guard scaffold: 非法 method 擋(rc2)", r.returncode == 2, r.stdout + r.stderr)
        r = run(vault, "guard", "scaffold", "--node", "Systems/Demo",
                "--invariant", "RealGuardX", "--method", "Zz", "--type", "behavioral",
                "--claim", "x", "--out", str(outd))
        check("guard scaffold: --invariant 不誤命中 [test:] 名(rc2)",
              r.returncode == 2, r.stdout + r.stderr)
        r = run(vault, "guard", "bind", "Systems/Demo", "還沒綁", "NewGuardX")
        nt = (vault / "Systems" / "Demo.md").read_text(encoding="utf-8")
        check("guard bind: [test:] 寫回 KEY 行", "[test:NewGuardX]" in nt, r.stdout + r.stderr)
        check("guard bind: 已綁行不受影響", nt.count("[test:RealGuardX]") == 1, nt)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_guard_trace():
    """guard trace — 合約→守衛測試→Verification 證據鏈(reverse lookup)。"""
    v = mkvault()
    write(v, "Systems/Mod.md",
          "type: system\nstatus: done\nsummary: |-\n"
          "  KEY:★INVARIANT★ 某合約 [test:MyGuardTest]",
          body="# Mod\n")
    write(v, "Verification/2026-01-02_g.md", "type: verification\nstatus: pass",
          body="# g\n本守衛 MyGuardTest 跑 lab PASS\n")
    r = run(v, "guard", "trace", "Systems/Mod")
    check("guard trace: 合約→測試→Verification 鏈",
          "MyGuardTest" in r.stdout and "2026-01-02_g" in r.stdout, r.stdout)
    write(v, "Systems/Lonely.md",
          "type: system\nstatus: done\nsummary: |-\n  KEY:★INVARIANT★ 沒人測 [test:NobodyTestsThis]",
          body="# Lonely\n")
    r = run(v, "guard", "trace", "Systems/Lonely")
    check("guard trace: 無 Verification 提到 → 明示",
          "無 Verification 提到" in r.stdout, r.stdout)
    # Finding 4: 只有裸合約的節點不可印「無合約」矛盾 footer
    write(v, "Systems/NakedOnly.md",
          "type: system\nstatus: done\nsummary: |-\n  KEY:★INVARIANT★ 裸合約A\n  KEY:★INVARIANT★ 裸合約B",
          body="# NakedOnly\n")
    r = run(v, "guard", "trace", "Systems/NakedOnly")
    check("guard trace: 裸合約節點不印『無合約』矛盾",
          "★INVARIANT★" in r.stdout and "無 ★INVARIANT★ 合約" not in r.stdout, r.stdout)
    # Finding 3: code block 內方法名不算證據
    write(v, "Systems/Cb.md",
          "type: system\nstatus: done\nsummary: |-\n  KEY:★INVARIANT★ 某 [test:OnlyInCodeBlock]",
          body="# Cb\n")
    write(v, "Verification/2026-01-03_cb.md", "type: verification\nstatus: pass",
          body="# cb\n```\nOnlyInCodeBlock 只出現在 code block\n```\n")
    r = run(v, "guard", "trace", "Systems/Cb")
    check("guard trace: code block 內方法名不算證據",
          "無 Verification 提到" in r.stdout, r.stdout)


def t_sync_verified_by():
    """sync-verified-by — 補 Check 3 漏寫(dry-run 預設 / --apply 寫 / 冪等)。"""
    v = mkvault()
    write(v, "Systems/Pay.md", "type: system\nstatus: done", body="# Pay\n")
    write(v, "Verification/2026-01-01_payv.md", "type: verification\nstatus: pass",
          body="# payv\n## 相關模組\n- [[Systems/Pay]]\n")
    r = run(v, "sync-verified-by")
    check("sync dry-run: 列出漏寫", "Systems/Pay.md" in r.stdout and "待補" in r.stdout, r.stdout)
    check("sync dry-run: 不寫入", "verified_by" not in read(v / "Systems" / "Pay.md"))
    r = run(v, "sync-verified-by", "--apply")
    check("sync --apply: 寫入 verified_by",
          "2026-01-01_payv" in read(v / "Systems" / "Pay.md"), r.stdout + r.stderr)
    r = run(v, "sync-verified-by")
    check("sync 冪等: 補完後無漏", "無漏寫" in r.stdout, r.stdout)


def t_guard_kotlin():
    """P5 語言可插拔:.lumos/config.json test_profile=kotlin-junit →
    discover 認 @Test fun(.kt)、scaffold 寫 .kt、rglob 偵測巢狀 src/test。"""
    import shutil
    root = Path(tempfile.mkdtemp(prefix="gctl-kt-"))
    vault = root / "docs" / "demo-knowledge"
    for sub in ("Systems", "Verification", "Projects", "MOC"):
        (vault / sub).mkdir(parents=True)
    (vault / "MOC" / "idx.md").write_bytes("---\ntype: moc\n---\n# idx\n".encode("utf-8"))
    (vault / "Systems" / "Login.md").write_bytes(
        ("---\ntype: system\nstatus: done\nsummary: |-\n"
        "  KEY:★INVARIANT★ 登入鎖定 [test:LoginLocksAfterFiveFails]\n"
        "---\n# Login\n").encode("utf-8"))
    (root / ".lumos").mkdir(parents=True)
    (root / ".lumos" / "config.json").write_bytes(
        '{"test_profile": "kotlin-junit"}\n'.encode("utf-8"))
    ktdir = root / "app" / "src" / "test" / "java" / "auth"
    ktdir.mkdir(parents=True)
    (ktdir / "LoginTest.kt").write_bytes(
        ("package auth\nimport org.junit.Test\nclass LoginTest {\n"
        "  @Test\n  fun LoginLocksAfterFiveFails() { }\n}\n").encode("utf-8"))
    tpl = root / ".lumos" / "guard-templates"
    tpl.mkdir(parents=True)
    (tpl / "pure.tmpl").write_bytes(
        ("// {{NODE}} | {{INVARIANT}} | {{CLAIM}}\nclass {{CLASS}} {\n"
        "  @Test fun {{METHOD}}() { fail(\"unfilled\") }\n}\n").encode("utf-8"))
    try:
        r = run(vault, "guard", "list")
        check("guard kotlin: @Test fun 認成真方法(real)", "真綁 1" in r.stdout, r.stdout)
        outd = root / "out"
        outd.mkdir()
        r = run(vault, "guard", "scaffold", "--node", "Systems/Login", "--invariant", "登入鎖定",
                "--method", "NewKtGuard", "--type", "pure", "--claim", "連五次失敗鎖定", "--out", str(outd))
        check("guard kotlin: scaffold 寫 .kt 副檔名",
              (outd / "NewKtGuardTests.kt").exists(), r.stdout + r.stderr)
        r = run(vault, "guard", "scaffold", "--node", "Systems/Login", "--invariant", "登入鎖定",
                "--method", "AutoDetectKt", "--type", "pure", "--claim", "x")
        check("guard kotlin: rglob 偵測巢狀 src/test",
              (root / "app" / "src" / "test" / "AutoDetectKtTests.kt").exists(), r.stdout + r.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_maestro_profile_discover():
    """T1 多平台:test_profile=maestro → discover 認 flow name:(含 appId 的 .yaml);
    file_must_match 濾掉無 appId 的 yaml(CI 檔);多字 name 因 \\s*$ 錨 NO MATCH。"""
    import shutil
    root = Path(tempfile.mkdtemp(prefix="gctl-mae-"))
    vault = root / "docs" / "demo-knowledge"
    for sub in ("Systems", "Verification", "Projects", "MOC"):
        (vault / sub).mkdir(parents=True)
    (vault / "MOC" / "idx.md").write_bytes("---\ntype: moc\n---\n# idx\n".encode("utf-8"))
    # 三條 invariant:checkoutFlow=real / buildJob=dangling(無 appId 被 file_must_match 濾)
    #              / should=dangling(多字 name NO MATCH)
    (vault / "Systems" / "Flow.md").write_bytes(
        ("---\ntype: system\nstatus: done\nsummary: |-\n"
        "  KEY:★INVARIANT★ 結帳流程 [test:checkoutFlow]\n"
        "  KEY:★INVARIANT★ 建置任務 [test:buildJob]\n"
        "  KEY:★INVARIANT★ 應顯示選單 [test:should]\n"
        "---\n# Flow\n").encode("utf-8"))
    (root / ".lumos").mkdir(parents=True)
    (root / ".lumos" / "config.json").write_bytes('{"test_profile": "maestro"}\n'.encode("utf-8"))
    mdir = root / ".maestro"
    mdir.mkdir(parents=True)
    (mdir / "checkout.yaml").write_bytes(
        ("appId: com.example.app\nname: checkoutFlow\ntags: [checkout]\n---\n- launchApp\n").encode("utf-8"))
    (mdir / "menu.yaml").write_bytes(   # 多字 name + 含 appId → \s*$ 錨 NO MATCH
        ("appId: com.example.app\nname: 'should show menu'\n---\n- launchApp\n").encode("utf-8"))
    ci = root / ".github" / "workflows"   # 無 appId 的 CI yaml → file_must_match 濾掉
    ci.mkdir(parents=True)
    (ci / "ci.yml").write_bytes(
        ("name: buildJob\non: [push]\njobs:\n  b:\n    runs-on: ubuntu-latest\n").encode("utf-8"))
    try:
        r = run(vault, "guard", "list")
        check("maestro: flow name:(含 appId)認成真方法 → 真綁 1", "真綁 1" in r.stdout, r.stdout)
        check("maestro: file_must_match 濾無 appId + 多字 name NO MATCH → 懸空 2",
              "懸空 2" in r.stdout, r.stdout)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_playwright_profile_discover():
    """T1 多平台:test_profile=playwright → discover 認 test('id')/test.describe('id');
    多字 title NO MATCH(識別字 capture 後需緊接引號)。"""
    import shutil
    root = Path(tempfile.mkdtemp(prefix="gctl-pw-"))
    vault = root / "docs" / "demo-knowledge"
    for sub in ("Systems", "Verification", "Projects", "MOC"):
        (vault / sub).mkdir(parents=True)
    (vault / "MOC" / "idx.md").write_bytes("---\ntype: moc\n---\n# idx\n".encode("utf-8"))
    (vault / "Systems" / "Web.md").write_bytes(
        ("---\ntype: system\nstatus: done\nsummary: |-\n"
        "  KEY:★INVARIANT★ 登入 [test:loginWorks]\n"
        "  KEY:★INVARIANT★ 選單 [test:should]\n"
        "---\n# Web\n").encode("utf-8"))
    (root / ".lumos").mkdir(parents=True)
    (root / ".lumos" / "config.json").write_bytes('{"test_profile": "playwright"}\n'.encode("utf-8"))
    tdir = root / "tests"
    tdir.mkdir(parents=True)
    (tdir / "login.spec.ts").write_bytes(
        ("import { test } from '@playwright/test';\n"
        "test('loginWorks', async ({ page }) => {});\n"
        "test('should show menu', async ({ page }) => {});\n").encode("utf-8"))
    try:
        r = run(vault, "guard", "list")
        check("playwright: test('id') 認成真方法 → 真綁 1", "真綁 1" in r.stdout, r.stdout)
        # 多字 title 'should show menu' NO MATCH → 不被收成 real(loginWorks 才 real;
        # 'should' 作為子字串在 .ts 內 → 歸偽證據,非 real)。斷言只有 1 條 real。
        check("playwright: 多字 title 未被收成 real(真綁不為 2)",
              "真綁 1" in r.stdout and "真綁 2" not in r.stdout, r.stdout)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _import_lumos():
    """把 scripts/lumos 當模組載入(檔名無 .py → 用 SourceFileLoader)供單元測試內部函式。"""
    import importlib.util
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("lumos_mod", GRAPHCTL)
    spec = importlib.util.spec_from_loader("lumos_mod", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    return m


def t_load_platforms():
    """T2 多根多 profile 載入:向後相容(無 config/舊 test_profile)+ 多平台 map +
    default_platform 規則(缺省報錯/指向不存在報錯)+ multiplatform 信號。"""
    import shutil
    m = _import_lumos()
    root = Path(tempfile.mkdtemp(prefix="gctl-lp-"))
    (root / "docs" / "demo-knowledge" / "MOC").mkdir(parents=True)
    cfg = root / ".lumos"
    cfg.mkdir()

    def setcfg(s):
        (cfg / "config.json").write_bytes(s.encode("utf-8")) if s is not None else \
            (cfg / "config.json").unlink(missing_ok=True)

    try:
        # 1. 無 config → legacy 單一條目 csharp-xunit、multiplatform False
        setcfg(None)
        r = m.load_platforms(root)
        check("load_platforms: 無 config → multiplatform False + csharp-xunit 單條目",
              r["multiplatform"] is False and list(r["platforms"]) == ["csharp-xunit"]
              and r["default_platform"] == "csharp-xunit"
              and r["platforms"]["csharp-xunit"]["root"] == root, repr(r))
        # 2. 舊 test_profile=kotlin-junit → legacy 單條目 kotlin-junit
        setcfg('{"test_profile": "kotlin-junit"}')
        r = m.load_platforms(root)
        check("load_platforms: 舊 test_profile → multiplatform False + kotlin-junit 單條目",
              r["multiplatform"] is False and list(r["platforms"]) == ["kotlin-junit"], repr(r))
        # 3. 多平台 map → multiplatform True、root 解析(../be 相對 repo_root)、default 生效
        (root.parent / (root.name + "-be")).mkdir(exist_ok=True)  # 讓 ../<name>-be 存在
        setcfg('{"default_platform":"android","platforms":{'
               '"android":{"profile":"kotlin-junit","root":"."},'
               '"backend":{"profile":"csharp-xunit","root":"../%s-be"}}}' % root.name)
        r = m.load_platforms(root)
        check("load_platforms: 多平台 → multiplatform True + 2 平台 + default android",
              r["multiplatform"] is True and set(r["platforms"]) == {"android", "backend"}
              and r["default_platform"] == "android"
              and r["platforms"]["backend"]["root"] == (root.parent / (root.name + "-be")).resolve(),
              repr(r))
        check("load_platforms: 平台 profile 解析為 profile dict(非字串)",
              r["platforms"]["android"]["profile"]["method_re"] is m.KOTLIN_TEST_RE, repr(r))
        # 4. 多平台缺 default_platform 且 >1 → 報錯(raise)
        setcfg('{"platforms":{"a":{"profile":"kotlin-junit","root":"."},'
               '"b":{"profile":"csharp-xunit","root":"."}}}')
        try:
            m.load_platforms(root); ok4 = False
        except (ValueError, SystemExit):
            ok4 = True
        check("load_platforms: 多平台缺 default_platform 且 >1 → 報錯", ok4)
        # 5. default_platform 指向不存在的鍵 → 報錯
        setcfg('{"default_platform":"ghost","platforms":{"a":{"profile":"kotlin-junit","root":"."}}}')
        try:
            m.load_platforms(root); ok5 = False
        except (ValueError, SystemExit):
            ok5 = True
        check("load_platforms: default_platform 指向不存在鍵 → 報錯", ok5)
    finally:
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(root.parent / (root.name + "-be"), ignore_errors=True)


def t_resolve_test_refs():
    """T3 平台前綴解析:resolve_test_refs(inv, platforms, default) → [(plat,name)]。
    多平台:含冒號段前綴須為已定義平台(否則報錯)、無冒號段歸 default;
    legacy(platforms 空):不切分,整串(含冒號)配 default。"""
    m = _import_lumos()
    plats = {"android": {}, "backend": {}}   # resolve 只看鍵名

    def inv(s):
        return f"KEY:★INVARIANT★ 某 {s}"

    # 多平台:雙前綴
    check("resolve: [test:android:X,backend:Y] → 兩平台各一",
          m.resolve_test_refs(inv("[test:android:X,backend:Y]"), plats, "android")
          == [("android", "X"), ("backend", "Y")])
    # 多平台:無前綴段落 fallback default
    check("resolve: [test:android:X,Y] → Y 歸 default(android)",
          m.resolve_test_refs(inv("[test:android:X,Y]"), plats, "android")
          == [("android", "X"), ("android", "Y")])
    # 多平台:裸 ref → default
    check("resolve: [test:X] 裸 ref → default",
          m.resolve_test_refs(inv("[test:X]"), plats, "android") == [("android", "X")])
    # 多平台:未定義前綴 → 報錯
    try:
        m.resolve_test_refs(inv("[test:foo:X]"), plats, "android"); okf = False
    except ValueError:
        okf = True
    check("resolve: [test:foo:X](foo 非平台)→ 報錯", okf)
    # legacy:platforms 空 → 不切分,整串配 default
    check("resolve legacy: [test:orderNote] → (default, orderNote)",
          m.resolve_test_refs(inv("[test:orderNote]"), {}, "csharp-xunit")
          == [("csharp-xunit", "orderNote")])
    check("resolve legacy: [test:foo:bar] → 不切分,整串當方法名(dangling 非報錯)",
          m.resolve_test_refs(inv("[test:foo:bar]"), {}, "csharp-xunit")
          == [("csharp-xunit", "foo:bar")])


def t_multiplatform_guard_list():
    """T4 跨 repo 多平台:圖譜在主 repo,invariant 綁前端 Kotlin(root=.)+ 後端 C#(root=../be)。
    guard list 依平台各自 discover → 兩條都 real;未定義方法 → dangling。"""
    import shutil
    root = Path(tempfile.mkdtemp(prefix="gctl-mp-"))
    main = root / "app"                       # 主 repo(圖譜所在)
    be = root / "backend"                     # 後端 sibling repo
    vault = main / "docs" / "demo-knowledge"
    for sub in ("Systems", "Verification", "Projects", "MOC"):
        (vault / sub).mkdir(parents=True)
    (vault / "MOC" / "idx.md").write_bytes("---\ntype: moc\n---\n# idx\n".encode("utf-8"))
    (vault / "Systems" / "X.md").write_bytes(
        ("---\ntype: system\nstatus: done\nsummary: |-\n"
        "  KEY:★INVARIANT★ 前端 [test:android:KtGuard]\n"
        "  KEY:★INVARIANT★ 後端 [test:backend:CsGuard]\n"
        "  KEY:★INVARIANT★ 缺 [test:android:NopeMissing]\n"
        "---\n# X\n").encode("utf-8"))
    (main / ".lumos").mkdir(parents=True)
    (main / ".lumos" / "config.json").write_bytes(
        ('{"default_platform":"android","platforms":{'
        '"android":{"profile":"kotlin-junit","root":"."},'
        '"backend":{"profile":"csharp-xunit","root":"../backend"}}}\n').encode("utf-8"))
    # 前端 Kotlin 測試(主 repo)
    ktdir = main / "src" / "test" / "java"
    ktdir.mkdir(parents=True)
    (ktdir / "G.kt").write_bytes(
        ("import org.junit.Test\nclass G {\n  @Test\n  fun KtGuard() { }\n}\n").encode("utf-8"))
    # 後端 C# 測試(sibling repo)
    csdir = be / "App.Tests"
    csdir.mkdir(parents=True)
    (csdir / "G.cs").write_bytes(
        ("using Xunit;\npublic class G {\n  [Fact]\n  public void CsGuard() { }\n}\n").encode("utf-8"))
    try:
        r = run(vault, "guard", "list")
        check("多平台 guard list: 前端 Kotlin + 後端 C# 跨 repo 各自 discover → 真綁 2",
              "真綁 2" in r.stdout, r.stdout)
        check("多平台 guard list: 未定義方法 → 懸空 1", "懸空 1" in r.stdout, r.stdout)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_multiplatform_doctor_check_t():
    """T4 doctor Check T 多平台:跨 repo 綁定 + 審計 → 過(rc0);未定義平台前綴 → 明確報錯。"""
    import shutil

    def build(inv_lines):
        root = Path(tempfile.mkdtemp(prefix="gctl-mpd-"))
        main = root / "app"
        be = root / "backend"
        vault = main / "docs" / "demo-knowledge"
        for sub in ("Systems", "Verification", "Projects", "MOC"):
            (vault / sub).mkdir(parents=True)
        (vault / "MOC" / "idx.md").write_bytes("---\ntype: moc\n---\n# idx\n".encode("utf-8"))
        (vault / "Systems" / "X.md").write_bytes(
            ("---\ntype: system\nstatus: done\nsummary: |-\n" + inv_lines + "---\n# X\n").encode("utf-8"))
        (main / ".lumos").mkdir(parents=True)
        (main / ".lumos" / "config.json").write_bytes(
            ('{"default_platform":"android","platforms":{'
            '"android":{"profile":"kotlin-junit","root":"."},'
            '"backend":{"profile":"csharp-xunit","root":"../backend"}}}\n').encode("utf-8"))
        ktdir = main / "src" / "test" / "java"
        ktdir.mkdir(parents=True)
        (ktdir / "G.kt").write_bytes(
            ("import org.junit.Test\nclass G {\n  @Test\n  fun KtGuard() { }\n}\n").encode("utf-8"))
        csdir = be / "App.Tests"
        csdir.mkdir(parents=True)
        (csdir / "G.cs").write_bytes(
            ("using Xunit;\npublic class G {\n  [Fact]\n  public void CsGuard() { }\n}\n").encode("utf-8"))
        return root, vault

    # A. 兩平台都綁真方法 + 審計 → Check T 不擋(無裸/懸空/未審)
    root, vault = build(
        "  KEY:★INVARIANT★ 前端 [test:android:KtGuard] [audit:sonnet/2026-07-02]\n"
        "  KEY:★INVARIANT★ 後端 [test:backend:CsGuard] [audit:sonnet/2026-07-02]\n")
    try:
        r = run(vault, "doctor", "--ci")
        check("doctor 多平台: 跨 repo 綁真方法+審計 → Check T 全過(2 條真綁真方法)",
              "都綁了真實可執行測試方法" in r.stdout
              and "條懸空 test_ref" not in r.stdout and "條偽證據" not in r.stdout, r.stdout)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    # B. 未定義平台前綴 → 明確報錯
    root, vault = build(
        "  KEY:★INVARIANT★ 亂平台 [test:ghost:Foo] [audit:sonnet/2026-07-02]\n")
    try:
        r = run(vault, "doctor", "--ci")
        check("doctor 多平台: 未定義平台前綴 → 報錯(rc1)",
              r.returncode == 1 and ("ghost" in r.stdout or "未定義" in r.stdout), r.stdout)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_guard_trace_multiplatform():
    """T4:guard trace 對 [test:平台:名] 應剝前綴後再搜 Verification(否則 android:X 對不上只寫 X 的篇)。"""
    import shutil
    root = Path(tempfile.mkdtemp(prefix="gctl-trmp-"))
    main = root / "app"
    vault = main / "docs" / "kg"
    for sub in ("Systems", "Verification", "MOC"):
        (vault / sub).mkdir(parents=True)
    (vault / "MOC" / "idx.md").write_bytes("---\ntype: moc\n---\n# idx\n".encode("utf-8"))
    (main / ".lumos").mkdir(parents=True)
    (main / ".lumos" / "config.json").write_bytes(
        ('{"default_platform":"android","platforms":{'
        '"android":{"profile":"kotlin-junit","root":"."}}}\n').encode("utf-8"))
    (vault / "Systems" / "S.md").write_bytes(
        ("---\ntype: system\nstatus: done\nsummary: |-\n"
        "  KEY:★INVARIANT★ 前端 [test:android:BuzzerMapsGuard]\n---\n# S\n").encode("utf-8"))
    (vault / "Verification" / "2026-07-02_buzzer.md").write_bytes(
        ("---\ntype: verification\nstatus: pass\ncreated: 2026-07-02\n---\n"
        "# buzzer\n驗證方法 BuzzerMapsGuard 通過。\n").encode("utf-8"))
    try:
        r = run(vault, "guard", "trace")
        check("guard trace 多平台: 剝平台前綴後命中提及裸方法名的 Verification",
              "2026-07-02_buzzer" in r.stdout, r.stdout)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_guard_bind_scaffold_platform():
    """T5:--platform 讓 method 維持識別字、平台另帶。bind 寫 [test:平台:方法]+去重;
    scaffold 依該平台 root+profile 選 scaffold_ext。"""
    import shutil
    root = Path(tempfile.mkdtemp(prefix="gctl-plat-"))
    main = root / "app"
    be = root / "backend"
    vault = main / "docs" / "kg"
    for sub in ("Systems", "Verification", "MOC"):
        (vault / sub).mkdir(parents=True)
    (vault / "MOC" / "idx.md").write_bytes("---\ntype: moc\n---\n# idx\n".encode("utf-8"))
    (main / ".lumos").mkdir(parents=True)
    (main / ".lumos" / "config.json").write_bytes(
        ('{"default_platform":"android","platforms":{'
        '"android":{"profile":"kotlin-junit","root":"."},'
        '"backend":{"profile":"csharp-xunit","root":"../backend"}}}\n').encode("utf-8"))
    (vault / "Systems" / "S.md").write_bytes(
        ("---\ntype: system\nstatus: done\nsummary: |-\n"
        "  KEY:★INVARIANT★ 後端載重宣稱ABC\n---\n# S\n").encode("utf-8"))
    (be / "App.Tests").mkdir(parents=True)
    # backend 平台的 guard-template(scaffold 從該平台 root 找)
    tpl = be / ".lumos" / "guard-templates"
    tpl.mkdir(parents=True)
    (tpl / "behavioral.tmpl").write_bytes(
        ("// {{NODE}} | {{INVARIANT}} | {{CLAIM}}\npublic class {{CLASS}} {\n"
        "  [Fact] public void {{METHOD}}() { Assert.Fail(\"unfilled\"); }\n}\n").encode("utf-8"))
    try:
        # bind --platform → 寫 [test:backend:CsGuard]
        r = run(vault, "guard", "bind", "Systems/S", "後端載重宣稱ABC", "CsGuard", "--platform", "backend")
        s = read(vault / "Systems" / "S.md")
        check("bind --platform: KEY 行寫入 [test:backend:CsGuard]",
              "[test:backend:CsGuard]" in s, s + r.stdout + r.stderr)
        # 再綁一次 → 去重(比完整 ref backend:CsGuard)
        r2 = run(vault, "guard", "bind", "Systems/S", "後端載重宣稱ABC", "CsGuard", "--platform", "backend")
        check("bind --platform: 重綁去重(比完整 platform:method)", "已綁" in r2.stdout, r2.stdout)
        # scaffold --platform backend → 用 csharp scaffold_ext(.cs)、從 backend root 找 template
        outd = be / "App.Tests"
        r3 = run(vault, "guard", "scaffold", "--node", "Systems/S", "--invariant", "後端載重宣稱ABC",
                 "--method", "NewCsG", "--type", "behavioral", "--platform", "backend",
                 "--claim", "x", "--out", str(outd))
        check("scaffold --platform: 依 backend profile 寫 .cs 副檔名",
              (outd / "NewCsGTests.cs").exists(), r3.stdout + r3.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_guard_profile_robustness():
    """P5 審計修正:壞 config 不 crash(F1)、ReDoS regex 拒用不 hang(F2)、null profile(F8)。"""
    import shutil
    root = Path(tempfile.mkdtemp(prefix="gctl-rob-"))
    vault = root / "docs" / "demo-knowledge"
    for sub in ("Systems", "Verification", "Projects", "MOC"):
        (vault / sub).mkdir(parents=True)
    (vault / "MOC" / "idx.md").write_bytes("---\ntype: moc\n---\n# idx\n".encode("utf-8"))
    (vault / "Systems" / "Z.md").write_bytes(
        "---\ntype: system\nstatus: done\nsummary: |-\n  KEY:★INVARIANT★ 某 [test:RealZ]\n---\n# Z\n"
        .encode("utf-8"))
    (root / "Z.Tests").mkdir()
    (root / "Z.Tests" / "Z.cs").write_bytes(
        "using Xunit;\npublic class Z {\n  [Fact]\n  public void RealZ() { }\n}\n".encode("utf-8"))
    cfgdir = root / ".lumos"
    cfgdir.mkdir()

    def setcfg(s):
        (cfgdir / "config.json").write_bytes(s.encode("utf-8"))

    try:
        setcfg('{"test": "oops"}')   # F1: test 非 dict
        r = run(vault, "doctor", "--ci")
        check("F1: test 非 dict 不 crash", "Traceback" not in r.stderr, r.stderr)
        setcfg('{"test_profile": "kotlin-junit", "test": {"exts": ".kt"}}')  # F1: exts 字串
        r = run(vault, "guard", "list")
        check("F1: exts 字串不 crash", "Traceback" not in r.stderr, r.stderr)
        setcfg('{"test": {"method_regex": "(a+)+$"}}')   # F2: ReDoS(若 hang 整個測試會卡死)
        r = run(vault, "doctor", "--ci")
        check("F2: ReDoS regex 拒用不 hang", "Traceback" not in r.stderr, r.stderr)
        setcfg('{"test_profile": null}')   # F8: null → csharp 預設,RealZ real
        r = run(vault, "guard", "list")
        check("F8: test_profile null → csharp 預設(真綁 1)", "真綁 1" in r.stdout, r.stdout)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_stale_candidate():
    """P2 stale --candidate(須配 --match):聚焦『改 X 該重驗哪幾篇』。
    含護欄(bare candidate / 空 match 報錯)、compose、block scalar 展開、Archive 標記。"""
    v = mkvault()
    write(v, "Verification/2026-01-01_a.md",
          "type: verification\nstatus: pass\nrevalidate_when:\n  - schema 變更\n  - 比率調整",
          body="# a\n")
    write(v, "Verification/2026-01-02_b.md", "type: verification\nstatus: pass", body="# b\n")
    write(v, "Verification/2026-01-03_c.md",
          "type: verification\nstatus: pass\nrevalidate_when:\n  - DispatchLog 改寫", body="# c\n")
    write(v, "Verification/2026-01-04_d.md",   # block scalar:DispatchLog 在第二行
          "type: verification\nstatus: pass\nrevalidate_when: |-\n  第一行條件\n  DispatchLog 第二行",
          body="# d\n")
    write(v, "Verification/Archive/2025-01/arch.md",
          "type: verification\nstatus: pass\nrevalidate_when:\n  - DispatchLog 舊", body="# arch\n")
    # 護欄:bare --candidate 無 --match → rc2
    r = run(v, "stale", "--candidate")
    check("stale: bare --candidate 須配 --match(rc2)", r.returncode == 2, r.stdout + r.stderr)
    # 護欄:空 --match → rc2
    r = run(v, "stale", "--match", "")
    check("stale: 空 --match → rc2", r.returncode == 2, r.stdout + r.stderr)
    # compose 聚焦
    r = run(v, "stale", "--candidate", "--match", "DispatchLog")
    check("compose: 命中 c", "2026-01-03_c" in r.stdout, r.stdout)
    check("compose: block scalar 第二行命中 d(未截斷)", "2026-01-04_d" in r.stdout, r.stdout)
    check("compose: 濾掉不含關鍵字的 a", "2026-01-01_a" not in r.stdout, r.stdout)
    check("compose: 排除 Archive", "Archive" not in r.stdout, r.stdout)
    # --match 路徑(非 candidate):含 Archive 且標 [archived]
    r = run(v, "stale", "--match", "DispatchLog")
    check("stale --match: Archive 命中標 [archived]", "[archived]" in r.stdout, r.stdout)
    check("stale --match: 含活躍 c", "2026-01-03_c" in r.stdout, r.stdout)


def t_archive_live_guard_wordboundary():
    """P3:活守衛護欄詞界比對 — 短/前綴 live 方法名不假性護住無關 Verification。"""
    import shutil
    root = Path(tempfile.mkdtemp(prefix="gctl-arch-"))
    vault = root / "docs" / "demo-knowledge"
    for sub in ("Systems", "Verification", "Projects", "MOC"):
        (vault / sub).mkdir(parents=True)
    (vault / "MOC" / "i.md").write_bytes("---\ntype: moc\n---\n# i\n".encode("utf-8"))
    (vault / "Systems" / "S.md").write_bytes(   # live guard 方法名 "Pay"(短)
        "---\ntype: system\nstatus: done\nsummary: |-\n  KEY:★INVARIANT★ 付款 [test:Pay]\n---\n# S\n"
        .encode("utf-8"))
    (root / "S.Tests").mkdir()
    (root / "S.Tests" / "S.cs").write_bytes(
        "using Xunit;\npublic class S { [Fact] public void Pay() {} }\n".encode("utf-8"))
    (vault / "Verification" / "2020-01-01_exact.md").write_bytes(   # 精確提 Pay → 護住
        "---\ntype: verification\nstatus: pass\ncreated: 2020-01-01\n---\n# e\n守衛 Pay 跑綠\n"
        .encode("utf-8"))
    (vault / "Verification" / "2020-01-02_substr.md").write_bytes(  # 只提 Payment → 不該護
        "---\ntype: verification\nstatus: pass\ncreated: 2020-01-02\n---\n# s\n講 Payment 流程,與守衛無關\n"
        .encode("utf-8"))
    try:
        r = subprocess.run([sys.executable, GRAPHCTL, "--vault", str(vault), "archive", "--days", "30"],
                           capture_output=True, text=True)
        check("archive 護欄: 精確提 Pay 的篇被護住(backs: Pay)",
              "2020-01-01_exact.md  (backs: Pay)" in r.stdout, r.stdout)
        check("archive 護欄: 只提 Payment(超字串)不被護住",
              "2020-01-02_substr.md  (backs" not in r.stdout, r.stdout)
        # CJK 緊貼方法名(無空格)仍須護住(re.ASCII 詞界;否則 Unicode \b 漏護)
        (vault / "Verification" / "2020-01-03_cjk.md").write_bytes(
            "---\ntype: verification\nstatus: pass\ncreated: 2020-01-03\n---\n# c\n守衛Pay跑綠無空格\n"
            .encode("utf-8"))
        r = subprocess.run([sys.executable, GRAPHCTL, "--vault", str(vault), "archive", "--days", "30"],
                           capture_output=True, text=True)
        check("archive 護欄: CJK 緊貼方法名仍護住(re.ASCII)",
              "2020-01-03_cjk.md  (backs: Pay)" in r.stdout, r.stdout)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_doctor_suggest():
    """P4 doctor --suggest:orphan Verification 推薦掛載 Systems(正文連結>plan_refs>feature/檔名)。"""
    v = mkvault()
    write(v, "Systems/Billing.md", "type: system\nstatus: done", body="# Billing\n")
    write(v, "Systems/Auth.md", "type: system\nstatus: done", body="# Auth\n")
    write(v, "Projects/X_計劃.md", "type: project\nstatus: doing", body="計劃連 [[Systems/Auth]]\n")
    write(v, "Verification/2026-01-01_a.md", "type: verification\nstatus: pass",
          body="# a\n驗 [[Systems/Billing]]\n")                              # 正文連向
    write(v, "Verification/2026-01-02_b.md",
          "type: verification\nstatus: pass\nplan_refs:\n  - \"[[X_計劃]]\"", body="# b\n")  # plan_refs
    write(v, "Verification/2026-01-03_c.md",
          "type: verification\nstatus: pass\nfeature: 修 Billing 的問題", body="# c\n")        # feature
    write(v, "Verification/2026-01-04_d.md", "type: verification\nstatus: pass", body="# d\n")  # 無線索
    r = run(v, "doctor", "--suggest")
    check("suggest: 正文連向 → 推薦 Billing",
          "2026-01-01_a" in r.stdout and "推薦 Systems/Billing.md" in r.stdout, r.stdout)
    check("suggest: plan_refs → 經計劃推薦 Auth",
          "經 plan_refs" in r.stdout and "Systems/Auth.md" in r.stdout, r.stdout)
    check("suggest: feature 提到 stem → 推薦", "feature 提到「Billing」" in r.stdout, r.stdout)
    check("suggest: 無線索 → 明示人工判斷", "人工判斷" in r.stdout, r.stdout)
    # 不帶 --suggest:Check 1 維持原本扁平清單(向後相容)
    r = run(v, "doctor")
    check("doctor(無 --suggest)不印推薦", "推薦 Systems" not in r.stdout, r.stdout)
    # Bug-1 前綴重疊抑制:feature 提「點數商城」不該也推薦子字串 Systems「點數」
    v2 = mkvault()
    write(v2, "Systems/點數.md", "type: system\nstatus: done", body="# 點\n")
    write(v2, "Systems/點數商城.md", "type: system\nstatus: done", body="# 商城\n")
    write(v2, "Verification/2026-02-01_e.md",
          "type: verification\nstatus: pass\nfeature: 點數商城兌換流程", body="# e\n")
    r = run(v2, "doctor", "--suggest")
    check("suggest: 前綴抑制 — 推薦點數商城", "推薦 Systems/點數商城.md" in r.stdout, r.stdout)
    check("suggest: 前綴抑制 — 不推薦子字串點數", "提到「點數」" not in r.stdout, r.stdout)
    # Bug-1 ASCII 詞界:feature 無 api 整詞時不推薦 api(避 pos_api 類假命中)
    v3 = mkvault()
    write(v3, "Systems/api.md", "type: system\nstatus: done", body="# api\n")
    write(v3, "Verification/2026-03-01_f.md",
          "type: verification\nstatus: pass\nfeature: pos_api_auth 流程修正", body="# f\n")
    r = run(v3, "doctor", "--suggest")
    check("suggest: ASCII 詞界 — api 不命中 pos_api_auth", "提到「api」" not in r.stdout, r.stdout)


def t_reversibility_lint():
    v = mkvault()
    write(v, "Systems/Mig.md",
          "type: system\nstatus: doing\nsummary: |-\n  KEY:★IRREVERSIBLE★ 跑 schema 遷移", body="# M\n")
    r = run(v, "lint", "Systems/Mig")
    check("lint: ★IRREVERSIBLE★ 缺回退 → rc1", r.returncode == 1 and "缺實質回退" in r.stdout, r.stdout)
    write(v, "Systems/Mig2.md",
          "type: system\nstatus: doing\n"
          "decisions:\n  - content: 用樂觀鎖\n    decided: 2026-06-19\n"
          "summary: |-\n  KEY:★IRREVERSIBLE★ 跑遷移 [rollback:decisions]", body="# M2\n")
    r = run(v, "lint", "Systems/Mig2")
    check("lint: [rollback:] 指到無實質 rollback → rc1", r.returncode == 1, r.stdout)
    write(v, "Systems/Mig3.md",
          "type: system\nstatus: doing\n"
          "decisions:\n  - content: 用樂觀鎖\n    decided: 2026-06-19\n    rollback: 跑 revert_v4.sql\n"
          "summary: |-\n  KEY:★IRREVERSIBLE★ 跑遷移 [rollback:decisions]", body="# M3\n")
    r = run(v, "lint", "Systems/Mig3")
    check("lint: irreversible 有實質回退 → rc0", r.returncode == 0, r.stdout)
    write(v, "Systems/Cp.md",
          "type: system\nstatus: doing\nsummary: |-\n  KEY:★CHECKPOINT★ 部署 lab2", body="# C\n")
    r = run(v, "lint", "Systems/Cp")
    check("lint: ★CHECKPOINT★ 缺回退 → warning rc0", r.returncode == 0 and "建議補回退" in r.stdout, r.stdout)
    write(v, "Issues/Bad.md",
          "type: issue\nstatus: open\nsummary: |-\n  KEY:★IRREVERSIBLE★ 標錯地方", body="# B\n")
    r = run(v, "lint", "Issues/Bad")
    check("lint: 可逆性標記在非 Systems → rc1", r.returncode == 1 and "只能在 Systems" in r.stdout, r.stdout)
    # ── [guard:decisions] 事前預防路徑(與 rollback 兩軌任一合規)──
    write(v, "Systems/Gd1.md",
          "type: system\nstatus: doing\n"
          "decisions:\n  - content: 補登 API\n    decided: 2026-06-22\n    guard: 冪等鍵 X-Idempotency-Key + Redis 60s 去重\n"
          "summary: |-\n  KEY:★IRREVERSIBLE★ 寄發票通知信 [guard:decisions]", body="# G1\n")
    r = run(v, "lint", "Systems/Gd1")
    check("lint: IRREVERSIBLE + 非空 guard → rc0", r.returncode == 0, r.stdout)
    write(v, "Systems/Gd2.md",
          "type: system\nstatus: doing\n"
          "decisions:\n  - content: 補登\n    decided: 2026-06-22\n"
          "summary: |-\n  KEY:★IRREVERSIBLE★ 寄信 [guard:decisions]", body="# G2\n")
    r = run(v, "lint", "Systems/Gd2")
    check("lint: IRREVERSIBLE + 空 guard → rc1", r.returncode == 1, r.stdout)
    write(v, "Systems/Gd5.md",
          "type: system\nstatus: doing\n"
          "decisions:\n  - content: 雙保險\n    decided: 2026-06-22\n    rollback: revert.sql\n    guard: 冪等鍵\n"
          "summary: |-\n  KEY:★IRREVERSIBLE★ 遷移 [rollback:decisions] [guard:decisions]", body="# G5\n")
    r = run(v, "lint", "Systems/Gd5")
    check("lint: rollback+guard 兩者皆有 → rc0", r.returncode == 0, r.stdout)
    write(v, "Systems/Gd6.md",
          "type: system\nstatus: doing\n"
          "decisions:\n  - content: 部署\n    decided: 2026-06-22\n    guard: 核可閘\n"
          "summary: |-\n  KEY:★CHECKPOINT★ 部署 lab [guard:decisions]", body="# G6\n")
    r = run(v, "lint", "Systems/Gd6")
    check("lint: CHECKPOINT + guard → guard 靜默忽略、無 rollback 仍 warning rc0",
          r.returncode == 0 and "建議補回退" in r.stdout, r.stdout)


def t_reversibility_doctor():
    v = mkvault()
    write(v, "Systems/Mig.md",
          "type: system\nstatus: doing\nsummary: |-\n  KEY:★IRREVERSIBLE★ 跑遷移", body="# M\n")
    r = run(v, "doctor", "--ci")
    check("doctor Check R: irreversible 缺回退 → rc1", r.returncode == 1 and "缺實質回退" in r.stdout, r.stdout)
    v2 = mkvault()
    write(v2, "Systems/Cp.md",
          "type: system\nstatus: doing\nsummary: |-\n  KEY:★CHECKPOINT★ 部署 lab2", body="# C\n")
    r2 = run(v2, "doctor", "--ci")
    check("doctor Check R: 只有 checkpoint 缺回退 → rc0(warn_soft 不計 issues)", r2.returncode == 0, r2.stdout)


def t_reversibility_guard_doctor():
    v = mkvault()
    # IRREVERSIBLE + 非空 guard → 不報 error(doctor --ci rc0)
    write(v, "Systems/Gd.md",
          "type: system\nstatus: doing\n"
          "decisions:\n  - content: 補登 API\n    decided: 2026-06-22\n    guard: 冪等鍵 + Redis 去重\n"
          "summary: |-\n  KEY:★IRREVERSIBLE★ 寄信 [guard:decisions]", body="# Gd\n")
    r = run(v, "doctor", "--ci")
    check("doctor: IRREVERSIBLE + 非空 guard → rc0", r.returncode == 0, r.stdout)
    # IRREVERSIBLE 兩者皆無 → error,提示含兩選項
    v2 = mkvault()
    write(v2, "Systems/Bad.md",
          "type: system\nstatus: doing\nsummary: |-\n  KEY:★IRREVERSIBLE★ 寄信沒守衛", body="# B\n")
    r = run(v2, "doctor")
    check("doctor: IRREVERSIBLE 兩軌皆無 → 提示 rollback 或 guard",
          "[guard:decisions]" in r.stdout and "[rollback:decisions]" in r.stdout, r.stdout)


def t_governance_log_write():
    import subprocess as sp
    root = Path(tempfile.mkdtemp(prefix="gctl-gov-"))
    vault = root / "docs" / "kg"
    for sub in ("Systems", "MOC"):
        (vault / sub).mkdir(parents=True)
    (vault / "MOC" / "i.md").write_bytes("---\ntype: moc\n---\n# i\n".encode("utf-8"))
    (vault / "Systems" / "Mig.md").write_bytes(
        "---\ntype: system\nstatus: doing\nsummary: |-\n  KEY:★IRREVERSIBLE★ 跑遷移\n---\n# M\n".encode("utf-8"))
    sp.run(["git", "init", "-q"], cwd=str(root))
    sp.run(["git", "add", "-A"], cwd=str(root))
    sp.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init"], cwd=str(root))
    try:
        run(vault, "doctor", "--ci")
        log = root / "docs" / ".governance-log.jsonl"
        check("gov-log: --ci 寫入 governance-log", log.exists() and "check-r" in log.read_text(encoding="utf-8"), "未寫")
        if log.exists():
            log.unlink()
        run(vault, "doctor")
        check("gov-log: 純 doctor 不寫", not log.exists(), "不該寫")
    finally:
        import shutil
        shutil.rmtree(root, ignore_errors=True)


def t_gov_query():
    root = Path(tempfile.mkdtemp(prefix="gctl-govq-"))
    vault = root / "docs" / "kg"
    (vault / "MOC").mkdir(parents=True)
    (vault / "MOC" / "i.md").write_bytes("---\ntype: moc\n---\n# i\n".encode("utf-8"))
    docs = root / "docs"
    (docs / ".bypass-log.jsonl").write_bytes(
        '{"ts":"2026-06-18T10:00:00","commit":"abc","subject":"skip graph"}\n'.encode("utf-8"))
    (docs / ".rot-queue.jsonl").write_bytes(
        '{"ts":"2026-06-18T11:00:00","commit":"abc12","verification":"docs/kg/Verification/Foo.md","reason":"schema 變"}\n'.encode("utf-8"))
    (docs / ".governance-log.jsonl").write_bytes(
        '{"ts":"2026-06-19T09:00:00","commit":"def","gate":"check-r","kind":"blocked","hard":true,"nodes":["OrderSvc"]}\n'.encode("utf-8"))
    try:
        r = run(vault, "gov")
        check("gov: 三來源合併", "check-r" in r.stdout and "skip graph" in r.stdout and "schema 變" in r.stdout, r.stdout)
        r = run(vault, "gov", "OrderSvc")
        check("gov <node>: 命中 governance-log 事件", "check-r" in r.stdout, r.stdout)
        r = run(vault, "gov", "Foo")
        check("gov <node>: stem 命中 rot-queue", "schema 變" in r.stdout, r.stdout)
    finally:
        import shutil
        shutil.rmtree(root, ignore_errors=True)


def t_marker_doc_sync():
    import pathlib
    repo = pathlib.Path(__file__).resolve().parent.parent
    skill = repo / "skills" / "lumos-project-notes" / "SKILL.md"
    disc = repo / "scripts" / "templates" / "graph-discipline.md"
    if not skill.exists() or not disc.exists():
        check("drift: skills/template 不在(vendored)→ 跳過", True)
        return
    st, dt = skill.read_text(encoding="utf-8"), disc.read_text(encoding="utf-8")
    for m in ("★CHECKPOINT★", "★IRREVERSIBLE★", "[rollback:", "[guard:"):
        check(f"drift: {m} 在 SKILL.md", m in st, "SKILL 缺")
        check(f"drift: {m} 在 graph-discipline", m in dt, "disc 缺")


def t_canary():
    import json as _j
    import shutil
    root = Path(tempfile.mkdtemp(prefix="gctl-can-"))
    vault = root / "docs" / "kg"
    (vault / "MOC").mkdir(parents=True)
    (vault / "MOC" / "i.md").write_bytes("---\ntype: moc\n---\n# i\n".encode("utf-8"))
    try:
        r = run(vault, "canary", "record", "missed", "--auditor", "sonnet")
        check("canary: record missed rc0", r.returncode == 0, r.stdout + r.stderr)
        log = root / "docs" / ".canary-log.jsonl"
        rec = _j.loads(log.read_text(encoding="utf-8").strip())
        check("canary: 寫入含 token + missed",
              rec.get("kind") == "missed" and rec.get("token", "").startswith("CANARY-"), str(rec))
        r = run(vault, "gov")
        check("canary: gov 顯示 canary/missed", "canary/missed" in r.stdout, r.stdout)
        # 兩筆不同 token → gov 各一列(不被 dedup 折成一列)
        run(vault, "canary", "record", "caught", "--token", "CANARY-A")
        run(vault, "canary", "record", "caught", "--token", "CANARY-B")
        r = run(vault, "gov")
        check("canary: 不同 token 不被 dedup", r.stdout.count("canary/caught") == 2, r.stdout)
        # 非法 kind → rc2(argparse choices)
        r = run(vault, "canary", "record", "bogus")
        check("canary: 非法 kind → rc2", r.returncode == 2, r.stdout + r.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_canary_loop_fields():
    import json as _j
    import shutil
    root = Path(tempfile.mkdtemp(prefix="gctl-clf-"))
    vault = root / "docs" / "kg"
    (vault / "MOC").mkdir(parents=True)
    (vault / "MOC" / "i.md").write_bytes("---\ntype: moc\n---\n# i\n".encode("utf-8"))
    try:
        r = run(vault, "canary", "record", "caught", "--loop", "L", "--severity", "major", "--token", "zz")
        check("canary --loop/--severity: rc0", r.returncode == 0, r.stdout + r.stderr)
        rec = _j.loads((root / "docs" / ".canary-log.jsonl").read_text(encoding="utf-8").strip())
        check("canary --loop/--severity: 寫入 loop+severity",
              rec.get("loop") == "L" and rec.get("severity") == "major", str(rec))
        r = run(vault, "gov")
        check("gov: canary detail 開頭含 loop=/sev=", "loop=L" in r.stdout and "sev=major" in r.stdout, r.stdout)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_loop_status():
    import json as _j
    import shutil
    root = Path(tempfile.mkdtemp(prefix="gctl-loop-"))
    vault = root / "docs" / "kg"
    (vault / "MOC").mkdir(parents=True)
    (vault / "MOC" / "i.md").write_bytes("---\ntype: moc\n---\n# i\n".encode("utf-8"))
    log = root / "docs" / ".canary-log.jsonl"
    n = [0]

    def rec(loop, kind, sev=None):
        n[0] += 1
        d = {"ts": "2026-06-19T10:00:00", "kind": kind, "auditor": "sonnet",
             "token": f"t{n[0]}", "note": ""}
        if loop:
            d["loop"] = loop
        if sev:
            d["severity"] = sev
        with open(log, "a", encoding="utf-8") as f:
            f.write(_j.dumps(d) + "\n")

    try:
        r = run(vault, "loop", "status", "L")
        check("loop status: 無記錄 → exit 1", r.returncode == 1, r.stdout + r.stderr)
        rec("L", "caught", "clean"); rec("L", "caught", "minor")
        r = run(vault, "loop", "status", "L")
        check("loop status: 連2輪 caught+clean/minor → CONVERGED exit0",
              r.returncode == 0 and "CONVERGED" in r.stdout, r.stdout)
        rec("L", "caught", "major")
        r = run(vault, "loop", "status", "L")
        check("loop status: 最後一輪 major → 未收斂 exit1", r.returncode == 1, r.stdout)
        rec("L", "caught", "clean"); rec("L", "caught", "clean")
        r = run(vault, "loop", "status", "L")
        check("loop status: tail-K 滑動,髒輪滑出 → CONVERGED", r.returncode == 0, r.stdout)
        rec("M", "caught", "clean"); rec("M", "missed"); rec("M", "caught", "clean")
        r = run(vault, "loop", "status", "M")
        check("loop status: missed 在 tail-2 → 未收斂", r.returncode == 1, r.stdout)
        rec("N", "caught"); rec("N", "caught")
        r = run(vault, "loop", "status", "N")
        check("loop status: 缺 severity → 未收斂", r.returncode == 1, r.stdout)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_check_k():
    # Check K: ★COMBO★ 鐵則只綁 1 個 [test:] → 軟提醒補組合(warn_soft,不擋)
    v = mkvault()
    write(v, "Systems/Thin.md",
          "type: system\nstatus: done\nsummary: |-\n  KEY:★INVARIANT★ 不可超賣 ★COMBO★ [test:OverbookHappy]",
          body="# Thin\n")
    r = run(v, "doctor")
    check("Check K: ★COMBO★ 綁 1 標記 → 提醒補組合", "happy-path" in r.stdout, r.stdout)

    # 綁 2 個 [test:] 標記 → 不提醒
    v2 = mkvault()
    write(v2, "Systems/Two.md",
          "type: system\nstatus: done\nsummary: |-\n  KEY:★INVARIANT★ 不可超賣 ★COMBO★ [test:Happy] [test:Combo]",
          body="# Two\n")
    check("Check K: ★COMBO★ 綁 2 標記 → 不提醒", "happy-path" not in run(v2, "doctor").stdout)

    # 無 ★COMBO★ → 不提醒
    v3 = mkvault()
    write(v3, "Systems/NoCombo.md",
          "type: system\nstatus: done\nsummary: |-\n  KEY:★INVARIANT★ 不可超賣 [test:Happy]",
          body="# NoCombo\n")
    check("Check K: 無 ★COMBO★ → 不提醒", "happy-path" not in run(v3, "doctor").stdout)

    # F1: [test:a,b] 單逗號標記算 1 個 → 仍提醒(免繞過)
    v4 = mkvault()
    write(v4, "Systems/Comma.md",
          "type: system\nstatus: done\nsummary: |-\n  KEY:★INVARIANT★ 不可超賣 ★COMBO★ [test:HappyA,HappyB]",
          body="# Comma\n")
    check("Check K F1: [test:a,b] 算 1 標記 → 仍提醒(免逗號繞過)", "happy-path" in run(v4, "doctor").stdout)


def _mk_git_vault():
    """temp git repo + docs/kg vault(子目錄)+ 一個初始 commit。回 (root, vault)。"""
    import subprocess
    root = Path(tempfile.mkdtemp(prefix="gctl-h-"))
    for cmd in (["git", "init", "-q"], ["git", "config", "user.email", "t@t.t"],
                ["git", "config", "user.name", "t"]):
        subprocess.run(cmd, cwd=root, capture_output=True)
    vault = root / "docs" / "kg"
    (vault / "MOC").mkdir(parents=True)
    (vault / "MOC" / "i.md").write_bytes("---\ntype: moc\n---\n# i\n".encode("utf-8"))
    subprocess.run(["git", "add", "-A"], cwd=root, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=root, capture_output=True)
    return root, vault


def t_check_h_irreversible_hint():
    import subprocess
    HEAD = "疑似碰外部不可逆"  # warn_soft head 的特徵詞

    # 1. smoke:staged 含 prod requests.post → 提示
    root, vault = _mk_git_vault()
    (root / "charge.py").write_bytes('requests.post("https://prod.api.com/charge")\n'.encode("utf-8"))
    subprocess.run(["git", "add", "charge.py"], cwd=root, capture_output=True)
    r = run(vault, "doctor", "--ci")
    check("Check H smoke: staged prod requests.post → 提示", HEAD in r.stdout, r.stdout)

    # 2. filter-test-file:test_ 檔含 sendmail → 不報
    root, vault = _mk_git_vault()
    (root / "test_email.py").write_bytes('sendmail("to@prod")\n'.encode("utf-8"))
    subprocess.run(["git", "add", "test_email.py"], cwd=root, capture_output=True)
    r = run(vault, "doctor", "--ci")
    check("Check H filter test-file: test_ 檔不報", HEAD not in r.stdout, r.stdout)

    # 3. filter-comment:純注解行 → 不報
    root, vault = _mk_git_vault()
    (root / "x.py").write_bytes('# sendgrid.send(...)\n'.encode("utf-8"))
    subprocess.run(["git", "add", "x.py"], cwd=root, capture_output=True)
    r = run(vault, "doctor", "--ci")
    check("Check H filter comment: 純注解不報", HEAD not in r.stdout, r.stdout)

    # 4. config-file:.yaml 含 prod.stripe → 報(SKIP_EXT 不排 .yaml)
    root, vault = _mk_git_vault()
    (root / "config.yaml").write_bytes('endpoint: https://prod.stripe.com\n'.encode("utf-8"))
    subprocess.run(["git", "add", "config.yaml"], cwd=root, capture_output=True)
    r = run(vault, "doctor", "--ci")
    check("Check H config: .yaml prod → 報", HEAD in r.stdout, r.stdout)

    # 5. no-ci:--strict(無 --ci)→ 印互動略過語、不掃
    root, vault = _mk_git_vault()
    (root / "charge.py").write_bytes('requests.post("https://prod.api.com")\n'.encode("utf-8"))
    subprocess.run(["git", "add", "charge.py"], cwd=root, capture_output=True)
    r = run(vault, "doctor", "--strict")
    check("Check H no-ci: 互動模式略過", "互動模式略過" in r.stdout, r.stdout)

    # 6. non-git:普通 vault(非 git repo)→ 靜默無疑似、不崩
    v = mkvault()
    r = run(v, "doctor", "--ci")
    check("Check H non-git: 不崩 + 無疑似", HEAD not in r.stdout, r.stdout)

    # 7. initial-commit:只有初始 commit、無新 staged → HEAD~1 rc≠0 → 無疑似
    root, vault = _mk_git_vault()
    r = run(vault, "doctor", "--ci")
    check("Check H initial-commit: 無 parent diff → 無疑似", HEAD not in r.stdout, r.stdout)


def t_merge_settings_dedupe():
    import subprocess, json, os
    tmp = Path(tempfile.mkdtemp(prefix="gctl-settings-"))
    fake_home = tmp
    settings = fake_home / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True)
    # 既有:舊裸路徑格式
    settings.write_text(json.dumps({"hooks": {"Stop": [
        {"hooks": [{"type": "command", "command": "${HOME}/.claude/hooks/check-graph-sync.py", "timeout": 10}]}
    ]}}), encoding="utf-8")
    env = dict(os.environ, HOME=str(fake_home), USERPROFILE=str(fake_home))
    merge = str(Path(GRAPHCTL).resolve().parent / "merge-claude-settings.py")
    subprocess.run([sys.executable, merge], env=env, capture_output=True, text=True)
    data = json.loads(settings.read_text(encoding="utf-8"))
    stop = data["hooks"]["Stop"]
    cmds = [h["command"] for e in stop for h in e["hooks"] if "check-graph-sync" in h["command"]]
    check("merge: check-graph-sync 同 hook 只一筆(去重遷移)", len(cmds) == 1, f"got {len(cmds)}: {cmds}")


def t_hook_cmd_home_resolved():
    # W3:hook command 路徑前綴。${HOME} 只有 POSIX shell 展開;native Windows(Claude Code
    # 經 cmd/PowerShell 跑 hook)不展開 → L1/L3 靜默不觸發。Windows 須用解析後的絕對 home。
    import importlib.util
    merge = str(Path(GRAPHCTL).resolve().parent / "merge-claude-settings.py")
    spec = importlib.util.spec_from_file_location("merge_mod_t", merge)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)  # 有 __main__ guard,import 不跑 main
    if sys.platform == "win32":
        # Claude Code 在 Windows 用 Git Bash 跑 hook → 反斜線會被吃掉。python 路徑(shutil.which
        # 在真機回 C:\...\python.EXE)必須正斜線化。monkeypatch _PY 模擬真機(測試 env stale PATH
        # 下 _PY 會退化成 "python3" 無反斜線、測不到轉換)。
        m._PY = "C:\\fake\\dir\\python.EXE"
        cmd = m._hook_cmd("check-graph-sync.py")
        check("hook cmd: Windows 無 ${HOME}、無反斜線(Git Bash 跑才不吃)、絕對路徑",
              "${HOME}" not in cmd and "\\" not in cmd
              and "/.claude/hooks/check-graph-sync.py" in cmd, cmd)
    else:
        cmd = m._hook_cmd("check-graph-sync.py")
        check("hook cmd: Unix 保留 ${HOME}(可攜)", "${HOME}" in cmd, cmd)


def t_link_or_copy_idempotent():
    # W4:_link_or_copy 重跑須冪等(get.ps1/install 重跑),且絕不刪來源。
    # Windows junction 不被 is_symlink() 認出 → 舊碼 rmtree 會跟進刪 target;且第二次 mklink
    # 報「已存在」→ fallback copytree 炸。修後第二次須乾淨重連、來源完好。
    from importlib.machinery import SourceFileLoader
    import importlib.util
    loader = SourceFileLoader("lumos_mod_lc", GRAPHCTL)
    spec = importlib.util.spec_from_loader("lumos_mod_lc", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)  # 有 __main__ guard,import 不跑 main
    base = Path(tempfile.mkdtemp(prefix="gctl-lc-"))
    src = base / "src"; src.mkdir()
    (src / "f.txt").write_bytes(b"keep-me\n")
    dst = base / "dst"
    m._link_or_copy(src, dst)            # 第一次:建連結/junction
    m._link_or_copy(src, dst)            # 第二次:不可炸(冪等)
    check("link_or_copy 冪等(第二次重跑不炸)", True, "")
    check("來源未被刪(f.txt 還在)", (src / "f.txt").exists(), "rmtree 跟進 junction 刪了來源!")
    check("dst 連到 src 內容(f.txt 可達)", (dst / "f.txt").exists(), "")


def t_deinit_vendored_toolkit_constant():
    import importlib.util
    from importlib.machinery import SourceFileLoader
    spec = importlib.util.spec_from_file_location(
        "m", GRAPHCTL, loader=SourceFileLoader("m", GRAPHCTL))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)  # __main__ guard → import 不跑 main
    expected = ("scripts/lumos", "scripts/test_lumos.py",
                "scripts/merge-claude-settings.py", "scripts/graph-rename.sh",
                "scripts/fetch-notesmd.sh")
    check("deinit: _VENDORED_TOOLKIT 5 檔且帶 scripts/ 前綴",
          tuple(m._VENDORED_TOOLKIT) == expected, f"got {getattr(m,'_VENDORED_TOOLKIT',None)!r}")


def _load_lumos():
    import importlib.util
    from importlib.machinery import SourceFileLoader
    spec = importlib.util.spec_from_file_location(
        "m", GRAPHCTL, loader=SourceFileLoader("m", GRAPHCTL))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def t_deinit_unbar_gate():
    import subprocess
    from pathlib import Path
    m = _load_lumos()
    root = Path(tempfile.mkdtemp(prefix="gctl-deinit-unbar-"))
    subprocess.run(["git", "-C", str(root), "init"], capture_output=True, text=True)
    subprocess.run(["git", "-C", str(root), "config", "core.hooksPath", "scripts/hooks"],
                   capture_output=True, text=True)
    rc1 = m._deinit_unbar_gate(root)
    hp = subprocess.run(["git", "-C", str(root), "config", "core.hooksPath"],
                        capture_output=True, text=True)
    check("deinit unbar: core.hooksPath 已 unset", hp.stdout.strip() == "", f"got {hp.stdout!r}")
    check("deinit unbar: rc 0 視為成功", rc1 == 0, f"rc={rc1}")
    rc2 = m._deinit_unbar_gate(root)   # 再 unset 一次 → key 已不存在
    check("deinit unbar: 重複 unset rc5 不崩潰", rc2 in (0, 5), f"rc={rc2}")


def t_deinit_strip_claude():
    from pathlib import Path
    m = _load_lumos()
    START = ("<!-- LUMOS:GRAPH-DISCIPLINE:START — 自動注入/更新,勿手改本區塊;"
             "改範本 scripts/templates/graph-discipline.md -->")
    END = "<!-- LUMOS:GRAPH-DISCIPLINE:END -->"

    # case A: 有自有段落 + 注入區塊 → 剝區塊、留自有段落、留檔
    root = Path(tempfile.mkdtemp(prefix="gctl-deinit-cm-a-"))
    (root / "CLAUDE.md").write_bytes(
        ("# CLAUDE.md\n\n我的專案規則。\n\n" + START + "\n圖譜紀律內文\n" + END + "\n").encode("utf-8"))
    stripped = m._deinit_strip_claude(root)
    txt = (root / "CLAUDE.md").read_text(encoding="utf-8")
    check("deinit claude A: 回 True", stripped is True, f"got {stripped}")
    check("deinit claude A: 自有段落保留", "我的專案規則。" in txt, txt)
    check("deinit claude A: 區塊已消失", "GRAPH-DISCIPLINE" not in txt, txt)
    check("deinit claude A: 檔仍在", (root / "CLAUDE.md").exists(), "")

    # case B: 無 START 標記 → no-op、回 False、內容不變
    root = Path(tempfile.mkdtemp(prefix="gctl-deinit-cm-b-"))
    (root / "CLAUDE.md").write_bytes("# CLAUDE.md\n\n只有我的內容\n".encode("utf-8"))
    before = (root / "CLAUDE.md").read_text(encoding="utf-8")
    res = m._deinit_strip_claude(root)
    check("deinit claude B: no-op 回 False", res is False, f"got {res}")
    check("deinit claude B: 內容不變", (root / "CLAUDE.md").read_text(encoding="utf-8") == before, "")

    # case C: CLAUDE.md 不存在 → no-op、回 False、不報錯
    root = Path(tempfile.mkdtemp(prefix="gctl-deinit-cm-c-"))
    res = m._deinit_strip_claude(root)
    check("deinit claude C: 無檔 no-op 回 False", res is False, f"got {res}")
    check("deinit claude C: 仍無 CLAUDE.md", not (root / "CLAUDE.md").exists(), "")

    # case D: END 在 START 之前(corrupt)→ no-op、回 False、內容不變
    root = Path(tempfile.mkdtemp(prefix="gctl-deinit-cm-d-"))
    (root / "CLAUDE.md").write_bytes(("# CLAUDE.md\n" + END + "\n中間\n" + START + "\n").encode("utf-8"))
    before = (root / "CLAUDE.md").read_text(encoding="utf-8")
    res = m._deinit_strip_claude(root)
    check("deinit claude D: END 在 START 前 no-op 回 False", res is False, f"got {res}")
    check("deinit claude D: 內容不變", (root / "CLAUDE.md").read_text(encoding="utf-8") == before, "")


def t_deinit_remove_vendored():
    from pathlib import Path
    m = _load_lumos()
    root = Path(tempfile.mkdtemp(prefix="gctl-deinit-rm-"))
    sc = root / "scripts"
    (sc / "hooks").mkdir(parents=True)
    (sc / "templates").mkdir(parents=True)
    (sc / "hooks" / "pre-commit").write_text("#!/bin/sh\n")
    (sc / "templates" / "graph-discipline.md").write_text("tpl\n")
    for rel in ("scripts/lumos", "scripts/test_lumos.py", "scripts/merge-claude-settings.py",
                "scripts/graph-rename.sh", "scripts/fetch-notesmd.sh"):
        (root / rel).write_text("x\n")
    (sc / "my_own_helper.py").write_text("mine\n")   # 使用者自有檔

    removed = m._deinit_remove_vendored(root)

    check("deinit rm: scripts/lumos 已移", not (sc / "lumos").exists(), "")
    check("deinit rm: scripts/hooks/ 整夾移除", not (sc / "hooks").exists(), "")
    check("deinit rm: scripts/templates/ 整夾移除", not (sc / "templates").exists(), "")
    check("deinit rm: 使用者自有檔保留", (sc / "my_own_helper.py").exists(), "")
    check("deinit rm: scripts/ 非空故保留", sc.is_dir(), "")
    check("deinit rm: 回傳列表含 scripts/lumos", "scripts/lumos" in removed, f"{removed}")

    # 第二個 repo:scripts/ 只剩 Lumos-owned → 清空後應 rmdir
    root2 = Path(tempfile.mkdtemp(prefix="gctl-deinit-rm2-"))
    (root2 / "scripts").mkdir()
    (root2 / "scripts" / "lumos").write_text("x\n")
    m._deinit_remove_vendored(root2)
    check("deinit rm: scripts/ 清空後 rmdir", not (root2 / "scripts").exists(), "")


def t_deinit_detect_installed():
    import subprocess
    from pathlib import Path
    m = _load_lumos()

    # 無安裝痕跡 → False
    bare = Path(tempfile.mkdtemp(prefix="gctl-deinit-det0-"))
    subprocess.run(["git", "-C", str(bare), "init"], capture_output=True, text=True)
    check("deinit detect: 空 repo False", m._deinit_detect_installed(bare) is False, "")

    # core.hooksPath 有值 → True
    h = Path(tempfile.mkdtemp(prefix="gctl-deinit-det1-"))
    subprocess.run(["git", "-C", str(h), "init"], capture_output=True, text=True)
    subprocess.run(["git", "-C", str(h), "config", "core.hooksPath", "scripts/hooks"],
                   capture_output=True, text=True)
    check("deinit detect: hooksPath 有值 True", m._deinit_detect_installed(h) is True, "")

    # scripts/hooks/ 存在 → True
    s = Path(tempfile.mkdtemp(prefix="gctl-deinit-det2-"))
    subprocess.run(["git", "-C", str(s), "init"], capture_output=True, text=True)
    (s / "scripts" / "hooks").mkdir(parents=True)
    check("deinit detect: scripts/hooks 存在 True", m._deinit_detect_installed(s) is True, "")

    # _claude_block_present
    c = Path(tempfile.mkdtemp(prefix="gctl-deinit-det3-"))
    (c / "CLAUDE.md").write_text("# CLAUDE.md\n<!-- LUMOS:GRAPH-DISCIPLINE:START x -->\n", encoding="utf-8")
    check("deinit detect: claude 區塊在 True", m._claude_block_present(c) is True, "")
    check("deinit detect: 無 claude False",
          m._claude_block_present(Path(tempfile.mkdtemp(prefix="gctl-deinit-det4-"))) is False, "")


def _mk_installed_project(prefix="gctl-deinit-proj-", with_vault=True, slug="demo"):
    """造一個已裝 Lumos 專案層的 hermetic repo(不跑 init/update,純手工)。回傳 root。"""
    import subprocess
    from pathlib import Path
    root = Path(tempfile.mkdtemp(prefix=prefix))
    subprocess.run(["git", "-C", str(root), "init"], capture_output=True, text=True)
    subprocess.run(["git", "-C", str(root), "config", "core.hooksPath", "scripts/hooks"],
                   capture_output=True, text=True)
    sc = root / "scripts"
    (sc / "hooks").mkdir(parents=True)
    (sc / "templates").mkdir(parents=True)
    (sc / "hooks" / "pre-commit").write_text("#!/bin/sh\nexit 0\n")
    (sc / "templates" / "graph-discipline.md").write_text("tpl\n")
    for rel in ("scripts/lumos", "scripts/test_lumos.py", "scripts/merge-claude-settings.py",
                "scripts/graph-rename.sh", "scripts/fetch-notesmd.sh"):
        (root / rel).write_text("x\n")
    START = ("<!-- LUMOS:GRAPH-DISCIPLINE:START — 自動注入/更新,勿手改本區塊;"
             "改範本 scripts/templates/graph-discipline.md -->")
    END = "<!-- LUMOS:GRAPH-DISCIPLINE:END -->"
    (root / "CLAUDE.md").write_bytes(
        ("# CLAUDE.md\n\n我的規則\n\n" + START + "\n紀律\n" + END + "\n").encode("utf-8"))
    if with_vault:
        kg = root / "docs" / f"{slug}-knowledge"
        (kg / "MOC").mkdir(parents=True)
        (kg / "Systems").mkdir(parents=True)
        (kg / "MOC" / "index.md").write_text("# idx\n")
        (kg / "Systems" / "S.md").write_text("# S\n")
    return root

def _deinit_run(root, *args, stdin_data=None):
    """從 root 跑 lumos deinit(cwd=root,git toplevel 即 root)。"""
    import subprocess, os
    fake = tempfile.mkdtemp(prefix="gctl-deinit-home-")
    # stdin_data=None → 顯式 DEVNULL,確保非 tty(否則繼承環境 stdin;Windows/某些終端
    # isatty() 不可靠,會誤判互動 → 走 input() 撞 EOF)。有資料才用 input= 餵。
    kw = {"input": stdin_data} if stdin_data is not None else {"stdin": subprocess.DEVNULL}
    return subprocess.run([sys.executable, GRAPHCTL, "deinit", *args],
                          cwd=str(root), **kw,
                          env=dict(os.environ, HOME=fake, USERPROFILE=fake),
                          capture_output=True, text=True)

def t_deinit_cmd_basic():
    from pathlib import Path
    # 整體(graph 在 Task 7 才刪;此處 --keep-graph 行為驗非破壞動作)
    root = _mk_installed_project()
    r = _deinit_run(root, "--keep-graph", "--yes")
    check("deinit cmd: rc 0", r.returncode == 0, f"{r.returncode} {r.stderr}")
    import subprocess
    hp = subprocess.run(["git", "-C", str(root), "config", "core.hooksPath"],
                        capture_output=True, text=True)
    check("deinit cmd: core.hooksPath 已 unset", hp.stdout.strip() == "", f"{hp.stdout!r}")
    check("deinit cmd: scripts/hooks/ 已移", not (root / "scripts" / "hooks").exists(), "")
    check("deinit cmd: scripts/lumos 已移", not (root / "scripts" / "lumos").exists(), "")
    cm = (root / "CLAUDE.md").read_text(encoding="utf-8")
    check("deinit cmd: claude 自有段落留", "我的規則" in cm, cm)
    check("deinit cmd: claude 區塊剝", "GRAPH-DISCIPLINE" not in cm, cm)

    # case 5 白名單:使用者自有檔保留
    root = _mk_installed_project(prefix="gctl-deinit-white-")
    (root / "scripts" / "mine.py").write_text("mine\n")
    _deinit_run(root, "--keep-graph", "--yes")
    check("deinit cmd: 使用者自有 scripts/mine.py 保留", (root / "scripts" / "mine.py").exists(), "")

    # case 7 來源自我保護:--source 指到 root 本身 → 拒絕 + rc2 + 無副作用
    root = _mk_installed_project(prefix="gctl-deinit-src-")
    r = _deinit_run(root, "--keep-graph", "--yes", "--source", str(root))
    check("deinit cmd: 來源自我保護 rc2", r.returncode == 2, f"{r.returncode} {r.stdout} {r.stderr}")
    check("deinit cmd: 自我保護下 scripts/lumos 未動", (root / "scripts" / "lumos").exists(), "")

    # case 4 冪等:乾淨 repo → rc0 + 印未安裝
    bare = Path(tempfile.mkdtemp(prefix="gctl-deinit-bare-"))
    subprocess.run(["git", "-C", str(bare), "init"], capture_output=True, text=True)
    r = _deinit_run(bare, "--yes")
    check("deinit cmd: 冪等 rc0", r.returncode == 0, f"{r.returncode} {r.stderr}")
    check("deinit cmd: 冪等印未安裝", "未安裝" in r.stdout, r.stdout)


def t_deinit_graph():
    import subprocess, os
    from pathlib import Path

    # case 1 完整 deinit:default(--yes)→ vault 不存在 + 其餘皆拆
    root = _mk_installed_project(prefix="gctl-deinit-g1-")
    r = _deinit_run(root, "--yes")
    check("deinit graph1: rc0", r.returncode == 0, f"{r.returncode} {r.stderr}")
    check("deinit graph1: vault 已刪", not (root / "docs" / "demo-knowledge").exists(), "")
    check("deinit graph1: scripts/lumos 已移", not (root / "scripts" / "lumos").exists(), "")

    # case 2 --keep-graph:vault 仍在
    root = _mk_installed_project(prefix="gctl-deinit-g2-")
    _deinit_run(root, "--keep-graph", "--yes")
    check("deinit graph2: --keep-graph 保留 vault", (root / "docs" / "demo-knowledge").is_dir(), "")

    # case 8 --dry-run:vault + config + 檔案全不動
    root = _mk_installed_project(prefix="gctl-deinit-g8-")
    r = _deinit_run(root, "--dry-run")
    check("deinit graph8: dry-run rc0", r.returncode == 0, f"{r.returncode}")
    check("deinit graph8: dry-run vault 仍在", (root / "docs" / "demo-knowledge").is_dir(), "")
    check("deinit graph8: dry-run scripts/lumos 仍在", (root / "scripts" / "lumos").exists(), "")
    hp = subprocess.run(["git", "-C", str(root), "config", "core.hooksPath"],
                        capture_output=True, text=True)
    check("deinit graph8: dry-run hooksPath 未動", hp.stdout.strip() == "scripts/hooks", f"{hp.stdout!r}")

    # case 9 非互動防呆:預設(無 --yes)+ 非 tty → 拒絕刪 + rc2 + vault 仍在
    root = _mk_installed_project(prefix="gctl-deinit-g9-")
    r = _deinit_run(root)   # subprocess capture → stdin 非 tty
    check("deinit graph9: 非互動無 --yes rc2", r.returncode == 2, f"{r.returncode} {r.stdout} {r.stderr}")
    check("deinit graph9: vault 未刪", (root / "docs" / "demo-knowledge").is_dir(), "")

    # case 10 vault==root 鐵閘:standalone vault repo(非 _lumos_src)→ 絕不 rmtree
    root = Path(tempfile.mkdtemp(prefix="gctl-deinit-g10-"))
    subprocess.run(["git", "-C", str(root), "init"], capture_output=True, text=True)
    subprocess.run(["git", "-C", str(root), "config", "core.hooksPath", "scripts/hooks"],
                   capture_output=True, text=True)
    (root / "MOC").mkdir(); (root / "Systems").mkdir()
    (root / "MOC" / "index.md").write_text("# idx\n")
    (root / "important_note.md").write_text("不可刪\n")
    START = ("<!-- LUMOS:GRAPH-DISCIPLINE:START — 自動注入/更新,勿手改本區塊;"
             "改範本 scripts/templates/graph-discipline.md -->")
    END = "<!-- LUMOS:GRAPH-DISCIPLINE:END -->"
    (root / "CLAUDE.md").write_bytes(("# CLAUDE.md\n\n" + START + "\nx\n" + END + "\n").encode("utf-8"))
    r = _deinit_run(root, "--yes")
    check("deinit graph10: 鐵閘 rc0", r.returncode == 0, f"{r.returncode} {r.stderr}")
    check("deinit graph10: 印 standalone vault 警示", "standalone vault" in r.stderr, r.stderr)
    check("deinit graph10: repo 根仍在(絕無 rmtree)", (root / "important_note.md").exists(), "")
    check("deinit graph10: MOC/ 圖譜仍在", (root / "MOC" / "index.md").exists(), "")
    hp = subprocess.run(["git", "-C", str(root), "config", "core.hooksPath"],
                        capture_output=True, text=True)
    check("deinit graph10: 其餘動作仍執行(hooksPath unset)", hp.stdout.strip() == "", f"{hp.stdout!r}")
    cm = (root / "CLAUDE.md").read_text(encoding="utf-8")
    check("deinit graph10: 其餘動作仍執行(claude 區塊剝)", "GRAPH-DISCIPLINE" not in cm, cm)

    # case 3 拆閘有效:deinit 後 commit「改 code 不動圖譜」不被擋
    root = _mk_installed_project(prefix="gctl-deinit-g3-")
    _deinit_run(root, "--keep-graph", "--yes")
    hp = subprocess.run(["git", "-C", str(root), "config", "core.hooksPath"],
                        capture_output=True, text=True)
    check("deinit graph3: core.hooksPath 空", hp.stdout.strip() == "", f"{hp.stdout!r}")
    check("deinit graph3: scripts/hooks/ 不存在", not (root / "scripts" / "hooks").exists(), "")
    (root / "code.py").write_text("print(1)\n")
    subprocess.run(["git", "-C", str(root), "add", "-A"], capture_output=True, text=True)
    cr = subprocess.run(["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t",
                         "commit", "-m", "change code only"], capture_output=True, text=True)
    check("deinit graph3: commit 不被擋(rc0)", cr.returncode == 0, f"{cr.returncode} {cr.stdout} {cr.stderr}")


def t_context_valid_under_warning():
    import datetime
    v = mkvault()
    # >90 天的 Verification 節點(date 2020 → 紅標)
    write(v, "Verification/old.md",
          'type: verification\nstatus: pass\ndate: 2020-01-01\nvalid_under:\n  - "DB schema v1 未變"')
    r = run(v, "context", "Verification/old")
    check("context: valid_under 警示 header", "⚠ 使用前驗證(valid_under" in r.stdout, r.stdout)
    check("context: >90 天紅標", "⚠ 節點已" in r.stdout, r.stdout)
    check("context: 條件內容印出", "DB schema v1 未變" in r.stdout, r.stdout)

    # 新節點(date=今天 → 有警示但無紅標)
    today = datetime.date.today().isoformat()
    write(v, "Verification/fresh.md",
          f'type: verification\nstatus: pass\ndate: {today}\nvalid_under:\n  - "並發 <= 1000 RPS"')
    r2 = run(v, "context", "Verification/fresh")
    check("context: 新節點有警示", "⚠ 使用前驗證(valid_under" in r2.stdout, r2.stdout)
    check("context: 新節點無紅標", "⚠ 節點已" not in r2.stdout, r2.stdout)

    # 無 valid_under → 不印警示
    write(v, "Systems/plain.md", 'type: system\nstatus: done\nupdated: 2020-01-01')
    r3 = run(v, "context", "Systems/plain")
    check("context: 無 valid_under 不印警示", "⚠ 使用前驗證(valid_under" not in r3.stdout, r3.stdout)

    # 空 valid_under(empty list)→ 不印 header
    write(v, "Verification/empty.md",
          'type: verification\nstatus: pass\ndate: 2020-01-01\nvalid_under: []')
    r4 = run(v, "context", "Verification/empty")
    check("context: 空 valid_under 不印 header", "⚠ 使用前驗證(valid_under" not in r4.stdout, r4.stdout)


def t_doctor_check_v():
    import datetime
    v = mkvault()
    write(v, "Verification/a.md",
          'type: verification\nstatus: pass\ndate: 2020-01-01\nvalid_under:\n  - "c1"')
    write(v, "Verification/b.md",
          'type: verification\nstatus: pass\ndate: 2020-02-02\nvalid_under:\n  - "c2"')
    today = datetime.date.today().isoformat()
    write(v, "Verification/c.md",
          f'type: verification\nstatus: pass\ndate: {today}\nvalid_under:\n  - "c3"')
    r = run(v, "doctor")
    check("doctor Check V: 段標題出現", "[V]" in r.stdout, r.stdout)
    check("doctor Check V: 2/3 (67%)", "2/3 (67%)" in r.stdout, r.stdout)

    # 全新節點 → 0% / ok 行
    v2 = mkvault()
    write(v2, "Verification/fresh.md",
          f'type: verification\nstatus: pass\ndate: {today}\nvalid_under:\n  - "c1"')
    r2 = run(v2, "doctor")
    check("doctor Check V: 全新 → 0%/ok", ("0/1 (0%)" in r2.stdout) or ("≤90" in r2.stdout), r2.stdout)


def t_doctor_check_p_precision():
    root, vault = _mk_docs_vault(prefix="gctl-checkp-v2-")
    (root / "scripts").mkdir()
    (root / "scripts" / "real.py").write_text("x\n")
    (root / "governance").mkdir()  # 讓 glob token 的頂層目錄錨定不先擋,確保是 glob 過濾起作用
    # 案例 A:glob/模板 token → 不報
    write(vault, "Systems/a.md", "type: system\nstatus: done",
          "# A\n見 `governance/pending/*.md` 與 `docs/<slug>-knowledge/` 慣例。\n")
    # 案例 B:符號/中文錨且檔存在 → 不報
    write(vault, "Systems/b.md", "type: system\nstatus: done",
          "# B\n見 `scripts/real.py:t_some_test` 與 `scripts/real.py:行號`。\n")
    # 案例 C:真死指針帶數字行號 → 報且顯示 :10
    write(vault, "Systems/c.md", "type: system\nstatus: done",
          "# C\n見 `scripts/ghost.py:10` 實作。\n")

    r = run(vault, "doctor")
    check("Check P v2: glob/模板不報", "governance/pending/*.md" not in r.stdout and "<slug>" not in r.stdout, r.stdout)
    check("Check P v2: 符號/中文錨且檔存在不報", "scripts/real.py" not in r.stdout, r.stdout)
    check("Check P v2: 真死指針報出", "scripts/ghost.py" in r.stdout, r.stdout)
    check("Check P v2: 數字行號顯示 :10", "Systems/c.md:10" in r.stdout, r.stdout)
    check("Check P v2: rc 不變", r.returncode == 0, f"rc={r.returncode}")


def _mk_docs_vault(prefix="gctl-checkp-"):
    """建 temp_root/docs/<slug>-knowledge vault(讓 Check C 的 repo_root 推導命中 docs/ 母目錄)。
    回傳 (root, vault)。"""
    root = Path(tempfile.mkdtemp(prefix=prefix))
    vault = root / "docs" / "demo-knowledge"
    for sub in ("Systems", "Verification", "Projects", "MOC"):
        (vault / sub).mkdir(parents=True)
    (vault / "MOC" / "idx.md").write_bytes("---\ntype: moc\n---\n# idx\n".encode("utf-8"))
    return root, vault


def t_doctor_check_p():
    # 案例 1+2+3+4+5:同一 vault 多節點
    root, vault = _mk_docs_vault()
    (root / "scripts").mkdir()                       # rule 3 錨定靠 scripts/ 存在
    (root / "scripts" / "real.py").write_text("x\n") # 案例 2 的真實檔
    # 案例 1:失效認領(scripts/ghost.py 不存在)
    write(vault, "Systems/a.md", "type: system\nstatus: done",
          "# A\n見 `scripts/ghost.py` 實作。\n")
    # 案例 2:存在路徑帶行號 → 不報
    write(vault, "Systems/b.md", "type: system\nstatus: done",
          "# B\n見 `scripts/real.py:10` 一帶。\n")
    # 案例 3:散文/非路徑 → 不報
    write(vault, "Systems/c.md", "type: system\nstatus: done",
          "# C\n反引號 `and/or`、散文 maker/checker、反引號 `cmd_context`(無斜線)。\n")
    # 案例 4:fenced block 內路徑 → 不報
    write(vault, "Systems/d.md", "type: system\nstatus: done",
          "# D\n```\n`scripts/ghost.py`\n```\n")
    # 案例 5:無路徑引用 → 不報
    write(vault, "Systems/e.md", "type: system\nstatus: done", "# E\n純文字無反引號路徑。\n")

    r = run(vault, "doctor")
    check("Check P: 段標題出現", "[P]" in r.stdout, r.stdout)
    check("Check P: 案例1 報出 ghost", ("Systems/a.md" in r.stdout and "scripts/ghost.py" in r.stdout), r.stdout)
    check("Check P: 案例2 存在路徑不報", "scripts/real.py" not in r.stdout, r.stdout)
    check("Check P: 案例3 散文/非路徑不報", "and/or" not in r.stdout and "cmd_context" not in r.stdout, r.stdout)
    check("Check P: 案例4 fenced 內不報", r.stdout.count("scripts/ghost.py") == 1, r.stdout)  # 只有案例1那次
    check("Check P: rc 不變(warn_soft 軟提醒)", r.returncode == 0, f"rc={r.returncode}")

    # 案例 6:無 docs/ 佈局(mkvault 的 vault 不在 docs/ 下)→ Check P 略過
    v2 = mkvault()
    r2 = run(v2, "doctor")
    check("Check P: 無 docs/ 佈局略過", "略過失效認領" in r2.stdout, r2.stdout)


def _mk_refcheck_repo():
    """temp repo:scripts/real.py(5行) + 頂層 scripts/ 目錄;refcheck 用 --repo 顯式指定,免 git。"""
    root = Path(tempfile.mkdtemp(prefix="gctl-refcheck-"))
    (root / "scripts").mkdir()
    (root / "scripts" / "real.py").write_text(
        "L1 = 1\nL2 = 2\nL3 = 3\nL4 = 4\nL5 = 5\n", encoding="utf-8")
    return root


def t_refcheck():
    import json as _json
    root = _mk_refcheck_repo()

    # ---- 案例 1/3/4/5/7 + 目錄型:綜合 spec ----
    md_all = root / "spec-all.md"
    md_all.write_text(
        "# t\n"
        "缺:`scripts/ghost.py` 實作。\n"
        "在:`scripts/real.py:3` 與超界 `scripts/real.py:99` 與裸 `scripts/real.py`。\n"
        "範圍:`scripts/real.py:2-4`。\n"
        "目錄:`scripts/`。\n"
        "跳過:`https://x/y`、`and/or`、`cmd_context`、`governance/pending/*.md`。\n"
        "```\nfenced 內 `scripts/fenced.py` 不抓\n```\n",
        encoding="utf-8")
    r = run(root, "refcheck", str(md_all), "--repo", str(root), "--json")
    check("refcheck: 綜合 spec rc=1(有 missing+out_of_range)", r.returncode == 1,
          f"rc={r.returncode}\n{r.stdout}\n{r.stderr}")
    data = _json.loads(r.stdout)
    by_key = {(c["token"], c["line"]): c for c in data["claims"]}

    check("refcheck: ghost 報 missing",
          by_key.get(("scripts/ghost.py", ""), {}).get("status") == "missing", r.stdout)
    check("refcheck: real.py:3 ok 且 excerpt=第3行實際內容",
          by_key.get(("scripts/real.py", "3"), {}).get("status") == "ok"
          and by_key.get(("scripts/real.py", "3"), {}).get("excerpt") == "L3 = 3", r.stdout)
    check("refcheck: real.py:99 報 line_out_of_range",
          by_key.get(("scripts/real.py", "99"), {}).get("status") == "line_out_of_range", r.stdout)
    check("refcheck: 裸 real.py ok 且 excerpt 空",
          by_key.get(("scripts/real.py", ""), {}).get("status") == "ok"
          and by_key.get(("scripts/real.py", ""), {}).get("excerpt") == "", r.stdout)
    ex24 = by_key.get(("scripts/real.py", "2-4"), {}).get("excerpt", "")
    check("refcheck: 範圍 2-4 ok 且 excerpt 含首尾行",
          by_key.get(("scripts/real.py", "2-4"), {}).get("status") == "ok"
          and "L2 = 2" in ex24 and "L4 = 4" in ex24, r.stdout)
    check("refcheck: 同檔多行號不塌成一條(r3-F1,:3/:99/裸/2-4 各自成 claim)",
          len([c for c in data["claims"] if c["token"] == "scripts/real.py"]) == 4, r.stdout)
    check("refcheck: 目錄型 token ok+dir 註記、excerpt 空",
          by_key.get(("scripts/", ""), {}).get("status") == "ok"
          and by_key.get(("scripts/", ""), {}).get("dir") is True, r.stdout)
    skipped = {"https://x/y", "and/or", "cmd_context", "governance/pending/*.md",
               "scripts/fenced.py"}
    check("refcheck: url/非頂層/無斜線/glob/fenced 皆不入 claims",
          not any(c["token"] in skipped for c in data["claims"]), r.stdout)
    check("refcheck: 統計欄位正確(ok4/missing1/oor1)",
          data["ok"] == 4 and data["missing"] == 1 and data["out_of_range"] == 1, r.stdout)

    # ---- 案例 2:全 ok → rc 0 ----
    md_ok = root / "spec-ok.md"
    md_ok.write_text("# t\n只有 `scripts/real.py:3`。\n", encoding="utf-8")
    r = run(root, "refcheck", str(md_ok), "--repo", str(root), "--json")
    check("refcheck: 全 ok rc=0", r.returncode == 0, f"rc={r.returncode}\n{r.stdout}")

    # ---- 案例 6:--repo 解析失敗 → rc 2 ----
    r = run(root, "refcheck", str(md_ok), "--repo", str(root / "nope"))
    check("refcheck: --repo 不存在 rc=2", r.returncode == 2, f"rc={r.returncode}")

    # ---- md 檔不存在 → rc 2 ----
    r = run(root, "refcheck", str(root / "ghost.md"), "--repo", str(root))
    check("refcheck: md 不存在 rc=2", r.returncode == 2, f"rc={r.returncode}")

    # ---- 人讀版(無 --json)可跑、rc 語意一致 ----
    r = run(root, "refcheck", str(md_all), "--repo", str(root))
    check("refcheck: 人讀版 rc=1 且含統計行", r.returncode == 1 and "missing" in r.stdout,
          f"rc={r.returncode}\n{r.stdout}")


def _mk_anchor_repo():
    """_mk_git_vault(git repo + docs/kg vault + initial commit)疊 5 個假錨點檔。"""
    root, vault = _mk_git_vault()
    (root / "scripts" / "hooks").mkdir(parents=True)
    for rel in ("scripts/test_lumos.py", "scripts/test_autonomous_loop.py",
                "scripts/hooks/pre-commit", "scripts/hooks/pre-push",
                "scripts/hooks/post-commit"):
        (root / rel).write_text(f"# fake {rel}\n", encoding="utf-8")
    return root, vault


def t_anchor():
    import json as _json
    root, vault = _mk_anchor_repo()
    bp = root / "governance" / "anchor-baseline.json"

    # baseline 不存在 → rc 0 + 警示(漸進採用)
    r = run(vault, "anchor", "verify", "--repo", str(root))
    check("anchor: 無 baseline rc=0 且警示未啟用", r.returncode == 0 and "未啟用" in r.stdout,
          f"rc={r.returncode}\n{r.stdout}")

    # approve 缺 --note → argparse rc=2
    r = run(vault, "anchor", "approve", "--repo", str(root))
    check("anchor: approve 缺 --note rc=2", r.returncode == 2, f"rc={r.returncode}\n{r.stderr}")

    # approve → baseline 建立(5 錨點 + note),verify rc=0
    r = run(vault, "anchor", "approve", "--repo", str(root), "--note", "初始")
    check("anchor: approve rc=0", r.returncode == 0, f"rc={r.returncode}\n{r.stdout}\n{r.stderr}")
    data = _json.loads(bp.read_text(encoding="utf-8"))
    check("anchor: baseline 5 錨點+note+version",
          len(data["anchors"]) == 5 and data["note"] == "初始" and data["version"] == 1,
          bp.read_text(encoding="utf-8"))
    r = run(vault, "anchor", "verify", "--repo", str(root))
    check("anchor: approve 後 verify rc=0", r.returncode == 0, f"rc={r.returncode}\n{r.stdout}")

    # governance-log 留痕(gate=anchor-approve,note 進 lumos gov 顯示)
    gl = root / "docs" / ".governance-log.jsonl"
    check("anchor: gov-log 有 anchor-approve 事件",
          gl.exists() and "anchor-approve" in gl.read_text(encoding="utf-8"),
          gl.read_text(encoding="utf-8") if gl.exists() else "無檔")
    r = run(vault, "gov")
    check("anchor: lumos gov 顯示 approve note", "初始" in r.stdout, r.stdout)

    # 改一檔 → verify rc=1 且列出該檔;--json mismatches 精確
    (root / "scripts" / "hooks" / "pre-push").write_text("# tampered\n", encoding="utf-8")
    r = run(vault, "anchor", "verify", "--repo", str(root))
    check("anchor: 改檔 verify rc=1 且列出", r.returncode == 1 and "scripts/hooks/pre-push" in r.stdout,
          f"rc={r.returncode}\n{r.stdout}")
    r = run(vault, "anchor", "verify", "--repo", str(root), "--json")
    d = _json.loads(r.stdout)
    check("anchor: --json ok=false 且 mismatch 指名",
          d["ok"] is False and any(m["file"] == "scripts/hooks/pre-push" for m in d["mismatches"]),
          r.stdout)

    # 缺檔 → rc=1
    (root / "scripts" / "hooks" / "pre-push").unlink()
    r = run(vault, "anchor", "verify", "--repo", str(root))
    check("anchor: 缺檔 verify rc=1", r.returncode == 1 and "缺檔" in r.stdout,
          f"rc={r.returncode}\n{r.stdout}")

    # 重 approve(容忍缺檔:警示 + 只寫存在的 4 個)→ verify 回 0
    r = run(vault, "anchor", "approve", "--repo", str(root), "--note", "重簽")
    check("anchor: 缺檔重 approve rc=0 帶警示", r.returncode == 0 and "缺失" in r.stdout,
          f"rc={r.returncode}\n{r.stdout}")
    data = _json.loads(bp.read_text(encoding="utf-8"))
    check("anchor: 重簽後 baseline 4 錨點", len(data["anchors"]) == 4, str(data["anchors"].keys()))
    r = run(vault, "anchor", "verify", "--repo", str(root))
    check("anchor: 重簽後 verify rc=0", r.returncode == 0, f"rc={r.returncode}\n{r.stdout}")

    # --repo 解析失敗 → rc=2
    r = run(vault, "anchor", "verify", "--repo", str(root / "nope"))
    check("anchor: --repo 不存在 rc=2", r.returncode == 2, f"rc={r.returncode}")


def t_lint_aligned():
    import subprocess as sp
    import importlib.util as U
    from importlib.machinery import SourceFileLoader
    root = Path(tempfile.mkdtemp(prefix="gctl-la-"))
    def git(*a): sp.run(["git",*a],cwd=root,capture_output=True)
    git("init"); git("config","user.email","t@t"); git("config","user.name","t")
    (root/"a.kt").write_text("l1\n",encoding="utf-8")
    git("add","-A"); git("-c","user.email=t@t","-c","user.name=t","commit","-m","c1")
    (root/"a.kt").write_text("l1\nl2\n",encoding="utf-8")
    git("add","-A"); git("-c","user.email=t@t","-c","user.name=t","commit","-m","c2")
    # lumos 無 .py 副檔名 → spec_from_file_location 推不出 loader,顯式給 SourceFileLoader
    spec=U.spec_from_file_location("lm",GRAPHCTL,loader=SourceFileLoader("lm",GRAPHCTL))
    m=U.module_from_spec(spec); spec.loader.exec_module(m)
    # added 集合:c2 的 +l2 在第 2 行
    diff=sp.run(["git","diff","-U3","HEAD~1..HEAD"],cwd=root,capture_output=True,text=True).stdout
    added=m._diff_added_lines(diff)
    check("added: a.kt 第2行", added.get("a.kt")=={2}, str(added))
    # 對齊:乾淨 ..HEAD → True
    check("aligned: 乾淨 ..HEAD True", m._lint_aligned("HEAD~1..HEAD", root) is True, "")
    # 對齊:... symmetric split 不炸(右端 rsplit)
    check("aligned: ...HEAD 不炸", isinstance(m._lint_aligned("HEAD~1...HEAD", root), bool), "")
    # dirty tree → False
    (root/"a.kt").write_text("l1\nl2\nDIRTY\n",encoding="utf-8")
    check("aligned: dirty False", m._lint_aligned("HEAD~1..HEAD", root) is False, "")


def t_lint_config():
    import importlib.util as U
    from importlib.machinery import SourceFileLoader
    # lumos 無 .py 副檔名 → 顯式給 SourceFileLoader
    spec = U.spec_from_file_location("lm2", GRAPHCTL, loader=SourceFileLoader("lm2", GRAPHCTL))
    m = U.module_from_spec(spec); spec.loader.exec_module(m)

    root = Path(tempfile.mkdtemp(prefix="gctl-lc-"))
    lumos_dir = root / ".lumos"
    lumos_dir.mkdir()

    # Case 1: .kt 命中 → ["cmd1"]
    lint_json = lumos_dir / "lint.json"
    lint_json.write_text('{"kt":["cmd1"],"py":["cmd2"]}', encoding="utf-8")
    config = m._lint_load_config(root)
    check("lint_config: 讀取 .lumos/lint.json 回 dict", isinstance(config, dict), str(config))
    # added: a.kt 第 1 行
    added = {"a.kt": {1}}
    cmds = m._lint_stacks_for_diff(added, config)
    check("lint_config: .kt 命中 → [cmd1]", cmds == ["cmd1"], str(cmds))

    # Case 2: 無宣告副檔名 .vue → []
    added_vue = {"a.vue": {1}}
    cmds_vue = m._lint_stacks_for_diff(added_vue, config)
    check("lint_config: .vue 無宣告 → []", cmds_vue == [], str(cmds_vue))

    # Case 3: 無 .lumos/lint.json → _lint_load_config 回 None
    root2 = Path(tempfile.mkdtemp(prefix="gctl-lc2-"))
    result = m._lint_load_config(root2)
    check("lint_config: 無 lint.json → None", result is None, str(result))

    # Case 4: 多檔共享 stack → 去重,不重複 cmd
    added_multi = {"a.kt": {1}, "b.kt": {2}}
    cmds_multi = m._lint_stacks_for_diff(added_multi, config)
    check("lint_config: 多 .kt 共享 stack → 去重 [cmd1]", cmds_multi == ["cmd1"], str(cmds_multi))

    # Case 5: 壞 JSON → None
    lint_json.write_text("{bad json}", encoding="utf-8")
    result_bad = m._lint_load_config(root)
    check("lint_config: 壞 JSON → None", result_bad is None, str(result_bad))


def t_pitfalls_diff():
    import json as _json, subprocess as sp
    root = Path(tempfile.mkdtemp(prefix="gctl-pfd-"))
    def git(*a): sp.run(["git", *a], cwd=root, capture_output=True)
    git("init"); git("config", "user.email", "t@t"); git("config", "user.name", "t")
    (root / "app.py").write_text("x = 1\n", encoding="utf-8")
    git("add", "-A"); git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "init")
    # 新增:無 timeout 的 requests.post(資源類)+ 迴圈內 query(效能類)
    (root / "app.py").write_text(
        "import requests\n"
        "def f(ids):\n"
        "    requests.post('http://x')\n"
        "    for i in ids:\n"
        "        db.execute('SELECT 1')\n", encoding="utf-8")
    git("add", "-A"); git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "c2")
    r = run(root, "pitfalls", "--diff", "HEAD~1..HEAD", "--repo", str(root), "--json")
    check("pitfalls --diff: rc 0(提示器)", r.returncode == 0, f"rc={r.returncode}\n{r.stderr}")
    data = _json.loads([l for l in r.stdout.splitlines() if l.strip().startswith("{")][0])
    tokens = " ".join(f"{c['pattern']}|{c['class']}" for c in data["claims"])
    check("pitfalls --diff: 命中無 timeout requests(資源)", "資源" in tokens, r.stdout)
    check("pitfalls --diff: 命中迴圈內 query(效能)", "效能" in tokens, r.stdout)
    check("pitfalls --diff: tier high", data["tier"] == "high", r.stdout)
    check("pitfalls --diff: class 用形態軸非四業務類",
          all(c["class"] in ("併發", "效能", "資源") for c in data["claims"]), r.stdout)
    check("pitfalls --diff: 每條有 line", all(isinstance(c["line"], int) for c in data["claims"]), r.stdout)
    check("pitfalls --diff: requests.post 在第 3 行", any(c["line"] == 3 for c in data["claims"]), r.stdout)
    check("pitfalls --diff: SELECT 在第 5 行", any(c["line"] == 5 for c in data["claims"]), r.stdout)
    # 純文檔 diff → tier standard
    (root / "readme.md").write_text("hello\n", encoding="utf-8")
    git("add", "-A"); git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "doc")
    r = run(root, "pitfalls", "--diff", "HEAD~1..HEAD", "--repo", str(root), "--json")
    data = _json.loads([l for l in r.stdout.splitlines() if l.strip().startswith("{")][0])
    check("pitfalls --diff: .md skip → tier standard", data["tier"] == "standard", r.stdout)
    # 測試檔內的 requests.post 不觸發(過濾繼承 _TEST_PAT)
    (root / "test_app.py").write_text("import requests\nrequests.post('http://y')\n", encoding="utf-8")
    git("add", "-A"); git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "t")
    r = run(root, "pitfalls", "--diff", "HEAD~1..HEAD", "--repo", str(root), "--json")
    data = _json.loads([l for l in r.stdout.splitlines() if l.strip().startswith("{")][0])
    check("pitfalls --diff: 測試檔 skip → tier standard", data["tier"] == "standard", r.stdout)
    # 併發寫入案: INSERT → class=併發(證第 6 條不再是死碼)
    (root / "write_op.py").write_text(
        "def store(val):\n"
        "    db.execute('INSERT INTO t VALUES(1)')\n", encoding="utf-8")
    git("add", "-A"); git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "insert")
    r = run(root, "pitfalls", "--diff", "HEAD~1..HEAD", "--repo", str(root), "--json")
    data = _json.loads([l for l in r.stdout.splitlines() if l.strip().startswith("{")][0])
    check("pitfalls --diff: INSERT → class=併發(第 6 條不死碼)", any(c["class"] == "併發" for c in data["claims"]), r.stdout)


def t_pitfalls_spec():
    root = Path(tempfile.mkdtemp(prefix="gctl-pf-"))
    (root / ".git").mkdir()
    # 命中 payment + external-send
    md_hit = root / "hit.md"
    md_hit.write_text("# s\n## 目標\n接 stripe 收款後寄送通知。\n## 組件\n扣款流程。\n", encoding="utf-8")
    r = run(root, "pitfalls", str(md_hit), "--repo", str(root))
    check("pitfalls spec: 印通用 3 問", "併發" in r.stdout and "效能" in r.stdout and "資源" in r.stdout, r.stdout)
    check("pitfalls spec: 命中 payment 追問", "冪等" in r.stdout, r.stdout)
    check("pitfalls spec: 命中 external-send 追問", "去重" in r.stdout or "重試" in r.stdout, r.stdout)
    # --check 命中且無節 → rc 1
    r = run(root, "pitfalls", str(md_hit), "--repo", str(root), "--check")
    check("pitfalls --check: 命中無節 rc 1", r.returncode == 1, f"rc={r.returncode}\n{r.stdout}")
    # 補節 → rc 0
    md_ok = root / "ok.md"
    md_ok.write_text("# s\n## 目標\n接 stripe 收款。\n## 實務隱患\n冪等鍵用訂單號。\n", encoding="utf-8")
    r = run(root, "pitfalls", str(md_ok), "--repo", str(root), "--check")
    check("pitfalls --check: 有節 rc 0", r.returncode == 0, f"rc={r.returncode}\n{r.stdout}")
    # 零命中 → rc 0(無節也不擋)
    md_clean = root / "clean.md"
    md_clean.write_text("# s\n## 目標\n重構內部排序,無外部行為。\n## 組件\n拆函數。\n", encoding="utf-8")
    r = run(root, "pitfalls", str(md_clean), "--repo", str(root), "--check")
    check("pitfalls --check: 零命中無節 rc 0", r.returncode == 0, f"rc={r.returncode}\n{r.stdout}")
    check("pitfalls spec: 零命中只印通用問", "冪等" not in r.stdout, r.stdout)
    # 剝除:風險詞只在黑名單樣板節 → 不觸發
    md_tmpl = root / "tmpl.md"
    md_tmpl.write_text("# s\n## 目標\n" + "純內部整理。" * 20 +
                       "\n## 組件\n" + "改函數命名。" * 20 +
                       "\n## 審計修正紀錄\nr1 canary 抓到金流 stripe 扣款壞 ref。\n", encoding="utf-8")
    r = run(root, "pitfalls", str(md_tmpl), "--repo", str(root), "--check")
    check("pitfalls 剝除: 風險詞只在審計紀錄節 → --check rc 0", r.returncode == 0, f"rc={r.returncode}\n{r.stdout}")
    # md 不存在 → rc 2
    r = run(root, "pitfalls", str(root / "ghost.md"), "--repo", str(root))
    check("pitfalls: md 不存在 rc 2", r.returncode == 2, f"rc={r.returncode}")


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("t_")]
    print(f"lumos 測試({len(tests)} 案例)")
    for t in tests:
        try:
            t()
        except Exception as e:
            global FAIL
            FAIL += 1
            print(f"  ✗ {t.__name__} EXCEPTION: {e}")
    print(f"\n{'─'*40}\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
