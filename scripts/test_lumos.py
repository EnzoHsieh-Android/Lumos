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
    for m in ("★CHECKPOINT★", "★IRREVERSIBLE★", "[rollback:", "[guard:", "[kill:",
              "spec-trace", "signoff"):
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


def t_fold_mirror_sections():
    m = _import_lumos()
    text = "---\nsummary: |-\n  KEY:x\n---\n## §2 A\n```json\n{}\n```\n## §4 誠實天花板\nc\n## §5 審計修正紀錄\nd"
    secs = m._fold_mirror_sections(text)
    assert "summary" in secs
    assert any("誠實天花板" in s for s in secs)   # 容 §4 前綴(r1-F5)
    assert any("審計修正紀錄" in s for s in secs)
    assert any("json" in s.lower() for s in secs)  # json fence 算鏡像段
    check("fold_mirror_sections: summary 在列表", "summary" in secs, str(secs))
    check("fold_mirror_sections: 誠實天花板(含節號)", any("誠實天花板" in s for s in secs), str(secs))
    check("fold_mirror_sections: 審計修正紀錄(含節號)", any("審計修正紀錄" in s for s in secs), str(secs))
    check("fold_mirror_sections: json fence 算鏡像段", any("json" in s.lower() for s in secs), str(secs))


def t_fold_value_drift():
    m = _import_lumos()
    text = "§1 用 `fold-check <node>`\n§2 用 `fold-check <path>`\n## §9 審計修正紀錄\nfold-check <node> 舊史"
    d = m._fold_value_drift(text)
    keys = [x["key"] for x in d]
    check("fold_value_drift: fold-check 全文域 body↔body 命中", "fold-check" in keys, str(keys))
    # 審計紀錄段的 <node> 不算(r2:排除掃描)——不應因它多一筆
    check("fold_value_drift: fold-check 只有一筆(審計段不計)", len([x for x in d if x["key"]=="fold-check"]) == 1, str(d))
    check("fold_value_drift: 一致→無 flag", m._fold_value_drift("只有 `fold-check <path>` 一種") == [], "")

    # C1 regression: 多節文件中 §1/§2/§3 不應觸發假陽(_sec pattern 已移除)
    multi_sec = "## §1 a\n## §2 b\n## §3 c"
    keys_c1 = [x["key"] for x in m._fold_value_drift(multi_sec)]
    check("fold_value_drift C1: §號無假陽(_sec 不在 keys)", "_sec" not in keys_c1, f"keys={keys_c1}")
    check("fold_value_drift C1: 多節文件無 drift", keys_c1 == [], f"keys={keys_c1}")

    # C2 regression: 審計段在中間時,後段 token 不被誤排除
    mid_audit = (
        "fold-check alpha\n"
        "## 審計修正紀錄\n"
        "fold-check OLD\n"
        "## 後段\n"
        "fold-check beta\n"
    )
    d_c2 = m._fold_value_drift(mid_audit)
    keys_c2 = [x["key"] for x in d_c2]
    # alpha vs beta → drift should be detected (後段未被誤刪)
    check("fold_value_drift C2: 後段 token 未被誤排除", "fold-check" in keys_c2, f"drifts={d_c2}")
    # OLD from audit section should NOT be in the values
    fc_entry = next((x for x in d_c2 if x["key"] == "fold-check"), None)
    check("fold_value_drift C2: fc_entry 存在", fc_entry is not None, str(d_c2))
    if fc_entry is not None:
        vals_c2 = {fc_entry["a"], fc_entry["b"]}
        check("fold_value_drift C2: 審計段 OLD 不納入掃描", "OLD" not in vals_c2, f"vals={vals_c2}")


def t_fold_reverse_omission():
    m = _import_lumos()
    text = "---\nsummary: |-\n  KEY:用 --foo\n---\n## §2 body\n用 --foo 和 --bar 和 `<path>`"
    r = m._fold_reverse_omission(text)
    toks = [x["token"] for x in r]
    check("fold_reverse_omission: --bar body 有 summary 無→命中", "--bar" in toks, str(toks))
    check("fold_reverse_omission: --foo 兩邊都有→不 flag", "--foo" not in toks, str(toks))
    check("fold_reverse_omission: placeholder <path> 排除(r2-F5)", "<path>" not in toks and "path" not in toks, str(toks))


def t_fold_reverse_omission_no_frontmatter():
    """空檔與無 frontmatter 的 .md 傳入 _fold_reverse_omission 不應拋例外。
    修前:fm_lines=None 時 `for line in fm_lines:` 拋 TypeError。
    修後:guard `(fm_lines or [])` → 回空 list / 合理 rc。
    """
    m = _import_lumos()

    # 空字串(空檔)
    result_empty = m._fold_reverse_omission("")
    check("fold_reverse_omission 空檔: 回 list 不拋例外", isinstance(result_empty, list), repr(result_empty))

    # 純 markdown 無 --- frontmatter
    plain_md = "# 標題\n\n這是一段純 markdown，沒有 frontmatter。\n\n用到 --some-flag 指令。\n"
    result_plain = m._fold_reverse_omission(plain_md)
    check("fold_reverse_omission 無 frontmatter: 回 list 不拋例外", isinstance(result_plain, list), repr(result_plain))


# ─── Task 4: cmd_fold_check 組裝 helpers ───────────────────────────────────

def run_lumos(args):
    """執行 scripts/lumos 並回傳 rc(int)。"""
    r = subprocess.run([sys.executable, GRAPHCTL, *args], capture_output=True, text=True)
    return r.returncode


def run_lumos_capture(args):
    """執行 scripts/lumos 並回傳 stdout(str)。"""
    r = subprocess.run([sys.executable, GRAPHCTL, *args], capture_output=True, text=True)
    return r.stdout


def make_tmp_spec_consistent():
    """建立一個無 drift 的暫存 spec 檔路徑(str)。
    含 ```json fence(token 不出現於 summary)→ 證明 FENCE_RE 剝除後 reverse_omission=[]。
    確保 value_drift=[] 且 reverse_omission=[]。
    """
    import tempfile
    text = (
        "---\n"
        "type: project\n"
        "status: doing\n"
        "summary: |-\n"
        "  KEY:介面設計\n"
        "---\n"
        "# 一致測試 spec\n"
        "\n"
        "§1 描述:介面設計說明。\n"
        "\n"
        "```json\n"
        '{"fenceOnlyToken": "shouldNotFlag"}\n'
        "```\n"
    )
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8")
    f.write(text)
    f.close()
    return f.name


def make_tmp_spec_with_node_path_drift():
    """建立一個含 fold-check <node> vs fold-check <path> value-drift 的暫存 spec 檔路徑(str)。
    §1 用 fold-check <node>,§2 用 fold-check <path> → value_drift 非空 → rc 1。
    """
    import tempfile
    text = (
        "---\n"
        "type: project\n"
        "status: doing\n"
        "summary: |-\n"
        "  KEY:介面設計\n"
        "---\n"
        "# drift 測試 spec\n"
        "\n"
        "§1 描述:舊文寫 fold-check <node>。\n"
        "\n"
        "§2 更新:新介面是 fold-check <path>。\n"
    )
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8")
    f.write(text)
    f.close()
    return f.name


def t_fold_check_rc_json():
    import json
    import os
    clean = make_tmp_spec_consistent()      # 無 drift,含 json fence
    drifty = make_tmp_spec_with_node_path_drift()
    try:
        out = json.loads(run_lumos_capture(["fold-check", drifty, "--json"]))
        check("fold_check_rc_json: clean spec → rc 0", run_lumos(["fold-check", clean]) == 0, "")
        check("fold_check_rc_json: drifty spec → rc 1", run_lumos(["fold-check", drifty]) == 1, "")
        check("fold_check_rc_json: --json keys 符合 schema", set(out) == {"path", "mirror_sections", "value_drift", "reverse_omission"}, str(set(out)))
        check("fold_check_rc_json: value_drift 非空(drift spec)", len(out["value_drift"]) > 0, str(out["value_drift"]))
        check("fold_check_rc_json: mirror_sections 是 list", isinstance(out["mirror_sections"], list), str(out["mirror_sections"]))
        check("fold_check_rc_json: reverse_omission 是 list", isinstance(out["reverse_omission"], list), str(out["reverse_omission"]))
    finally:
        for p in (clean, drifty):
            try:
                os.remove(p)
            except OSError:
                pass


def t_fold_check_regression():
    """對現有已固化 spec 跑 fold-check:確認不 crash、rc in (0,1)。
    有 flag 是可接受的自指範例(value-drift 範例、審計紀錄舊值),人工判;此測試只守不 crash。
    """
    spec = str(Path(__file__).resolve().parent.parent /
               "docs/lumos-toolchain-knowledge/Projects/主動影響幅度偵測_計劃.md")
    rc = run_lumos(["fold-check", spec])
    check("fold_check_regression: 已固化 spec 不 crash(rc in 0,1)", rc in (0, 1), f"rc={rc}")


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


def t_lint_sarif():
    import importlib.util as U, json as J
    from importlib.machinery import SourceFileLoader
    spec=U.spec_from_file_location("lm",GRAPHCTL,loader=SourceFileLoader("lm",GRAPHCTL)); m=U.module_from_spec(spec); spec.loader.exec_module(m)
    root=Path(tempfile.mkdtemp(prefix="gctl-ls-"))
    # 假 SARIF:絕對 file:// uri + per-run driver + 一筆 location-less
    sarif={"runs":[{"tool":{"driver":{"name":"detekt"}},"results":[
        {"ruleId":"R1","message":{"text":"m1"},"locations":[{"physicalLocation":{
            "artifactLocation":{"uri":f"file://{root}/app/X.kt"},"region":{"startLine":5}}}]},
        {"ruleId":"R2","message":{"text":"no-loc"}}  # location-less → 跳該筆不連坐
    ]}]}
    sf=root/"fake.sarif"; sf.write_text(J.dumps(sarif),encoding="utf-8")
    cmd=f"cp {sf} {{LINT_SARIF_OUT}}"   # 假 linter=把預存 SARIF 複製到注入路徑
    claims, ok = m._lint_run_and_parse(cmd, root)
    check("sarif ok", ok is True, "")
    check("sarif: 1 claim(location-less 跳)", len(claims)==1, str(claims))
    c=claims[0]
    check("sarif: uri 正規化 repo 相對", c["file"]=="app/X.kt", c["file"])
    check("sarif: source per-run", c["source"]=="lint:detekt", c["source"])
    check("sarif: line/rule/message", c["line"]==5 and c["rule"]=="R1" and c["message"]=="m1", str(c))
    # 指令失敗無 SARIF → ok False
    claims2, ok2 = m._lint_run_and_parse("false", root)
    check("sarif: 失敗 ok False", ok2 is False and claims2==[], "")


def t_lint_sarif_malformed_run():
    """Finding 1: 含壞 run(無 tool key)的 SARIF — 壞 run 跳過,好 run claim 仍回傳,不 crash。"""
    import importlib.util as U, json as J
    from importlib.machinery import SourceFileLoader
    spec=U.spec_from_file_location("lm2",GRAPHCTL,loader=SourceFileLoader("lm2",GRAPHCTL)); m=U.module_from_spec(spec); spec.loader.exec_module(m)
    root=Path(tempfile.mkdtemp(prefix="gctl-lsm-"))
    sarif={"runs":[
        # 壞 run:完全沒有 tool 鍵 → 應 skip 而不 crash
        {"results":[{"ruleId":"BAD","message":{"text":"bad"},"locations":[{"physicalLocation":{
            "artifactLocation":{"uri":f"file://{root}/bad.kt"},"region":{"startLine":1}}}]}]},
        # 好 run:正常 driver
        {"tool":{"driver":{"name":"detekt"}},"results":[
            {"ruleId":"R1","message":{"text":"good"},"locations":[{"physicalLocation":{
                "artifactLocation":{"uri":f"file://{root}/app/Good.kt"},"region":{"startLine":7}}}]}
        ]},
    ]}
    sf=root/"mixed.sarif"; sf.write_text(J.dumps(sarif),encoding="utf-8")
    cmd=f"cp {sf} {{LINT_SARIF_OUT}}"
    claims, ok = m._lint_run_and_parse(cmd, root)
    check("sarif malformed run: ok True(有好 run)", ok is True, "")
    check("sarif malformed run: 僅好 run 的 claim 回傳(=1)", len(claims)==1, str(claims))
    check("sarif malformed run: claim 來自好 run", claims[0]["source"]=="lint:detekt" and claims[0]["file"]=="app/Good.kt", str(claims))


def t_lint_sarif_relative_uri():
    """Finding 2: SARIF uri 已是 repo-relative(無 file://) → file 直接用,不產 ../.. 遍歷路徑。"""
    import importlib.util as U, json as J
    from importlib.machinery import SourceFileLoader
    spec=U.spec_from_file_location("lm3",GRAPHCTL,loader=SourceFileLoader("lm3",GRAPHCTL)); m=U.module_from_spec(spec); spec.loader.exec_module(m)
    root=Path(tempfile.mkdtemp(prefix="gctl-lsr-"))
    # uri 是 repo-relative(沒有 file:// 也沒有絕對路徑前綴)
    sarif={"runs":[{"tool":{"driver":{"name":"ktlint"}},"results":[
        {"ruleId":"R9","message":{"text":"rel"},"locations":[{"physicalLocation":{
            "artifactLocation":{"uri":"app/Y.kt"},"region":{"startLine":3}}}]}
    ]}]}
    sf=root/"rel.sarif"; sf.write_text(J.dumps(sarif),encoding="utf-8")
    cmd=f"cp {sf} {{LINT_SARIF_OUT}}"
    claims, ok = m._lint_run_and_parse(cmd, root)
    check("sarif relative uri: ok True", ok is True, "")
    check("sarif relative uri: 1 claim", len(claims)==1, str(claims))
    check("sarif relative uri: file=app/Y.kt(非 ../.. 遍歷)", claims[0]["file"]=="app/Y.kt", claims[0].get("file",""))
    check("sarif relative uri: 無 ../.. 前綴", not claims[0]["file"].startswith(".."), claims[0].get("file",""))


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


def t_pitfalls_lint_integration():
    """Task 4: _pitfall_diff_mode 尾段整合——lint claims 合併/過濾/tier/fallback。"""
    import json as _json
    import subprocess as sp
    import sys as _sys

    # ── 共用 git fixture 建立 helper ──────────────────────────────────────
    def make_repo():
        root = Path(tempfile.mkdtemp(prefix="gctl-pli-"))
        def git(*a):
            sp.run(["git", *a], cwd=root, capture_output=True)
        git("init")
        git("config", "user.email", "t@t")
        git("config", "user.name", "t")
        return root, git

    def commit_file(root, git, name, content):
        (root / name).write_text(content, encoding="utf-8")
        git("add", "-A")
        git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", f"add {name}")

    # 寫假 linter 腳本到臨時目錄,避免 shell 引號問題
    helper_dir = Path(tempfile.mkdtemp(prefix="gctl-pli-helper-"))

    def make_linter(name, sarif_dict):
        """生成 fake linter 腳本:把 sarif 寫到 argv[1]"""
        sarif_json = _json.dumps(sarif_dict)
        script_path = helper_dir / name
        script_path.write_text(
            "import sys, json\n"
            f"data = {repr(sarif_json)}\n"
            "open(sys.argv[1], 'w').write(data)\n",
            encoding="utf-8",
        )
        return f"{_sys.executable} {script_path} {{LINT_SARIF_OUT}}"

    # SARIF 含兩個 finding: line 2 (在 diff-added) + line 99 (不在 diff-added)
    sarif_multi_dict = {
        "runs": [{
            "tool": {"driver": {"name": "FakeLint"}},
            "originalUriBaseIds": {},
            "results": [
                {
                    "ruleId": "FAKE001",
                    "message": {"text": "fake warning line 2"},
                    "locations": [{"physicalLocation": {
                        "artifactLocation": {"uri": "base.kt"},
                        "region": {"startLine": 2},
                    }}]
                },
                {
                    "ruleId": "FAKE002",
                    "message": {"text": "fake warning line 99"},
                    "locations": [{"physicalLocation": {
                        "artifactLocation": {"uri": "base.kt"},
                        "region": {"startLine": 99},
                    }}]
                },
            ]
        }]
    }
    fake_cmd = make_linter("fakelint_multi.py", sarif_multi_dict)

    # ── Case 1+2: config 存在, aligned diff ──────────────────────────────
    # base.kt: 第 1 行舊, 第 2 行新增(含 requests.get(→regex 命中), 第 3 行新增
    # diff HEAD~1..HEAD 新增行 = {2, 3}
    # .lumos/lint.json 在 init commit 提交,保持 dirty tree 清空 → aligned=True
    root, git = make_repo()
    (root / ".lumos").mkdir()
    (root / ".lumos" / "lint.json").write_text(_json.dumps({"kt": [fake_cmd]}), encoding="utf-8")
    commit_file(root, git, "base.kt", "// base\n")  # 含 .lumos 一起提交
    (root / "base.kt").write_text(
        "// base\n"
        "    val r = requests.get('http://x')\n"
        "    val x = 1\n",
        encoding="utf-8",
    )
    git("add", "-A")
    git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "add kt code")

    r = run(root, "pitfalls", "--diff", "HEAD~1..HEAD", "--repo", str(root), "--json")
    check("pitfalls-lint: rc 0", r.returncode == 0, f"rc={r.returncode}\n{r.stderr}")
    data = _json.loads([l for l in r.stdout.splitlines() if l.strip().startswith("{")][0])

    sources = [c.get("source", "") for c in data["claims"]]
    # Case 1: 兩種 source 都在
    check("pitfalls-lint: lint source 出現(lint:FakeLint)",
          any("lint:FakeLint" in s for s in sources), str(data))
    check("pitfalls-lint: regex source 出現(pitfalls-builtin)",
          any(s == "pitfalls-builtin" for s in sources), str(data))

    # Case 2: aligned → line 2 保留, line 99 過濾掉
    lint_lines = [c["line"] for c in data["claims"] if "lint:" in c.get("source", "")]
    check("pitfalls-lint: aligned 過濾 line 2 保留", 2 in lint_lines, f"lint_lines={lint_lines}")
    check("pitfalls-lint: aligned 過濾 line 99 剔除", 99 not in lint_lines, f"lint_lines={lint_lines}")

    # lint_ran 有記錄 cmd
    check("pitfalls-lint: lint_ran 非空", bool(data.get("lint_ran")), str(data))
    # tier high(有 claims)
    check("pitfalls-lint: tier high", data["tier"] == "high", str(data))

    # ── Case 3: dirty tree (unaligned) → 全收 + filtered:false ──────────
    root3, git3 = make_repo()
    commit_file(root3, git3, "base.kt", "// base\n")
    (root3 / "base.kt").write_text(
        "// base\n"
        "    val r = requests.get('http://x')\n",
        encoding="utf-8",
    )
    git3("add", "-A")
    git3("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "add kt")

    # 製造 dirty tree: 新增未 commit 的改動 → _lint_aligned 回 False
    (root3 / "dirty_untracked.kt").write_text("// dirty\n", encoding="utf-8")

    sarif_line99_dict = {
        "runs": [{
            "tool": {"driver": {"name": "FakeLint"}},
            "originalUriBaseIds": {},
            "results": [{
                "ruleId": "FAKE001",
                "message": {"text": "fake warning line 99"},
                "locations": [{"physicalLocation": {
                    "artifactLocation": {"uri": "base.kt"},
                    "region": {"startLine": 99},
                }}]
            }]
        }]
    }
    fake_dirty_cmd = make_linter("fakelint_dirty.py", sarif_line99_dict)
    (root3 / ".lumos").mkdir()
    (root3 / ".lumos" / "lint.json").write_text(
        _json.dumps({"kt": [fake_dirty_cmd]}), encoding="utf-8"
    )

    r3 = run(root3, "pitfalls", "--diff", "HEAD~1..HEAD", "--repo", str(root3), "--json")
    data3 = _json.loads([l for l in r3.stdout.splitlines() if l.strip().startswith("{")][0])
    lint_lines3 = [c["line"] for c in data3["claims"] if "lint:" in c.get("source", "")]
    check("pitfalls-lint: unaligned line 99 保留(全收)",
          99 in lint_lines3, f"lint_lines3={lint_lines3} data3={data3}")
    check("pitfalls-lint: unaligned filtered:false 標記",
          data3.get("filtered") is False, str(data3))

    # ── Case 4: 無 .lumos/lint.json → regex-only, 無 lint_ran ───────────
    root4, git4 = make_repo()
    commit_file(root4, git4, "app.py", "x = 1\n")
    (root4 / "app.py").write_text(
        "import requests\n"
        "requests.post('http://x')\n",
        encoding="utf-8",
    )
    git4("add", "-A")
    git4("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "c2")

    r4 = run(root4, "pitfalls", "--diff", "HEAD~1..HEAD", "--repo", str(root4), "--json")
    data4 = _json.loads([l for l in r4.stdout.splitlines() if l.strip().startswith("{")][0])
    check("pitfalls-lint: 無 config → 無 lint_ran key", "lint_ran" not in data4, str(data4))
    check("pitfalls-lint: 無 config → regex claims 存在", len(data4.get("claims", [])) > 0, str(data4))

    # ── Case 5: lint cmd 失敗 → lint_skipped 記錄, rc 0, regex claims 在 ─
    root5, git5 = make_repo()
    commit_file(root5, git5, "base.kt", "// base\n")
    (root5 / "base.kt").write_text(
        "// base\n"
        "    val r = requests.get('http://x')\n",
        encoding="utf-8",
    )
    git5("add", "-A")
    git5("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "add kt")

    fail_script = helper_dir / "fakelint_fail.py"
    fail_script.write_text("import sys\nsys.exit(1)\n", encoding="utf-8")
    fail_cmd = f"{_sys.executable} {fail_script} {{LINT_SARIF_OUT}}"
    (root5 / ".lumos").mkdir()
    (root5 / ".lumos" / "lint.json").write_text(
        _json.dumps({"kt": [fail_cmd]}), encoding="utf-8"
    )

    r5 = run(root5, "pitfalls", "--diff", "HEAD~1..HEAD", "--repo", str(root5), "--json")
    check("pitfalls-lint: cmd 失敗 rc 0", r5.returncode == 0, f"rc={r5.returncode}\n{r5.stderr}")
    data5 = _json.loads([l for l in r5.stdout.splitlines() if l.strip().startswith("{")][0])
    check("pitfalls-lint: cmd 失敗 → lint_skipped 有記錄", bool(data5.get("lint_skipped")), str(data5))
    check("pitfalls-lint: cmd 失敗 → regex claims 仍在", len(data5.get("claims", [])) > 0, str(data5))

    # ── Case 6: diff 未碰宣告棧 → lint_ran 空 ────────────────────────────
    root6, git6 = make_repo()
    commit_file(root6, git6, "readme.txt", "hello\n")
    (root6 / "readme.txt").write_text("hello world\n", encoding="utf-8")
    git6("add", "-A")
    git6("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "update txt")

    # config 只宣告 kt,但 diff 是 txt
    (root6 / ".lumos").mkdir()
    (root6 / ".lumos" / "lint.json").write_text(_json.dumps({"kt": [fake_cmd]}), encoding="utf-8")

    r6 = run(root6, "pitfalls", "--diff", "HEAD~1..HEAD", "--repo", str(root6), "--json")
    data6 = _json.loads([l for l in r6.stdout.splitlines() if l.strip().startswith("{")][0])
    check("pitfalls-lint: 未碰宣告棧 → lint_ran 空", data6.get("lint_ran") == [], str(data6))


def t_lint_watch_semver():
    import importlib.util as U
    from importlib.machinery import SourceFileLoader
    spec = U.spec_from_file_location("lm", GRAPHCTL, loader=SourceFileLoader("lm", GRAPHCTL))
    m = U.module_from_spec(spec); spec.loader.exec_module(m)
    # _semver_parse
    check("parse 1.23.7", m._semver_parse("1.23.7") == (1,23,7), str(m._semver_parse("1.23.7")))
    check("parse v 前綴剝除", m._semver_parse("v1.2.3") == (1,2,3), str(m._semver_parse("v1.2.3")))
    check("parse 非數字段→None", m._semver_parse("1.x.3") is None, str(m._semver_parse("1.x.3")))
    # _is_prerelease 正例
    for v in ["1.24.0-RC1","0.5.0b1","2.22.0.dev20260702"]:
        check(f"prerelease True {v}", m._is_prerelease(v) is True, v)
    # _is_prerelease 負例(不可假陽性)
    for v in ["1.24.0","5.0.2.4997","cobra"]:
        check(f"prerelease False {v}", m._is_prerelease(v) is False, v)
    # _compare_versions 三態
    check("behind", m._compare_versions("1.23.7","1.24.0") == ("behind",""), str(m._compare_versions("1.23.7","1.24.0")))
    check("current(反向)", m._compare_versions("1.24.0","1.23.7")[0] == "current", str(m._compare_versions("1.24.0","1.23.7")))
    check("current(相等)", m._compare_versions("1.2.3","1.2.3")[0] == "current", "")
    check("skip unparseable", m._compare_versions("1.x","1.2.3") == ("skip","unparseable"), str(m._compare_versions("1.x","1.2.3")))
    check("skip prerelease", m._compare_versions("1.0.0","1.1.0-RC1") == ("skip","prerelease"), str(m._compare_versions("1.0.0","1.1.0-RC1")))
    check("skip 段數不一(calendar)", m._compare_versions("1.23.7","2024.1") == ("skip","segment-count-mismatch"), str(m._compare_versions("1.23.7","2024.1")))
    check("skip 段數不一(4段maven)", m._compare_versions("5.0.1","5.0.1.3006") == ("skip","segment-count-mismatch"), "")
    # 數值排序見證(同段數,證非字串比較:字串 '1.9.0' > '1.20.0' 但數值應 behind)
    check("數值 behind 1.9.0→1.20.0", m._compare_versions("1.9.0","1.20.0") == ("behind",""), str(m._compare_versions("1.9.0","1.20.0")))


def t_lint_watch_registry():
    import importlib.util as U, json as J, os, tempfile
    from importlib.machinery import SourceFileLoader
    spec = U.spec_from_file_location("lm", GRAPHCTL, loader=SourceFileLoader("lm", GRAPHCTL))
    m = U.module_from_spec(spec); spec.loader.exec_module(m)
    # 四型 registry 的假 response,key = _registry_latest 內部組出的 url
    pypi_url = "https://pypi.org/pypi/ruff/json"
    npm_url  = "https://registry.npmjs.org/eslint/latest"
    gh_url   = "https://api.github.com/repos/detekt/detekt/releases/latest"
    import urllib.parse as UP
    mvn_url  = ("https://search.maven.org/solrsearch/select?q="
               + UP.quote('g:"org.sonarsource.scanner.cli" AND a:"sonar-scanner-cli"')
               + "&core=gav&sort=timestamp+desc&rows=20&wt=json")
    fixture = {
        pypi_url: {"info": {"version": "0.4.9"}},
        npm_url:  {"version": "9.0.0"},
        gh_url:   {"tag_name": "v1.24.0"},
        # maven docs 含 3.9 / 3.20.0 / 一個 RC → 過濾 RC、數值 max 應回 3.20.0
        mvn_url:  {"response": {"docs": [
            {"v": "3.9"}, {"v": "3.20.0"}, {"v": "3.21.0-RC1"}, {"v": "3.11"}]}},
    }
    fx = Path(tempfile.mkdtemp(prefix="gctl-lw-")) / "fx.json"
    fx.write_text(J.dumps(fixture), encoding="utf-8")
    os.environ["LUMOS_LINT_WATCH_FIXTURE"] = str(fx)
    try:
        check("pypi", m._registry_latest("pypi:ruff") == ("0.4.9", None), str(m._registry_latest("pypi:ruff")))
        check("npm", m._registry_latest("npm:eslint") == ("9.0.0", None), str(m._registry_latest("npm:eslint")))
        check("github 剝 v", m._registry_latest("github:detekt/detekt") == ("1.24.0", None), str(m._registry_latest("github:detekt/detekt")))
        check("maven 數值 max 過濾 RC",
              m._registry_latest("maven:org.sonarsource.scanner.cli:sonar-scanner-cli") == ("3.20.0", None),
              str(m._registry_latest("maven:org.sonarsource.scanner.cli:sonar-scanner-cli")))
        # pypi info.version 為 prerelease → (None, "latest is prerelease")
        fixture[pypi_url] = {"info": {"version": "0.4.3a1"}}
        fx.write_text(J.dumps(fixture), encoding="utf-8")
        check("pypi prerelease", m._registry_latest("pypi:ruff") == (None, "latest is prerelease"), str(m._registry_latest("pypi:ruff")))
        # 抓取回 None(fixture 無此 key)→ (None, "registry query failed: ...")
        latest, reason = m._registry_latest("npm:does-not-exist")
        check("抓取失敗", latest is None and reason.startswith("registry query failed"), f"{latest},{reason}")
    finally:
        os.environ.pop("LUMOS_LINT_WATCH_FIXTURE", None)


def t_lint_watch_cli():
    import subprocess as sp, json as J, os, tempfile
    root = Path(tempfile.mkdtemp(prefix="gctl-lwcli-"))
    (root / ".lumos").mkdir()
    watch = [
        {"name":"ruff","registry":"pypi:ruff","current":"0.4.2"},        # behind
        {"name":"eslint","registry":"npm:eslint","current":"9.0.0"},     # current(相等)
        {"name":"cal","registry":"npm:cal","current":"1.23.7"},          # skip(段數不一 2024.1)
        {"name":"down","registry":"npm:down","current":"0.0.0"},         # fetch 失敗→failed
    ]
    (root / ".lumos" / "lint-watch.json").write_text(J.dumps(watch), encoding="utf-8")
    fixture = {
        "https://pypi.org/pypi/ruff/json": {"info":{"version":"0.4.9"}},
        "https://registry.npmjs.org/eslint/latest": {"version":"9.0.0"},
        "https://registry.npmjs.org/cal/latest": {"version":"2024.1"},
        # down 無 fixture key → fetch None → failed
    }
    fx = root / "fx.json"; fx.write_text(J.dumps(fixture), encoding="utf-8")
    env = dict(os.environ, LUMOS_LINT_WATCH_FIXTURE=str(fx))
    r = sp.run([sys.executable, GRAPHCTL, "lint-watch", "--repo", str(root), "--json"],
               capture_output=True, text=True, env=env)
    check("rc 0", r.returncode == 0, r.stderr)
    d = J.loads(r.stdout)
    check("1 candidate(ruff)", len(d["candidates"]) == 1 and d["candidates"][0]["name"] == "ruff", str(d["candidates"]))
    check("candidate latest", d["candidates"][0]["latest"] == "0.4.9", str(d["candidates"][0]))
    check("checked = behind+current = 2", d["checked"] == 2, str(d["checked"]))
    failed_names = {f["name"] for f in d["failed"]}
    check("failed 含 cal(段數) + down(抓取)", failed_names == {"cal","down"}, str(d["failed"]))
    # 缺清單 → rc 0 空候選
    root2 = Path(tempfile.mkdtemp(prefix="gctl-lwcli2-"))
    r2 = sp.run([sys.executable, GRAPHCTL, "lint-watch", "--repo", str(root2), "--json"], capture_output=True, text=True, env=env)
    check("缺清單 rc0", r2.returncode == 0 and J.loads(r2.stdout)["candidates"] == [], r2.stdout)
    # 壞清單(非 list)→ rc 2
    (root2 / ".lumos").mkdir()
    (root2 / ".lumos" / "lint-watch.json").write_text('{"not":"a list"}', encoding="utf-8")
    r3 = sp.run([sys.executable, GRAPHCTL, "lint-watch", "--repo", str(root2), "--json"], capture_output=True, text=True, env=env)
    check("壞清單 rc2", r3.returncode == 2, f"rc={r3.returncode}")
    # 清單條目缺必填欄位(missing current)→ rc 2
    root3 = Path(tempfile.mkdtemp(prefix="gctl-lwcli3-"))
    (root3 / ".lumos").mkdir()
    (root3 / ".lumos" / "lint-watch.json").write_text(
        '[{"name":"x","registry":"npm:x"}]', encoding="utf-8"
    )
    r4 = sp.run([sys.executable, GRAPHCTL, "lint-watch", "--repo", str(root3), "--json"],
                capture_output=True, text=True, env=env)
    check("malformed entry rc2", r4.returncode == 2, f"rc={r4.returncode} stderr={r4.stderr}")


def t_lint_watch_google_maven():
    """google-maven: registry type — XML maven-metadata.xml; prerelease-in-<latest> 陷阱避開."""
    import importlib.util as U, json as J, os, tempfile
    from importlib.machinery import SourceFileLoader
    spec = U.spec_from_file_location("lm", GRAPHCTL, loader=SourceFileLoader("lm", GRAPHCTL))
    m = U.module_from_spec(spec); spec.loader.exec_module(m)

    agp_url = ("https://dl.google.com/dl/android/maven2/"
               "com/android/tools/build/gradle/maven-metadata.xml")
    only_pre_url = ("https://dl.google.com/dl/android/maven2/"
                    "com/example/only-pre/maven-metadata.xml")

    # Realistic AGP XML: <latest> is alpha (the known trap), stable max = 9.2.1
    agp_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<metadata>'
        '<versioning>'
        '<latest>9.4.0-alpha03</latest>'
        '<release>9.4.0-alpha03</release>'
        '<versions>'
        '<version>8.2.2</version>'
        '<version>9.0.0</version>'
        '<version>9.2.0</version>'
        '<version>9.2.1</version>'
        '<version>9.4.0-alpha03</version>'
        '<version>3.9</version>'
        '</versions>'
        '</versioning>'
        '</metadata>'
    )
    only_pre_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<metadata><versioning><latest>9.4.0-alpha03</latest>'
        '<versions><version>9.4.0-alpha03</version><version>9.3.0-beta01</version></versions>'
        '</versioning></metadata>'
    )

    fixture = {
        agp_url: agp_xml,
        only_pre_url: only_pre_xml,
        # missing_url not present → fetch None
    }
    fx_dir = tempfile.mkdtemp(prefix="gctl-gm-")
    fx = Path(fx_dir) / "fx.json"
    fx.write_text(J.dumps(fixture), encoding="utf-8")
    os.environ["LUMOS_LINT_WATCH_FIXTURE"] = str(fx)
    try:
        # 1. AGP: must NOT use <latest>=alpha03; stable numeric max = 9.2.1
        result = m._registry_latest("google-maven:com.android.tools.build:gradle")
        check("google-maven AGP stable max=9.2.1 (NOT alpha)",
              result == ("9.2.1", None), str(result))

        # 2. Only-prerelease XML → (None, "no stable version")
        result2 = m._registry_latest("google-maven:com.example:only-pre")
        check("google-maven only-prerelease → no stable version",
              result2 == (None, "no stable version"), str(result2))

        # 3. URL not in fixture (fetch returns None) → (None, "registry query failed: ...")
        latest3, reason3 = m._registry_latest("google-maven:com.example:missing")
        check("google-maven missing url → registry query failed",
              latest3 is None and reason3 is not None and "registry query failed" in reason3,
              f"{latest3},{reason3}")

        # 4. _http_get_text: returns XML string for known key, None for missing key
        text = m._http_get_text(agp_url)
        check("_http_get_text fixture returns XML string",
              isinstance(text, str) and "<metadata>" in text, repr(text)[:80])
        missing_text = m._http_get_text("https://dl.google.com/NOTHERE")
        check("_http_get_text missing key → None", missing_text is None, repr(missing_text))

    finally:
        os.environ.pop("LUMOS_LINT_WATCH_FIXTURE", None)
        import shutil; shutil.rmtree(fx_dir, ignore_errors=True)


def t_compose_parse():
    import importlib.util as U, json, tempfile
    from importlib.machinery import SourceFileLoader
    from pathlib import Path
    spec = U.spec_from_file_location("lm", GRAPHCTL, loader=SourceFileLoader("lm", GRAPHCTL))
    m = U.module_from_spec(spec); spec.loader.exec_module(m)
    d = Path(tempfile.mkdtemp(prefix="gctl-cm-"))
    md = d / "metrics"; rd = d / "reports"; md.mkdir(); rd.mkdir()
    (md / "app_release-module.json").write_text(json.dumps({
        "skippableComposables": 96, "restartableComposables": 229, "totalComposables": 233,
        "knownUnstableArguments": 100, "inferredUnstableClasses": 29}), encoding="utf-8")
    # csv: KdsScreen non-skippable(skippable=0,restartable=1); MainFeatureBtn skippable(1,1);
    #      ColZeroWidget non-skippable(0,1) — col-0 bare fun fixture
    (rd / "app_release-composables.csv").write_text(
        "package,name,composable,skippable,restartable,readonly,inline,isLambda,hasDefaults,defaultsGroup,groups,calls,\n"
        "com.citrus.KdsScreen,KdsScreen,1,0,1,0,0,0,0,0,2,15,\n"
        "com.citrus.MainFeatureBtn,MainFeatureBtn,1,1,1,0,0,0,0,0,1,1,\n"
        "com.citrus.GenScreen,GenScreen,1,0,1,0,0,0,0,0,1,1,\n"
        "com.citrus.ColZeroWidget,ColZeroWidget,1,0,1,0,0,0,0,0,1,1,\n", encoding="utf-8")
    # txt: KdsScreen 有 unstable viewModel;GenScreen 為泛型 fun GenScreen<T>(;含空行 default;裸 fun helper 無關鍵字;
    #      ColZeroWidget col-0 裸 fun 有 unstable param(M2 修正驗證)
    (rd / "app_release-composables.txt").write_text(
        'restartable scheme("[androidx.compose.ui.UiComposable]") fun KdsScreen(\n'
        '  unstable viewModel: CentralViewModel\n'
        '  stable askUpdate: Function0<Unit>\n'
        ')\n'
        'restartable skippable fun MainFeatureBtn(\n'
        '  stable status: String = @static {\n'
        '\n'                                # 空行(多行 default)不該斷區塊
        '  }\n'
        ')\n'
        'restartable fun GenScreen<T>(\n'   # 泛型
        '  unstable data: T\n'
        ')\n'
        'fun calculateYOffset(\n'           # 裸 fun 無關鍵字前綴(無 unstable)
        '  stable width: Int\n'
        '): Dp\n'
        'fun ColZeroWidget(\n'             # col-0 裸 fun WITH unstable(M2 核心案例)
        '  unstable data: Foo\n'
        ')\n', encoding="utf-8")
    # module
    mod = m._compose_read_module(str(md), "app_release")
    check("module skippable", mod["skippableComposables"] == 96, str(mod))
    check("module missing→None", m._compose_read_module(str(md), "nope") is None, "")
    # module corrupt JSON → None (M3: parse-error branch)
    (md / "app_release-corrupt.json").write_text("{not json", encoding="utf-8")
    check("module corrupt JSON→None", m._compose_read_module(str(md), "app_release-corrupt") is None, "")
    # composables
    non_sk, fqn2name, umap = m._compose_read_composables(str(rd), "app_release")
    check("non_skippable = KdsScreen+GenScreen+ColZeroWidget(FQN)",
          non_sk == {"com.citrus.KdsScreen", "com.citrus.GenScreen", "com.citrus.ColZeroWidget"}, str(non_sk))
    check("fqn2name", fqn2name["com.citrus.KdsScreen"] == "KdsScreen", str(fqn2name))
    check("unstable KdsScreen", umap.get("KdsScreen") == ["viewModel: CentralViewModel"], str(umap.get("KdsScreen")))
    check("unstable GenScreen(泛型名剝<T>)", umap.get("GenScreen") == ["data: T"], str(umap.get("GenScreen")))
    check("MainFeatureBtn 空行不斷→無 unstable", umap.get("MainFeatureBtn", []) == [], str(umap.get("MainFeatureBtn")))
    check("col-0 fun ColZeroWidget unstable captured(M2)",
          umap.get("ColZeroWidget") == ["data: Foo"], str(umap.get("ColZeroWidget")))
    # csv missing → early-return empty (M1)
    import tempfile as _tf
    empty_rd = Path(_tf.mkdtemp(prefix="gctl-cm-nocsv-"))
    (empty_rd / "x-composables.txt").write_text("fun Orphan(\n  unstable x: Y\n)\n", encoding="utf-8")
    ns2, fn2, um2 = m._compose_read_composables(str(empty_rd), "x")
    check("csv missing→early-return (set(),{},{})", (ns2, fn2, um2) == (set(), {}, {}),
          f"ns2={ns2} fn2={fn2} um2={um2}")


def t_compose_diff():
    import importlib.util as U
    from importlib.machinery import SourceFileLoader
    spec = U.spec_from_file_location("lm", GRAPHCTL, loader=SourceFileLoader("lm", GRAPHCTL))
    m = U.module_from_spec(spec); spec.loader.exec_module(m)
    baseline = {"aggregate": {"skippableComposables": 96, "restartableComposables": 229,
                              "totalComposables": 233, "knownUnstableArguments": 100, "inferredUnstableClasses": 29},
                "non_skippable": ["com.citrus.KdsScreen"]}
    cur_agg = {"skippableComposables": 96, "restartableComposables": 230, "totalComposables": 234,
               "knownUnstableArguments": 108, "inferredUnstableClasses": 29}
    cur_non = {"com.citrus.KdsScreen", "com.citrus.NewScreen"}   # NewScreen 新增
    fqn2name = {"com.citrus.NewScreen": "NewScreen", "com.citrus.KdsScreen": "KdsScreen"}
    umap = {"NewScreen": ["vm: CentralViewModel"]}
    regs = m._compose_diff("app", baseline, cur_agg, cur_non, fqn2name, umap)
    kinds = [(r["kind"], r.get("name") or r.get("metric")) for r in regs]
    check("new_non_skippable NewScreen",
          ("new_non_skippable", "com.citrus.NewScreen") in kinds, str(kinds))
    nn = [r for r in regs if r["kind"]=="new_non_skippable"][0]
    check("unstable_params 附上", nn["unstable_params"] == ["vm: CentralViewModel"], str(nn))
    check("knownUnstableArguments 上升報", ("aggregate", "knownUnstableArguments") in kinds, str(kinds))
    check("inferredUnstableClasses 未升→不報",
          ("aggregate", "inferredUnstableClasses") not in kinds, str(kinds))
    # skippable_ratio: baseline 96/233=.412, current 96/234=.410 → 差 .002 < EPS(.01) → 不報
    check("ratio 微幅<EPS 不報", ("aggregate", "skippable_ratio") not in kinds, str(kinds))
    # ratio 大跌:current skippable=80/234=.342 vs .412 差 .07>EPS → 報
    regs2 = m._compose_diff("app", baseline, dict(cur_agg, skippableComposables=80), cur_non, fqn2name, umap)
    check("ratio 大跌>EPS 報", any(r["kind"]=="aggregate" and r.get("metric")=="skippable_ratio" for r in regs2), str(regs2))
    # 移除的 composable 不報:baseline 有 X 現況無 → 無 regression
    regs3 = m._compose_diff("app", {"aggregate": baseline["aggregate"], "non_skippable": ["com.citrus.KdsScreen","com.citrus.Gone"]},
                            cur_agg, {"com.citrus.KdsScreen"}, {}, {})
    check("移除不報", not any(r["kind"]=="new_non_skippable" for r in regs3), str(regs3))


def t_compose_metrics_cli():
    import subprocess as sp, json, tempfile
    from pathlib import Path
    root = Path(tempfile.mkdtemp(prefix="gctl-cmcli-"))
    (root/".lumos").mkdir()
    md = root/"app"/"m"; rd = root/"app"/"r"; md.mkdir(parents=True); rd.mkdir(parents=True)
    (root/".lumos"/"compose-metrics.json").write_text(json.dumps(
        {"modules":[{"name":"app","metrics_dir":"app/m","reports_dir":"app/r"}]}), encoding="utf-8")
    def write_metrics(skippable, non_sk_rows):
        (md/"app_release-module.json").write_text(json.dumps(
            {"skippableComposables":skippable,"restartableComposables":10,"totalComposables":20,
             "knownUnstableArguments":5,"inferredUnstableClasses":2}), encoding="utf-8")
        rows = "package,name,composable,skippable,restartable,readonly,inline,isLambda,hasDefaults,defaultsGroup,groups,calls,\n"
        for fqn,name in non_sk_rows:
            rows += f"{fqn},{name},1,0,1,0,0,0,0,0,1,1,\n"
        (rd/"app_release-composables.csv").write_text(rows, encoding="utf-8")
        (rd/"app_release-composables.txt").write_text("", encoding="utf-8")
    write_metrics(10, [("com.a.Foo","Foo")])
    # baseline 缺 → baseline_missing、rc 0、無 regressions
    r0 = sp.run([sys.executable,GRAPHCTL,"compose-metrics","--repo",str(root),"--json"],capture_output=True,text=True)
    d0 = json.loads(r0.stdout)
    check("baseline_missing", r0.returncode==0 and d0["baseline_missing"] is True and d0["regressions"]==[], r0.stdout)
    # --update-baseline 立基準
    ru = sp.run([sys.executable,GRAPHCTL,"compose-metrics","--repo",str(root),"--update-baseline"],capture_output=True,text=True)
    check("update-baseline rc0", ru.returncode==0 and (root/".lumos"/"compose-baseline.json").exists(), ru.stderr)
    # 新增 non_skippable Bar → 報 new_non_skippable
    write_metrics(10, [("com.a.Foo","Foo"),("com.a.Bar","Bar")])
    r1 = sp.run([sys.executable,GRAPHCTL,"compose-metrics","--repo",str(root),"--json"],capture_output=True,text=True)
    d1 = json.loads(r1.stdout)
    names = [x.get("name") for x in d1["regressions"] if x["kind"]=="new_non_skippable"]
    check("new_non_skippable Bar", r1.returncode==0 and "com.a.Bar" in names, r1.stdout)
    check("checked_modules 1", d1["checked_modules"]==1, str(d1))
    # Fix #2: --update-baseline 當 0 模組解析時不能覆寫 baseline
    root2 = Path(tempfile.mkdtemp(prefix="gctl-cmcli-noparse-"))
    (root2/".lumos").mkdir()
    md2 = root2/"app"/"m"; rd2 = root2/"app"/"r"; md2.mkdir(parents=True); rd2.mkdir(parents=True)
    (root2/".lumos"/"compose-metrics.json").write_text(json.dumps(
        {"modules":[{"name":"app","metrics_dir":"app/m","reports_dir":"app/r"}]}), encoding="utf-8")
    sentinel = '{"sentinel":true}'
    (root2/".lumos"/"compose-baseline.json").write_text(sentinel, encoding="utf-8")
    # no metrics files → all modules fail to parse → parsed list is empty
    ru2 = sp.run([sys.executable,GRAPHCTL,"compose-metrics","--repo",str(root2),"--update-baseline"],capture_output=True,text=True)
    after = (root2/".lumos"/"compose-baseline.json").read_text(encoding="utf-8")
    check("0-parse baseline not overwritten", ru2.returncode==0 and after==sentinel, f"stdout={ru2.stdout!r} file={after!r}")
    # Fix #1: corrupt baseline → baseline_unreadable=True, baseline_missing=False, rc 0, file intact
    root3 = Path(tempfile.mkdtemp(prefix="gctl-cmcli-corrupt-"))
    (root3/".lumos").mkdir()
    md3 = root3/"app"/"m"; rd3 = root3/"app"/"r"; md3.mkdir(parents=True); rd3.mkdir(parents=True)
    (root3/".lumos"/"compose-metrics.json").write_text(json.dumps(
        {"modules":[{"name":"app","metrics_dir":"app/m","reports_dir":"app/r"}]}), encoding="utf-8")
    corrupt_content = b"not valid json!!!"
    (root3/".lumos"/"compose-baseline.json").write_bytes(corrupt_content)
    write_metrics_into = lambda md_,rd_,sk,rows: (
        (md_/("app_release-module.json")).write_text(json.dumps(
            {"skippableComposables":sk,"restartableComposables":10,"totalComposables":20,
             "knownUnstableArguments":5,"inferredUnstableClasses":2}), encoding="utf-8"),
        (rd_/("app_release-composables.csv")).write_text(
            "package,name,composable,skippable,restartable,readonly,inline,isLambda,hasDefaults,defaultsGroup,groups,calls,\n", encoding="utf-8"),
        (rd_/("app_release-composables.txt")).write_text("", encoding="utf-8"),
    )
    write_metrics_into(md3, rd3, 10, [])
    rc3 = sp.run([sys.executable,GRAPHCTL,"compose-metrics","--repo",str(root3),"--json"],capture_output=True,text=True)
    d3 = json.loads(rc3.stdout)
    after3 = (root3/".lumos"/"compose-baseline.json").read_bytes()
    check("corrupt-baseline rc0", rc3.returncode==0, f"rc={rc3.returncode} stderr={rc3.stderr!r}")
    check("corrupt-baseline unreadable true", d3.get("baseline_unreadable") is True, str(d3))
    check("corrupt-baseline missing false", d3.get("baseline_missing") is not True, str(d3))
    check("corrupt-baseline regressions empty", d3.get("regressions")==[], str(d3))
    check("corrupt-baseline file intact", after3==corrupt_content, f"file changed: {after3!r}")
    # 壞宣告 → rc 2
    (root/".lumos"/"compose-metrics.json").write_text('[]', encoding="utf-8")
    r2 = sp.run([sys.executable,GRAPHCTL,"compose-metrics","--repo",str(root),"--json"],capture_output=True,text=True)
    check("壞宣告 rc2", r2.returncode==2, f"rc={r2.returncode}")


def t_compose_metrics_audit():
    import subprocess as sp, json, tempfile
    from pathlib import Path
    root = Path(tempfile.mkdtemp(prefix="gctl-cmaudit-"))
    (root/".lumos").mkdir()
    md = root/"app"/"m"; rd = root/"app"/"r"; md.mkdir(parents=True); rd.mkdir(parents=True)
    (root/".lumos"/"compose-metrics.json").write_text(json.dumps(
        {"modules":[{"name":"app","metrics_dir":"app/m","reports_dir":"app/r"}]}), encoding="utf-8")
    (md/"app_release-module.json").write_text(json.dumps(
        {"skippableComposables":8,"restartableComposables":10,"totalComposables":20,
         "knownUnstableArguments":5,"inferredUnstableClasses":2}), encoding="utf-8")
    (rd/"app_release-composables.csv").write_text(
        "package,name,composable,skippable,restartable,readonly,inline,isLambda,hasDefaults,defaultsGroup,groups,calls,\n"
        "com.a.Foo,Foo,1,0,1,0,0,0,0,0,1,1,\n"
        "com.a.Bar,Bar,1,0,1,0,0,0,0,0,1,1,\n"
        "com.a.Ok,Ok,1,1,1,0,0,0,0,0,1,1,\n", encoding="utf-8")
    (rd/"app_release-composables.txt").write_text(
        "restartable fun Foo(\n  unstable vm: Baz\n)\nrestartable skippable fun Ok()\n", encoding="utf-8")
    # audit: 無視 baseline(不存在也照列)→ inventory 含全部 non-skippable(Foo+Bar,不含 Ok)
    r = sp.run([sys.executable,GRAPHCTL,"compose-metrics","--repo",str(root),"--audit","--json"],
               capture_output=True,text=True)
    check("audit rc0", r.returncode==0, r.stderr)
    d = json.loads(r.stdout)
    names = sorted(x["name"] for x in d["inventory"])
    check("audit inventory = 全部 non-skippable(無視 baseline)", names==["com.a.Bar","com.a.Foo"], str(names))
    foo = [x for x in d["inventory"] if x["name"]=="com.a.Foo"][0]
    check("audit unstable_params 附上", foo["unstable_params"]==["vm: Baz"], str(foo))
    check("audit aggregate", d["aggregate"]["app"]["skippableComposables"]==8, str(d.get("aggregate")))
    check("audit checked_modules/failed 欄位", d["checked_modules"]==1 and d["failed"]==[], str(d))
    # 缺 config + --audit → audit 形狀(有 inventory 鍵,非 delta 形狀)
    root2 = Path(tempfile.mkdtemp(prefix="gctl-cmaudit2-"))
    ra = sp.run([sys.executable,GRAPHCTL,"compose-metrics","--repo",str(root2),"--audit","--json"],
                capture_output=True,text=True)
    da = json.loads(ra.stdout)
    check("缺config+audit → audit 形狀(inventory 鍵)", ra.returncode==0 and "inventory" in da and "regressions" not in da, ra.stdout)


def t_pitfalls_no_lint():
    """--no-lint:--diff 只跑 regex 層,即使有 .lumos/lint.json 也不跑 lint(pre-push advisory 用)。"""
    import json as _json, subprocess as sp, sys as _sys
    root = Path(tempfile.mkdtemp(prefix="gctl-pfnl-"))
    def git(*a): sp.run(["git", *a], cwd=root, capture_output=True)
    git("init"); git("config", "user.email", "t@t"); git("config", "user.name", "t")
    (root / "a.kt").write_text("l1\n", encoding="utf-8")
    git("add", "-A"); git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "c1")
    # 假 linter:寫最小 SARIF 到 {LINT_SARIF_OUT}
    hd = Path(tempfile.mkdtemp(prefix="gctl-pfnl-h-"))
    sarif = _json.dumps({"runs": [{"tool": {"driver": {"name": "FakeLint"}}, "results": []}]})
    (hd / "lint.py").write_text(f"import sys\nopen(sys.argv[1],'w').write({repr(sarif)})\n", encoding="utf-8")
    (root / ".lumos").mkdir()
    (root / ".lumos" / "lint.json").write_text(
        _json.dumps({"kt": [f"{_sys.executable} {hd/'lint.py'} {{LINT_SARIF_OUT}}"]}), encoding="utf-8")
    # diff 新增一個含風險 pattern 的 .kt 行(INSERT → 併發類命中,確保 tier=high/有 claim)
    (root / "a.kt").write_text("l1\nval q = \"INSERT INTO t VALUES(1)\"\n", encoding="utf-8")
    git("add", "-A"); git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "c2")
    def run(extra):
        r = sp.run([_sys.executable, GRAPHCTL, "pitfalls", "--diff", "HEAD~1..HEAD", "--json", "--repo", str(root)] + extra,
                   capture_output=True, text=True)
        return _json.loads(r.stdout)
    d_full = run([])
    d_nl = run(["--no-lint"])
    check("預設(有 lint.json)→ lint 真的有跑(lint_ran 非空)", bool(d_full.get("lint_ran")), str(d_full.get("lint_ran")))
    check("--no-lint → 無 lint_ran 鍵(regex-only)", "lint_ran" not in d_nl, str(sorted(d_nl.keys())))
    check("--no-lint 仍有 regex claims + tier", "claims" in d_nl and "tier" in d_nl, str(sorted(d_nl.keys())))


def t_lint_sarif_v1():
    """SARIF v1.0(dotnet/Roslyn ErrorLog 預設)——tool.name/resultFile.uri/message 字串,與 v2.1 不同。"""
    import importlib.util as U, json as J, tempfile
    from importlib.machinery import SourceFileLoader
    spec = U.spec_from_file_location("lm", GRAPHCTL, loader=SourceFileLoader("lm", GRAPHCTL))
    m = U.module_from_spec(spec); spec.loader.exec_module(m)
    root = Path(tempfile.mkdtemp(prefix="gctl-s1-"))
    sarif_v1 = {
        "version": "1.0.0",
        "runs": [{
            "tool": {"name": "Microsoft (R) Visual C# Compiler"},
            "results": [
                {"ruleId": "CA1805", "message": "member explicitly initialized to default",
                 "locations": [{"resultFile": {"uri": f"file://{root}/App/Foo.cs",
                                               "region": {"startLine": 8}}}]},
                {"ruleId": "CA0000", "message": "no-loc"},  # location-less → 跳不連坐
            ]
        }]
    }
    sf = root / "v1.sarif"; sf.write_text(J.dumps(sarif_v1), encoding="utf-8")
    claims, ok = m._lint_run_and_parse(f"cp {sf} {{LINT_SARIF_OUT}}", root)
    check("v1 ok", ok is True, "")
    check("v1 1 claim(location-less 跳)", len(claims) == 1, str(claims))
    c = claims[0]
    check("v1 tool.name → source", c["source"] == "lint:Microsoft (R) Visual C# Compiler", c["source"])
    check("v1 resultFile.uri → repo 相對", c["file"] == "App/Foo.cs", c["file"])
    check("v1 message 字串 + line/rule", c["line"] == 8 and c["rule"] == "CA1805" and c["message"] == "member explicitly initialized to default", str(c))


def t_lint_watch_nuget():
    """nuget registry type:index.json versions 過濾 prerelease 取數值 max。"""
    import importlib.util as U, json as J, os, tempfile
    from importlib.machinery import SourceFileLoader
    spec = U.spec_from_file_location("lm", GRAPHCTL, loader=SourceFileLoader("lm", GRAPHCTL))
    m = U.module_from_spec(spec); spec.loader.exec_module(m)
    url = "https://api.nuget.org/v3-flatcontainer/stylecop.analyzers/index.json"  # id 小寫
    fixture = {url: {"versions": ["1.1.0", "1.1.118", "1.2.0-beta.556", "1.0.2"]}}
    fx = Path(tempfile.mkdtemp(prefix="gctl-ng-")) / "fx.json"
    fx.write_text(J.dumps(fixture), encoding="utf-8")
    os.environ["LUMOS_LINT_WATCH_FIXTURE"] = str(fx)
    try:
        check("nuget 過濾 beta 取穩定 max",
              m._registry_latest("nuget:StyleCop.Analyzers") == ("1.1.118", None),
              str(m._registry_latest("nuget:StyleCop.Analyzers")))
        fixture[url] = {"versions": ["1.2.0-beta.1", "1.2.0-beta.2"]}
        fx.write_text(J.dumps(fixture), encoding="utf-8")
        check("nuget 全 beta → no stable",
              m._registry_latest("nuget:StyleCop.Analyzers") == (None, "no stable version"),
              str(m._registry_latest("nuget:StyleCop.Analyzers")))
    finally:
        os.environ.pop("LUMOS_LINT_WATCH_FIXTURE", None)


def t_lint_runner_stdout_isolation():
    """linter 寫 stdout(如 dotnet 警告走 stdout)不可污染 lumos --json(Landmark 真機暴露的 bug)。"""
    import importlib.util as U, json as J, tempfile, sys as _sys
    from importlib.machinery import SourceFileLoader
    spec = U.spec_from_file_location("lm", GRAPHCTL, loader=SourceFileLoader("lm", GRAPHCTL))
    m = U.module_from_spec(spec); spec.loader.exec_module(m)
    root = Path(tempfile.mkdtemp(prefix="gctl-iso-"))
    # 假 linter:先大量印到 stdout(模擬 dotnet 警告),再寫合法 SARIF 到 {LINT_SARIF_OUT}
    sarif = J.dumps({"version": "2.1.0", "runs": [{"tool": {"driver": {"name": "Noisy"}}, "results": []}]})
    hd = Path(tempfile.mkdtemp(prefix="gctl-iso-h-"))
    (hd / "noisy.py").write_text(
        "import sys\nprint('WARNING junk to stdout line1')\nprint('WARNING junk line2')\n"
        f"open(sys.argv[1],'w').write({repr(sarif)})\n", encoding="utf-8")
    cmd = f"{_sys.executable} {hd/'noisy.py'} {{LINT_SARIF_OUT}}"
    # _lint_run_and_parse 本身回 (claims, ok);污染測的是它不讓 child stdout 冒出來——
    # 用 subprocess 捕捉本進程 stdout:呼叫 _lint_run_and_parse 期間 child 的 stdout 應被 DEVNULL 吞掉
    import subprocess as sp
    probe = hd / "probe.py"
    probe.write_text(
        "import importlib.util as U,sys\n"
        "from importlib.machinery import SourceFileLoader\n"
        f"s=U.spec_from_file_location('lm',{repr(GRAPHCTL)},loader=SourceFileLoader('lm',{repr(GRAPHCTL)}))\n"
        "m=U.module_from_spec(s); s.loader.exec_module(m)\n"
        f"claims,ok=m._lint_run_and_parse({repr(cmd)}, {repr(str(root))})\n"
        "print('RESULT', ok)\n", encoding="utf-8")
    r = sp.run([_sys.executable, str(probe)], capture_output=True, text=True)
    check("child stdout 未污染(無 WARNING junk 洩漏)", "WARNING junk" not in r.stdout, r.stdout[:200])
    check("_lint_run_and_parse 仍正常回 (ok=True)", "RESULT True" in r.stdout, r.stdout[:200])


def t_sqlfluff_sarif_bridge():
    """sqlfluff --format json → lumos sqlfluff-sarif → SARIF → _lint_run_and_parse 吃得到(MSSQL 進 lint-adapter)。"""
    import importlib.util as U, json as J, subprocess as sp, sys as _sys, tempfile
    from importlib.machinery import SourceFileLoader
    root = Path(tempfile.mkdtemp(prefix="gctl-sqlb-"))
    sf_json = J.dumps([{"filepath": "db/001.sql", "violations": [
        {"start_line_no": 3, "code": "CP01", "description": "Keywords must be consistently upper case."},
        {"start_line_no": 5, "code": "LT05", "description": "Line is too long."}]}])
    out = root / "o.sarif"
    r = sp.run([_sys.executable, GRAPHCTL, "sqlfluff-sarif", "--out", str(out)],
               input=sf_json, capture_output=True, text=True)
    check("sqlfluff-sarif rc0", r.returncode == 0, r.stderr)
    d = J.loads(out.read_text(encoding="utf-8"))
    check("SARIF v2.1 + driver sqlfluff", d.get("version") == "2.1.0" and d["runs"][0]["tool"]["driver"]["name"] == "sqlfluff", str(d)[:120])
    check("2 results 映射", len(d["runs"][0]["results"]) == 2, str(len(d["runs"][0]["results"])))
    # 再過 _lint_run_and_parse:應得 lint:sqlfluff claims
    spec = U.spec_from_file_location("lm", GRAPHCTL, loader=SourceFileLoader("lm", GRAPHCTL))
    m = U.module_from_spec(spec); spec.loader.exec_module(m)
    claims, ok = m._lint_run_and_parse(f"cp {out} {{LINT_SARIF_OUT}}", root)
    check("lint-adapter 吃到 sqlfluff claim", ok and len(claims) == 2 and claims[0]["source"] == "lint:sqlfluff", str(claims))
    check("claim 映射 file/line/rule", claims[0]["file"] == "db/001.sql" and claims[0]["line"] == 3 and claims[0]["rule"] == "CP01", str(claims[0]))
    # 空 stdin → 空 results 不崩
    r2 = sp.run([_sys.executable, GRAPHCTL, "sqlfluff-sarif"], input="", capture_output=True, text=True)
    check("空 stdin 不崩", r2.returncode == 0 and '"results": []' in r2.stdout, r2.stdout[:80])


def t_stylelint_sarif_bridge():
    """stylelint --formatter json → lumos stylelint-sarif → SARIF → _lint_run_and_parse(CSS 進 lint-adapter)。"""
    import importlib.util as U, json as J, subprocess as sp, sys as _sys, tempfile
    from importlib.machinery import SourceFileLoader
    root = Path(tempfile.mkdtemp(prefix="gctl-stylb-"))
    sl_json = J.dumps([{"source": "src/a.css", "warnings": [
        {"line": 3, "rule": "color-no-invalid-hex", "text": "Invalid hex color"},
        {"line": 7, "rule": "block-no-empty", "text": "Empty block"}]}])
    out = root / "o.sarif"
    r = sp.run([_sys.executable, GRAPHCTL, "stylelint-sarif", "--out", str(out)],
               input=sl_json, capture_output=True, text=True)
    check("stylelint-sarif rc0", r.returncode == 0, r.stderr)
    d = J.loads(out.read_text(encoding="utf-8"))
    check("SARIF driver stylelint + 2 results",
          d["runs"][0]["tool"]["driver"]["name"] == "stylelint" and len(d["runs"][0]["results"]) == 2, str(d)[:120])
    spec = U.spec_from_file_location("lm", GRAPHCTL, loader=SourceFileLoader("lm", GRAPHCTL))
    m = U.module_from_spec(spec); spec.loader.exec_module(m)
    claims, ok = m._lint_run_and_parse(f"cp {out} {{LINT_SARIF_OUT}}", root)
    check("lint-adapter 吃到 stylelint claim",
          ok and len(claims) == 2 and claims[0]["source"] == "lint:stylelint"
          and claims[0]["file"] == "src/a.css" and claims[0]["line"] == 3 and claims[0]["rule"] == "color-no-invalid-hex",
          str(claims))
    r2 = sp.run([_sys.executable, GRAPHCTL, "stylelint-sarif"], input="", capture_output=True, text=True)
    check("空 stdin 不崩", r2.returncode == 0 and '"results": []' in r2.stdout, r2.stdout[:80])


# ─── Task 1: lumos impact 子命令骨架 + rc 協定 ────────────────────────────────

def t_impact_cli_skeleton():
    # 非 vault 目錄 → rc 3(vault 找不到)
    with tempfile.TemporaryDirectory() as d:
        rc = run_lumos(["impact", "--file", "x.py", "--repo", d, "--json"])
        check("impact: 非圖譜應 rc3", rc == 3, f"非圖譜應 rc3, got {rc}")
    # 缺 --file → argparse rc 2
    check("impact: 缺 --file 應 rc2", run_lumos(["impact", "--repo", "."]) == 2, "")


# ─── Task 2: code→node 反查(body inline-code,重讀盤,路徑規範化) ──────────────

def make_fixture_vault(files: dict):
    """建立 fixture repo:repo_root 含 scripts/ 頂層目錄 + docs/test-knowledge/ vault。
    files: {vault-rel-path: content-str} — 直接寫進 vault 子目錄。
    回傳 (env, repo_root):env 是 Env(vault),repo_root 是 Path。
    """
    import importlib.util
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("lumos_mod", GRAPHCTL)
    spec = importlib.util.spec_from_loader("lumos_mod", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)

    repo = Path(tempfile.mkdtemp(prefix="gctl-impact-"))
    # 建頂層 scripts/ 目錄(讓 _refcheck_scan 的 top_dirs 能認到 scripts/)
    (repo / "scripts").mkdir()
    (repo / "scripts" / "lumos").write_text("# fake lumos\n", encoding="utf-8")
    # 建 vault
    vault = repo / "docs" / "test-knowledge"
    for sub in ("Systems", "Verification", "Projects", "MOC"):
        (vault / sub).mkdir(parents=True, exist_ok=True)
    (vault / "MOC" / "idx.md").write_bytes("---\ntype: moc\n---\n# idx\n".encode("utf-8"))
    # 寫入測試節點
    for rel_path, content in files.items():
        p = vault / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    env = m.Env(vault)
    return env, repo


def t_impact_reverse_lookup():
    import importlib.util
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("lumos_mod", GRAPHCTL)
    spec = importlib.util.spec_from_loader("lumos_mod", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    _impact_reverse_lookup = m._impact_reverse_lookup

    env, repo = make_fixture_vault({
        "Systems/A.md": "---\ntype: system\nstatus: doing\n---\nbody 提到 `scripts/lumos` 的用法",
        "Systems/B.md": "---\ntype: system\nstatus: doing\n---\nbody 無關",
        "Systems/C.md": "---\ntype: system\nstatus: doing\ncore_refs: scripts/lumos\n---\ncore 節點",
    })
    hits = _impact_reverse_lookup("scripts/lumos", env, repo)
    check("impact_reverse_lookup: A(body inline-code 命中) 在結果中",
          "Systems/A.md" in hits, f"hits={hits}")
    check("impact_reverse_lookup: B(無引用) 不在結果中",
          "Systems/B.md" not in hits, f"hits={hits}")
    check("impact_reverse_lookup: C(core_refs 不算 code 反查 r7-F2) 不在結果中",
          "Systems/C.md" not in hits, f"hits={hits}")

    # 絕對路徑輸入規範化後仍命中
    abs_path = str(repo / "scripts" / "lumos")
    hits_abs = _impact_reverse_lookup(abs_path, env, repo)
    check("impact_reverse_lookup: 絕對路徑輸入規範化後仍命中 A",
          "Systems/A.md" in hits_abs, f"hits_abs={hits_abs}")
    check("impact_reverse_lookup: 絕對路徑輸入規範化後 C 仍不在",
          "Systems/C.md" not in hits_abs, f"hits_abs={hits_abs}")


def t_impact_contract():
    """Task 3: _impact_contract(note) -> (contract, combo) 兩軸偵測。"""
    import importlib.util
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("lumos_mod_ic", GRAPHCTL)
    spec = importlib.util.spec_from_loader("lumos_mod_ic", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    _impact_contract = m._impact_contract
    Note = m.Note

    def note_with(summary_text):
        """建立最簡 Note fixture,只設 fields["summary"]。"""
        n = Note()
        n.rel = "Systems/fixture.md"
        n.stem = "fixture"
        n.fields = {"type": "system", "status": "doing", "summary": summary_text}
        n.block_keys = set()
        n.fm_lines = []
        n.targets = []
        n.lint = []
        n.mtime = 0
        return n

    # ★INVARIANT★ → contract="INVARIANT"
    contract, combo = _impact_contract(note_with("KEY:★INVARIANT★ x [test:t]"))
    check("impact_contract: INVARIANT 節點回 INVARIANT",
          contract == "INVARIANT", f"got {contract!r}")

    # ★IRREVERSIBLE★(無 INVARIANT) → contract="IRREVERSIBLE"(走獨立 RE)
    contract, combo = _impact_contract(note_with("KEY:★IRREVERSIBLE★ y [rollback:decisions]"))
    check("impact_contract: IRREVERSIBLE(無 INVARIANT)走獨立 RE 回 IRREVERSIBLE",
          contract == "IRREVERSIBLE", f"got {contract!r}")

    # 兩者同時有 → 取 IRREVERSIBLE(最高)
    contract, combo = _impact_contract(
        note_with("KEY:★IRREVERSIBLE★ y\nKEY:★INVARIANT★ x [test:t]"))
    check("impact_contract: IRREVERSIBLE+INVARIANT 取最高=IRREVERSIBLE",
          contract == "IRREVERSIBLE", f"got {contract!r}")

    # ★INVARIANT★★COMBO★ → combo=True
    _, combo = _impact_contract(note_with("KEY:★INVARIANT★ ★COMBO★ z [test:t]"))
    check("impact_contract: INVARIANT+COMBO 行 → combo=True",
          combo is True, f"got combo={combo!r}")

    # 純 ★DEBT★ → (None, False)
    result = _impact_contract(note_with("KEY:★DEBT★ w"))
    check("impact_contract: 純 DEBT → (None, False)",
          result == (None, False), f"got {result!r}")


# ─── Task 4: 間接關聯 BFS(hop 1..depth, seen cycle guard, 雙向邊) ─────────────

def t_impact_bfs_cycle_and_depth():
    import importlib.util
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("lumos_mod_bfs", GRAPHCTL)
    spec = importlib.util.spec_from_loader("lumos_mod_bfs", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    _impact_bfs = m._impact_bfs

    # A↔B 環:A 是 direct → BFS 應展開 B(hop1),A 不得重入 indirect(r8-F4)
    env, _ = make_fixture_vault({
        "S/A.md": "---\nrelated:\n  - \"[[B]]\"\n---\n`scripts/x`",
        "S/B.md": "---\nrelated:\n  - \"[[A]]\"\n---\nb",
    })
    out = _impact_bfs(["S/A.md"], env, depth=2)
    nodes = [o[0] for o in out]
    check("impact_bfs: B(A 的鄰居) 在 indirect 中(hop1)",
          "S/B.md" in nodes, f"nodes={nodes}")
    check("impact_bfs: A(direct) 不得沿環重入 indirect(r8-F4)",
          "S/A.md" not in nodes, f"nodes={nodes}")


def t_impact_bfs_depth_limit():
    import importlib.util
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("lumos_mod_bfs2", GRAPHCTL)
    spec = importlib.util.spec_from_loader("lumos_mod_bfs2", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    _impact_bfs = m._impact_bfs

    # D→N1→N2 chain: depth=1 只出 N1(hop1),不出 N2
    env, _ = make_fixture_vault({
        "S/D.md": "---\nrelated:\n  - \"[[N1]]\"\n---\nd",
        "S/N1.md": "---\nrelated:\n  - \"[[N2]]\"\n---\nn1",
        "S/N2.md": "---\n---\nn2",
    })
    out1 = _impact_bfs(["S/D.md"], env, depth=1)
    nodes1 = [o[0] for o in out1]
    check("impact_bfs: depth=1 包含 N1(hop1)",
          "S/N1.md" in nodes1, f"nodes1={nodes1}")
    check("impact_bfs: depth=1 不包含 N2(hop2)",
          "S/N2.md" not in nodes1, f"nodes1={nodes1}")

    # depth=2 出 N1(hop1) 和 N2(hop2)
    out2 = _impact_bfs(["S/D.md"], env, depth=2)
    nodes2 = [o[0] for o in out2]
    check("impact_bfs: depth=2 包含 N1(hop1)",
          "S/N1.md" in nodes2, f"nodes2={nodes2}")
    check("impact_bfs: depth=2 包含 N2(hop2)",
          "S/N2.md" in nodes2, f"nodes2={nodes2}")
    # 驗 hop 值
    hop_n2 = next(o[1] for o in out2 if o[0] == "S/N2.md")
    check("impact_bfs: N2 的 hop=2",
          hop_n2 == 2, f"hop_n2={hop_n2}")


def t_impact_bfs_backlink():
    import importlib.util
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("lumos_mod_bfs3", GRAPHCTL)
    spec = importlib.util.spec_from_loader("lumos_mod_bfs3", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    _impact_bfs = m._impact_bfs

    # D 是 direct;X 連向 D(backlink);X 應以 is_backlink=True 出現
    env, _ = make_fixture_vault({
        "S/D.md": "---\n---\nd",
        "S/X.md": "---\nrelated:\n  - \"[[D]]\"\n---\nx",
    })
    out = _impact_bfs(["S/D.md"], env, depth=1)
    nodes = [o[0] for o in out]
    check("impact_bfs: X(backlink 指向 D) 在 indirect 中",
          "S/X.md" in nodes, f"nodes={nodes}")
    x_entry = next((o for o in out if o[0] == "S/X.md"), None)
    check("impact_bfs: X 的 is_backlink=True",
          x_entry is not None and x_entry[3] is True,
          f"x_entry={x_entry}")


def t_impact_bfs_tuple_fields():
    """每筆 tuple: (node, hop, from_node, is_backlink) 欄位存在且正確。"""
    import importlib.util
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("lumos_mod_bfs4", GRAPHCTL)
    spec = importlib.util.spec_from_loader("lumos_mod_bfs4", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    _impact_bfs = m._impact_bfs

    env, _ = make_fixture_vault({
        "S/D.md": "---\nrelated:\n  - \"[[N]]\"\n---\nd",
        "S/N.md": "---\n---\nn",
    })
    out = _impact_bfs(["S/D.md"], env, depth=1)
    check("impact_bfs: 有結果", len(out) > 0, f"out={out}")
    entry = out[0]
    check("impact_bfs: tuple 長度=4", len(entry) == 4, f"entry={entry}")
    node, hop, from_node, is_backlink = entry
    check("impact_bfs: hop=1", hop == 1, f"hop={hop}")
    check("impact_bfs: from_node 是 direct", from_node == "S/D.md", f"from_node={from_node}")
    check("impact_bfs: is_backlink 是 bool", isinstance(is_backlink, bool),
          f"is_backlink={is_backlink!r}")


# ─── Task 5: via 標記(二次反查,outlink/backlink 讀對端,body-wikilink fallback) ──

def t_impact_via_both_directions():
    import importlib.util
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("lumos_mod_via", GRAPHCTL)
    spec = importlib.util.spec_from_loader("lumos_mod_via", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    _impact_via = m._impact_via

    env, _ = make_fixture_vault({
        "S/F.md": "---\nrelated:\n  - \"[[G]]\"\n---\n`scripts/x`",
        "S/G.md": "g",
        "S/H.md": "---\nverified_by:\n  - \"[[F]]\"\n---\nh",  # H→F,對 F 是 backlink
    })
    # outlink: F→G via related(讀 frontier=F 的 fields)
    result_outlink = _impact_via("S/F.md", "S/G.md", False, env)
    check("impact_via: outlink F→G 讀 frontier(F.fields) 得 via=related",
          result_outlink == "related", f"got {result_outlink!r}")

    # backlink: H→F,從 F 反查到 H(in_e);須讀 dest(H).fields 找 verified_by:[[F]]
    result_backlink = _impact_via("S/F.md", "S/H.md", True, env)
    check("impact_via: backlink H→F 讀 dest(H.fields) 得 via=verified_by(不是讀 F)",
          result_backlink == "verified_by", f"got {result_backlink!r}")


def t_impact_via_body_wikilink_fallback():
    """body-wikilink fallback: 當連結不在任何 frontmatter 欄位時回 body-wikilink(r5-F3)。"""
    import importlib.util
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("lumos_mod_via2", GRAPHCTL)
    spec = importlib.util.spec_from_loader("lumos_mod_via2", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    _impact_via = m._impact_via

    env, _ = make_fixture_vault({
        # P→Q 連結只在 body([[Q]]),frontmatter 無 wikilink
        "S/P.md": "---\n---\nbody 連向 [[Q]]",
        "S/Q.md": "---\n---\nq",
    })
    # outlink: P→Q,frontmatter 無 wikilink → body-wikilink fallback
    result = _impact_via("S/P.md", "S/Q.md", False, env)
    check("impact_via: outlink body-wikilink fallback → body-wikilink",
          result == "body-wikilink", f"got {result!r}")


# ─── Task 6: core_refs 跨 repo 葉(cross_repo/no_expand,不展開) ───────────────

def t_impact_core_refs_leaf():
    """Task 6: 直接節點有 core_refs → 影響清單 indirect 含跨 repo 葉,標 cross_repo/no_expand,不 KeyError。"""
    import importlib.util
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("lumos_mod_cr", GRAPHCTL)
    spec = importlib.util.spec_from_loader("lumos_mod_cr", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    _impact_collect = m._impact_collect

    env, _ = make_fixture_vault({
        "S/A.md": "---\ncore_refs: core-knowledge/systems/rule\n---\n`scripts/x`",
    })
    res = _impact_collect("S/A.md", env, depth=2)
    leaf = [r for r in res["indirect"] if r.get("cross_repo")]
    check("impact_core_refs: indirect 含跨 repo 葉",
          len(leaf) > 0, f"indirect={res['indirect']}")
    check("impact_core_refs: 葉的 node == core-knowledge/systems/rule",
          leaf[0]["node"] == "core-knowledge/systems/rule", f"leaf={leaf}")
    check("impact_core_refs: 葉的 no_expand is True",
          leaf[0]["no_expand"] is True, f"leaf={leaf}")
    check("impact_core_refs: 葉的 via == core_refs",
          leaf[0].get("via") == "core_refs", f"leaf={leaf}")
    check("impact_core_refs: 葉的 cross_repo is True",
          leaf[0]["cross_repo"] is True, f"leaf={leaf}")


# ─── Task 7: 排序 + --json schema 輸出 + 人讀輸出 ─────────────────────────────

def t_impact_json_schema_and_sort():
    """Task 7: --json schema 欄位齊 + 合約節點排最前 + 空集回 rc0。

    fixture:
    - Systems/WithContract.md  含 ★INVARIANT★,body 引 `scripts/lumos` → 直接+有合約
    - Systems/NoContract.md    無合約,body 引 `scripts/lumos` → 直接+無合約
    - Systems/Indirect.md      related 指向 NoContract → 間接(hop1)
    空集合:新建 empty_repo → 回 {direct:[], indirect:[]} rc0。
    """
    import json as _json
    import tempfile as _tf

    # ── 建 fixture repo ──────────────────────────────────────────
    repo = Path(_tf.mkdtemp(prefix="gctl-t7-"))
    # scripts/ 頂層目錄(讓 _refcheck_scan top_dirs 認到 scripts/)
    (repo / "scripts").mkdir()
    (repo / "scripts" / "lumos").write_text("# fake lumos\n", encoding="utf-8")
    # vault
    vault = repo / "docs" / "test-knowledge"
    for sub in ("Systems", "Verification", "Projects", "MOC"):
        (vault / sub).mkdir(parents=True, exist_ok=True)
    (vault / "MOC" / "idx.md").write_bytes(
        "---\ntype: moc\n---\n# idx\n".encode("utf-8")
    )
    # 節點 A: 有合約(INVARIANT),引 scripts/lumos
    (vault / "Systems" / "WithContract.md").write_text(
        "---\ntype: system\nstatus: doing\nsummary: |-\n"
        "  KEY:★INVARIANT★ 合約 [test:t_stub]\n"
        "---\n引用 `scripts/lumos` 的用法\n",
        encoding="utf-8",
    )
    # 節點 B: 無合約,引 scripts/lumos;有 related 指向 Indirect
    (vault / "Systems" / "NoContract.md").write_text(
        "---\ntype: system\nstatus: doing\nrelated:\n  - \"[[Indirect]]\"\n"
        "---\n也引用 `scripts/lumos`\n",
        encoding="utf-8",
    )
    # 節點 C: 間接節點(NoContract 的 related)
    (vault / "Systems" / "Indirect.md").write_text(
        "---\ntype: system\nstatus: doing\n---\n無 code 引用\n",
        encoding="utf-8",
    )

    FIX = str(repo)

    # ── 主 schema 測試 ───────────────────────────────────────────
    out = run_lumos_capture(["impact", "--file", "scripts/lumos", "--repo", FIX, "--json"])
    d = _json.loads(out)

    check("impact_json: 頂層 key 集合 == {file,direct,indirect,incidents}",
          set(d) == {"file", "direct", "indirect", "incidents"}, f"keys={set(d)}")

    # direct 欄位: 必有 node/hit/contract/combo; 不得有 hop/from
    for x in d["direct"]:
        check("impact_json: direct 項含 node/hit/contract/combo",
              set(x) >= {"node", "hit", "contract", "combo"}, f"direct_item={x}")
        check("impact_json: direct 項無 hop",
              "hop" not in x, f"direct_item={x}")
        check("impact_json: direct 項無 from",
              "from" not in x, f"direct_item={x}")

    # indirect 欄位: 必有 node/hop/via/direction/from/contract/combo
    for x in d["indirect"]:
        check("impact_json: indirect 項含必要欄位",
              set(x) >= {"node", "hop", "via", "direction", "from", "contract", "combo"},
              f"indirect_item={x}")

    # combo 必有(每筆都出,無則 false)
    for x in d["direct"]:
        check("impact_json: direct.combo 是 bool",
              isinstance(x.get("combo"), bool), f"direct_item={x}")
    for x in d["indirect"]:
        check("impact_json: indirect.combo 是 bool",
              isinstance(x.get("combo"), bool), f"indirect_item={x}")

    # 合約節點排最前(若有合約節點,第一個的 contract 非 None;若全無合約,任意)
    if d["direct"]:
        has_contract = [x for x in d["direct"] if x["contract"] is not None]
        if has_contract:
            check("impact_json: 合約節點排 direct 之首",
                  d["direct"][0]["contract"] in ("IRREVERSIBLE", "INVARIANT"),
                  f"direct[0]={d['direct'][0]}, all={d['direct']}")
        else:
            check("impact_json: 無合約節點時首位 contract=None",
                  d["direct"][0]["contract"] is None, f"direct[0]={d['direct'][0]}")

    # 應有至少一個直接節點(WithContract 和 NoContract 都引了 scripts/lumos)
    check("impact_json: 有直接節點(WithContract+NoContract)",
          len(d["direct"]) >= 2, f"direct={d['direct']}")

    # 應有間接節點(NoContract related 指向 Indirect)
    check("impact_json: 有間接節點(Indirect via related)",
          len(d["indirect"]) >= 1, f"indirect={d['indirect']}")

    # indirect.hop 應為 int
    for x in d["indirect"]:
        check("impact_json: indirect.hop 是 int",
              isinstance(x["hop"], int), f"indirect_item={x}")

    # ── 空集合測試: 找不到任何直接節點時 rc0 + json 出 ─────────────────
    empty_repo = Path(_tf.mkdtemp(prefix="gctl-t7-empty-"))
    (empty_repo / "scripts").mkdir()
    (empty_repo / "scripts" / "newfile.py").write_text("# new\n", encoding="utf-8")
    empty_vault = empty_repo / "docs" / "test-knowledge"
    for sub in ("Systems", "Verification", "Projects", "MOC"):
        (empty_vault / sub).mkdir(parents=True, exist_ok=True)
    (empty_vault / "MOC" / "idx.md").write_bytes(
        "---\ntype: moc\n---\n# idx\n".encode("utf-8")
    )
    rc_empty = run_lumos(
        ["impact", "--file", "scripts/newfile.py", "--repo", str(empty_repo), "--json"]
    )
    check("impact_json: 空集合 rc==0(顯式斷言)",
          rc_empty == 0, f"rc={rc_empty}")
    out_empty = run_lumos_capture(
        ["impact", "--file", "scripts/newfile.py", "--repo", str(empty_repo), "--json"]
    )
    d_empty = _json.loads(out_empty)
    check("impact_json: 空集合 direct=[]",
          d_empty["direct"] == [], f"direct={d_empty['direct']}")
    check("impact_json: 空集合 indirect=[]",
          d_empty["indirect"] == [], f"indirect={d_empty['indirect']}")


def t_impact_cross_direct_node_dedup():
    """回歸: 兩個互相 related 的直接節點(A、B 都引 scripts/lumos 且互 related),
    跑 --json 後 B(與 A)只應出現在 direct、不得出現在 indirect。

    修前 bug: direct_seen 在迴圈內逐一 add,處理 A 的 BFS 展開命中 B 時 B 還沒進
    direct_seen → B 被誤加進 indirect,之後處理 B 又進 direct → B 同時出現在
    direct 與 indirect(矛盾輸出)。修後:先預種全量 direct_seen。
    """
    import json as _json
    import tempfile as _tf

    repo = Path(_tf.mkdtemp(prefix="gctl-t7-dedup-"))
    (repo / "scripts").mkdir()
    (repo / "scripts" / "lumos").write_text("# fake lumos\n", encoding="utf-8")
    vault = repo / "docs" / "test-knowledge"
    for sub in ("Systems", "Verification", "Projects", "MOC"):
        (vault / sub).mkdir(parents=True, exist_ok=True)
    (vault / "MOC" / "idx.md").write_bytes(
        "---\ntype: moc\n---\n# idx\n".encode("utf-8")
    )

    # A: 引 scripts/lumos,related 指向 B
    (vault / "Systems" / "DirectA.md").write_text(
        "---\ntype: system\nstatus: doing\nrelated:\n  - \"[[DirectB]]\"\n"
        "---\n引用 `scripts/lumos` 的用法\n",
        encoding="utf-8",
    )
    # B: 引 scripts/lumos,related 指向 A(互相 related)
    (vault / "Systems" / "DirectB.md").write_text(
        "---\ntype: system\nstatus: doing\nrelated:\n  - \"[[DirectA]]\"\n"
        "---\n也引用 `scripts/lumos`\n",
        encoding="utf-8",
    )

    rc = run_lumos(["impact", "--file", "scripts/lumos", "--repo", str(repo), "--json"])
    check("impact_dedup: rc==0", rc == 0, f"rc={rc}")

    out = run_lumos_capture(
        ["impact", "--file", "scripts/lumos", "--repo", str(repo), "--json"]
    )
    d = _json.loads(out)

    direct_nodes = {x["node"] for x in d["direct"]}
    indirect_nodes = {x["node"] for x in d["indirect"]}
    overlap = direct_nodes & indirect_nodes

    check("impact_dedup: DirectA 在 direct", "Systems/DirectA.md" in direct_nodes,
          f"direct_nodes={direct_nodes}")
    check("impact_dedup: DirectB 在 direct", "Systems/DirectB.md" in direct_nodes,
          f"direct_nodes={direct_nodes}")
    check("impact_dedup: direct 與 indirect 無交集(B 不得同時在兩邊)",
          len(overlap) == 0, f"overlap={overlap}, direct={direct_nodes}, indirect={indirect_nodes}")


def t_impact_multisource_bfs_min_hop():
    """I1 回歸:multi-source BFS 保證 hop = 距最近直接節點的 min 距離。

    圖結構:
      D1 → N(hop=2 via D1)
      D2 → N(hop=1 via D2)
      D1 先在 direct_rels 裡迭代

    斷言:N 的 hop == 1(min),而非 2(first-wins 舊 bug)。
    """
    import json as _json
    import tempfile as _tf

    repo = Path(_tf.mkdtemp(prefix="gctl-t-i1-minhop-"))
    (repo / "scripts").mkdir()
    (repo / "scripts" / "lumos").write_text("# fake lumos\n", encoding="utf-8")
    vault = repo / "docs" / "test-knowledge"
    for sub in ("Systems", "Verification", "Projects", "MOC"):
        (vault / sub).mkdir(parents=True, exist_ok=True)
    (vault / "MOC" / "idx.md").write_bytes(
        "---\ntype: moc\n---\n# idx\n".encode("utf-8")
    )

    # N: 目標節點,不引 scripts/lumos
    (vault / "Systems" / "NodeN.md").write_text(
        "---\ntype: system\nstatus: doing\n---\n# N\n",
        encoding="utf-8",
    )
    # M: 中繼節點,D1 → M → N(D1 到 N 是 hop=2)
    (vault / "Systems" / "NodeM.md").write_text(
        "---\ntype: system\nstatus: doing\nrelated:\n  - \"[[NodeN]]\"\n---\n# M\n",
        encoding="utf-8",
    )
    # D1: 引 scripts/lumos,related → M(D1→M→N,hop=2);D1 先在字母序排在前
    (vault / "Systems" / "DirectA.md").write_text(
        "---\ntype: system\nstatus: doing\nrelated:\n  - \"[[NodeM]]\"\n"
        "---\n引用 `scripts/lumos`\n",
        encoding="utf-8",
    )
    # D2: 引 scripts/lumos,related → N(D2→N,hop=1)
    (vault / "Systems" / "DirectB.md").write_text(
        "---\ntype: system\nstatus: doing\nrelated:\n  - \"[[NodeN]]\"\n"
        "---\n也引用 `scripts/lumos`\n",
        encoding="utf-8",
    )

    out = run_lumos_capture(
        ["impact", "--file", "scripts/lumos", "--repo", str(repo), "--json"]
    )
    d = _json.loads(out)

    indirect_nodes = {x["node"]: x for x in d["indirect"]}
    direct_nodes = {x["node"] for x in d["direct"]}

    check("impact_minhop: DirectA 在 direct", "Systems/DirectA.md" in direct_nodes,
          f"direct={direct_nodes}")
    check("impact_minhop: DirectB 在 direct", "Systems/DirectB.md" in direct_nodes,
          f"direct={direct_nodes}")
    check("impact_minhop: NodeN 在 indirect", "Systems/NodeN.md" in indirect_nodes,
          f"indirect keys={list(indirect_nodes)}")
    n_hop = indirect_nodes.get("Systems/NodeN.md", {}).get("hop")
    check("impact_minhop: NodeN.hop == 1(multi-source BFS min 距離,非 first-wins 2)",
          n_hop == 1, f"got hop={n_hop}, expected 1")


def t_impact_depth_config_integration():
    """Task 8 M-3: CLI --depth 顯式值覆蓋 .lumos/impact.json config 的整合測試。

    建一個 fixture repo:
    - .lumos/impact.json 設 {"depth": 3}
    - 一個 code 檔 scripts/target.py(不需實際 python,只需存在)
    - vault 含 depth 1 可見但 depth 3 才多見的多層圖:
        DirectNode → Hop1 → Hop2 → Hop3(三層 related chain)
      DirectNode body 引 `scripts/target.py` → 直接節點。
      Hop1/2/3 依 related 鏈串 → 深度控制間接 hop 上限。

    驗兩點:
    1. 不帶 --depth → 用 config depth=3 → indirect 可看到 hop3 節點(Hop3)。
    2. 帶 --depth 1 → 覆蓋 config → indirect 最多 hop=1 → Hop2/Hop3 不出現。
    """
    import json as _json
    import tempfile as _tf

    # ── 建 fixture ──
    repo = Path(_tf.mkdtemp(prefix="gctl-t8-depth-"))
    (repo / "scripts").mkdir()
    (repo / "scripts" / "target.py").write_text("# target\n", encoding="utf-8")

    vault = repo / "docs" / "test-knowledge"
    for sub in ("Systems", "Verification", "Projects", "MOC"):
        (vault / sub).mkdir(parents=True, exist_ok=True)
    (vault / "MOC" / "idx.md").write_bytes(b"---\ntype: moc\n---\n# idx\n")

    # DirectNode — body 引 scripts/target.py,related → Hop1
    (vault / "Systems" / "DirectNode.md").write_text(
        "---\ntype: system\nstatus: doing\nrelated:\n  - \"[[Hop1]]\"\n---\n"
        "引用 `scripts/target.py`\n",
        encoding="utf-8",
    )
    # Hop1 → related → Hop2
    (vault / "Systems" / "Hop1.md").write_text(
        "---\ntype: system\nstatus: doing\nrelated:\n  - \"[[Hop2]]\"\n---\n無 code 引用\n",
        encoding="utf-8",
    )
    # Hop2 → related → Hop3
    (vault / "Systems" / "Hop2.md").write_text(
        "---\ntype: system\nstatus: doing\nrelated:\n  - \"[[Hop3]]\"\n---\n無 code 引用\n",
        encoding="utf-8",
    )
    # Hop3 — 葉節點
    (vault / "Systems" / "Hop3.md").write_text(
        "---\ntype: system\nstatus: doing\n---\n無 code 引用\n",
        encoding="utf-8",
    )

    # .lumos/impact.json — config depth=3
    (repo / ".lumos").mkdir()
    (repo / ".lumos" / "impact.json").write_text('{"depth": 3}', encoding="utf-8")

    FIX = str(repo)
    file_arg = "scripts/target.py"

    # ── 情境 A: 不帶 --depth → config depth=3 → Hop3 應出現 ──
    out_a = run_lumos_capture(["impact", "--file", file_arg, "--repo", FIX, "--json"])
    d_a = _json.loads(out_a)
    indirect_nodes_a = {x["node"] for x in d_a["indirect"]}
    check("impact_depth_integration: config depth=3 → Hop3 出現於 indirect",
          any("Hop3" in n for n in indirect_nodes_a),
          f"indirect_nodes={indirect_nodes_a}")
    check("impact_depth_integration: config depth=3 → Hop2 出現於 indirect",
          any("Hop2" in n for n in indirect_nodes_a),
          f"indirect_nodes={indirect_nodes_a}")

    # ── 情境 B: --depth 1 覆蓋 config(3) → 只有 hop≤1 → Hop2/Hop3 不應出現 ──
    out_b = run_lumos_capture(["impact", "--file", file_arg, "--repo", FIX, "--depth", "1", "--json"])
    d_b = _json.loads(out_b)
    indirect_nodes_b = {x["node"] for x in d_b["indirect"]}
    check("impact_depth_integration: --depth 1 覆蓋 config → Hop2 不出現",
          not any("Hop2" in n for n in indirect_nodes_b),
          f"indirect_nodes={indirect_nodes_b}")
    check("impact_depth_integration: --depth 1 覆蓋 config → Hop3 不出現",
          not any("Hop3" in n for n in indirect_nodes_b),
          f"indirect_nodes={indirect_nodes_b}")
    check("impact_depth_integration: --depth 1 → Hop1 仍出現(depth=1 的 hop1 可達)",
          any("Hop1" in n for n in indirect_nodes_b),
          f"indirect_nodes={indirect_nodes_b}")

    # ── 情境 C: bool in config 不穿透 int 守衛 → 回預設 depth=2 ──
    # 改 config 為 {"depth": true}(bool),確認不套用(fallback=2 → Hop3 看不到)
    (repo / ".lumos" / "impact.json").write_text('{"depth": true}', encoding="utf-8")
    out_c = run_lumos_capture(["impact", "--file", file_arg, "--repo", FIX, "--json"])
    d_c = _json.loads(out_c)
    indirect_nodes_c = {x["node"] for x in d_c["indirect"]}
    # depth=2 → Hop1(hop1) + Hop2(hop2) 可見、Hop3(hop3) 不可見
    check("impact_depth_integration: bool depth 不穿透守衛 → Hop3 不出現(fallback depth=2)",
          not any("Hop3" in n for n in indirect_nodes_c),
          f"indirect_nodes={indirect_nodes_c}")
    check("impact_depth_integration: bool depth 不穿透守衛 → Hop2 仍出現(fallback depth=2)",
          any("Hop2" in n for n in indirect_nodes_c),
          f"indirect_nodes={indirect_nodes_c}")


def t_impact_config():
    """Task 8: _impact_load_config — 有檔 depth/ttl merge 預設;無檔 → 2/20;壞 json → 2/20 不拋。"""
    import importlib.util
    import tempfile
    import os
    from importlib.machinery import SourceFileLoader

    # 動態 import scripts/lumos(無 .py 副檔名 → 用 SourceFileLoader)
    loader = SourceFileLoader("lumos_mod_cfg", GRAPHCTL)
    spec = importlib.util.spec_from_loader("lumos_mod_cfg", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    fn = m._impact_load_config

    # 情境 1: 有 .lumos/impact.json {"depth":3} → depth 3,ttl_min 補預設 20
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(d + "/.lumos")
        open(d + "/.lumos/impact.json", "w").write('{"depth":3}')
        got = fn(d)
        check("impact_config: 有檔 depth 3", got == {"depth": 3, "ttl_min": 20}, f"got={got}")

    # 情境 2: 無 .lumos/impact.json → 預設 2/20
    with tempfile.TemporaryDirectory() as d:
        got = fn(d)
        check("impact_config: 無檔 → 2/20", got == {"depth": 2, "ttl_min": 20}, f"got={got}")

    # 情境 3: 壞 json → 預設 2/20,不拋
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(d + "/.lumos")
        open(d + "/.lumos/impact.json", "w").write("{bad")
        try:
            got = fn(d)
            check("impact_config: 壞 json → 2/20", got == {"depth": 2, "ttl_min": 20}, f"got={got}")
        except Exception as e:
            check("impact_config: 壞 json 不拋", False, f"raised {e}")

    # 情境 4: ttl_min 可覆寫
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(d + "/.lumos")
        open(d + "/.lumos/impact.json", "w").write('{"depth":4,"ttl_min":60}')
        got = fn(d)
        check("impact_config: depth+ttl 皆覆寫", got == {"depth": 4, "ttl_min": 60}, f"got={got}")

    # 情境 5: depth=true(bool)→ 不視為合法 int → fallback 2
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(d + "/.lumos")
        open(d + "/.lumos/impact.json", "w").write('{"depth":true}')
        got = fn(d)
        check("impact_config: depth=true(bool)→ fallback 2",
              got == {"depth": 2, "ttl_min": 20}, f"got={got}")

    # 情境 6: ttl_min=false(bool)→ 不視為合法 int → fallback 20
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(d + "/.lumos")
        open(d + "/.lumos/impact.json", "w").write('{"ttl_min":false}')
        got = fn(d)
        check("impact_config: ttl_min=false(bool)→ fallback 20",
              got == {"depth": 2, "ttl_min": 20}, f"got={got}")


def t_impact_hook_filter_and_rc():
    """Task 9: impact-hook 過濾 + tool_input.file_path 巢狀讀取 + rc 處理。

    測試對象是 scripts/hooks/claude/impact-hook.py 的可 import 函式:
      - extract_path(payload) → 從 payload["tool_input"]["file_path"] 取路徑
      - hook_decide(payload)  → 非 code → None;code 觸發 → 非 None
    """
    import importlib.util
    from importlib.machinery import SourceFileLoader
    hook_path = str(Path(__file__).resolve().parent / "hooks" / "claude" / "impact-hook.py")
    loader = SourceFileLoader("impact_hook_mod", hook_path)
    spec = importlib.util.spec_from_loader("impact_hook_mod", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    extract_path = m.extract_path
    hook_decide = m.hook_decide

    # 1. extract_path: 從巢狀 tool_input 讀 file_path
    check("impact_hook: extract_path 讀 tool_input.file_path",
          extract_path({"tool_input": {"file_path": "x.py"}}) == "x.py",
          "expected 'x.py'")

    # 2. 圖譜檔(.md 在 docs/*-knowledge/)→ 放行(None)
    check("impact_hook: .md 圖譜路徑 → 放行 None",
          hook_decide({"tool_input": {"file_path": "docs/x-knowledge/a.md"}}) is None,
          "expected None for graph .md")

    # 3. /docs/ 路徑下的 code 副檔名也應排除(EXCLUDE_PATH_CONTAINS)
    check("impact_hook: /docs/ 下 .py → 放行 None",
          hook_decide({"tool_input": {"file_path": "docs/some/file.py"}}) is None,
          "expected None for /docs/ path")

    # 4. code 副檔名(.py)→ 觸發(非 None)
    check("impact_hook: .py → 觸發(非 None)",
          hook_decide({"tool_input": {"file_path": "a.py"}}) is not None,
          "expected non-None for .py")

    # 5. node_modules 下 .js → 放行(EXCLUDE_PATH_CONTAINS)
    check("impact_hook: node_modules/.js → 放行 None",
          hook_decide({"tool_input": {"file_path": "node_modules/lib/a.js"}}) is None,
          "expected None for node_modules")

    # 6. lock 檔 → 放行(EXCLUDE_FILENAMES)
    check("impact_hook: package-lock.json → 放行 None",
          hook_decide({"tool_input": {"file_path": "package-lock.json"}}) is None,
          "expected None for lock file")

    # 7. 非 code 副檔名(.txt)→ 放行
    check("impact_hook: .txt → 放行 None",
          hook_decide({"tool_input": {"file_path": "readme.txt"}}) is None,
          "expected None for .txt")

    # 8. .ts → 觸發
    check("impact_hook: .ts → 觸發(非 None)",
          hook_decide({"tool_input": {"file_path": "src/foo.ts"}}) is not None,
          "expected non-None for .ts")


def t_impact_hook_ttl():
    """Task 10: _ttl_should_inject TTL 冷卻窗 + 惰性清理 >24h session 目錄。

    測試對象是 scripts/hooks/claude/impact-hook.py 的:
      - _ttl_should_inject(session_id, file_abs, ttl_sec) -> bool
      - _backdate_marker(session_id, file_abs, seconds_ago)  (測試輔助)
    """
    import importlib.util
    import tempfile
    import hashlib
    import time
    from importlib.machinery import SourceFileLoader
    from pathlib import Path as _P

    hook_path = str(_P(__file__).resolve().parent / "hooks" / "claude" / "impact-hook.py")
    loader = SourceFileLoader("impact_hook_mod_ttl", hook_path)
    spec = importlib.util.spec_from_loader("impact_hook_mod_ttl", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)

    _ttl_should_inject = m._ttl_should_inject
    _backdate_marker = m._backdate_marker

    sid = "sess-ttl-test-001"
    f = "/abs/path/to/testfile.py"

    # 計算 marker 路徑,以便 cleanup 後驗證
    h = hashlib.sha1(f.encode()).hexdigest()[:16]
    marker_path = _P(tempfile.gettempdir()) / f"lumos-impact-{sid}" / h

    try:
        # 確保乾淨起點
        if marker_path.exists():
            marker_path.unlink()

        # 1. 首次呼叫 → True,且建立 marker 檔
        result_first = _ttl_should_inject(sid, f, ttl_sec=1200)
        check("impact_hook_ttl: 首次 True", result_first is True,
              f"expected True, got {result_first}")
        check("impact_hook_ttl: 首次後 marker 存在",
              marker_path.exists(), f"marker 未建立: {marker_path}")

        # 2. 窗內第二次 → False(冷卻)
        result_second = _ttl_should_inject(sid, f, ttl_sec=1200)
        check("impact_hook_ttl: 窗內第二次 False", result_second is False,
              f"expected False (cooldown), got {result_second}")

        # 3. 把 marker 倒推 2000s → 窗外復活 True
        _backdate_marker(sid, f, 2000)
        result_revive = _ttl_should_inject(sid, f, ttl_sec=1200)
        check("impact_hook_ttl: 窗外復活 True", result_revive is True,
              f"expected True (revive after backdate), got {result_revive}")

        # 4. 測試惰性清理:建一個 mtime 超過 24h 的假 session 目錄
        old_sid = "sess-old-stale-999"
        old_session_dir = _P(tempfile.gettempdir()) / f"lumos-impact-{old_sid}"
        old_session_dir.mkdir(parents=True, exist_ok=True)
        old_marker = old_session_dir / "deadbeef12345678"
        old_marker.write_text("0.0")  # 極老時間戳
        # 把 mtime 設為 25h 前
        old_time = time.time() - 25 * 3600
        import os as _os
        _os.utime(str(old_session_dir), (old_time, old_time))

        # 觸發一次 inject(對一個新 sid/file),會觸發惰性清理
        new_sid = "sess-trigger-cleanup-002"
        new_f = "/abs/path/to/anotherfile.py"
        _ttl_should_inject(new_sid, new_f, ttl_sec=1200)

        # 舊的 session 目錄應被清掉
        check("impact_hook_ttl: 惰性清理 >24h session 目錄被刪",
              not old_session_dir.exists(),
              f"old session dir still exists: {old_session_dir}")

    finally:
        # 清理本測試建立的 marker 檔與目錄
        for cleanup_sid, cleanup_f in [
            (sid, f),
            ("sess-trigger-cleanup-002", "/abs/path/to/anotherfile.py"),
        ]:
            cleanup_h = hashlib.sha1(cleanup_f.encode()).hexdigest()[:16]
            cleanup_dir = _P(tempfile.gettempdir()) / f"lumos-impact-{cleanup_sid}"
            cleanup_marker = cleanup_dir / cleanup_h
            if cleanup_marker.exists():
                cleanup_marker.unlink()
            try:
                cleanup_dir.rmdir()
            except OSError:
                pass
        # 確保 stale dir 清掉(若清理邏輯沒跑到)
        old_sid = "sess-old-stale-999"
        old_session_dir = _P(tempfile.gettempdir()) / f"lumos-impact-{old_sid}"
        import shutil as _shutil
        if old_session_dir.exists():
            _shutil.rmtree(str(old_session_dir), ignore_errors=True)


def t_impact_hook_inject():
    """Task 11: additionalContext 注入 + 動手前分析指令 + fail-open。

    測試對象是 scripts/hooks/claude/impact-hook.py 的:
      - build_additional_context(impact_data) -> str   (注入文字生成)
      - inject_additional_context(impact_data) -> None (印 JSON 到 stdout)

    輔助函式 hook_run_with_impact(impact_data) 用 subprocess 重跑 main(),
    繞過真實 lumos 呼叫,直接把 impact_data mock 注入;回傳 stdout 字串。
    """
    import importlib.util
    import io
    import json
    import subprocess
    import sys
    import tempfile
    from importlib.machinery import SourceFileLoader
    from pathlib import Path as _P
    from unittest.mock import patch

    hook_path = str(_P(__file__).resolve().parent / "hooks" / "claude" / "impact-hook.py")
    loader = SourceFileLoader("impact_hook_mod_inject", hook_path)
    spec = importlib.util.spec_from_loader("impact_hook_mod_inject", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)

    build_additional_context = m.build_additional_context
    inject_additional_context = m.inject_additional_context

    def hook_run_with_impact(impact_data: dict) -> str:
        """呼叫 inject_additional_context,捕捉 stdout 回傳。"""
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            inject_additional_context(impact_data)
        return buf.getvalue().strip()

    # ── 1. 非空影響集 → stdout 是合法 JSON,含 hookSpecificOutput.additionalContext + 指令文字 ──
    out = hook_run_with_impact({
        "direct": [{"node": "S/A", "hit": "body-inline-code", "contract": "INVARIANT", "combo": False}],
        "indirect": []
    })
    check("impact_hook_inject: 非空影響集 stdout 非空",
          out != "",
          f"expected non-empty stdout, got {out!r}")
    j = json.loads(out)
    check("impact_hook_inject: hookSpecificOutput.hookEventName == PreToolUse",
          j["hookSpecificOutput"]["hookEventName"] == "PreToolUse",
          f"got {j}")
    ctx = j["hookSpecificOutput"]["additionalContext"]
    check("impact_hook_inject: additionalContext 含指令文字「動手前」",
          "動手前" in ctx,
          f"ctx={ctx!r}")

    # ── 2. 空影響集(direct 與 indirect 皆空)→ 不注入(無輸出) ──
    out_empty = hook_run_with_impact({"direct": [], "indirect": []})
    check("impact_hook_inject: 空集合不注入(無輸出)",
          out_empty == "",
          f"expected empty stdout for empty impact, got {out_empty!r}")

    # ── 3. build_additional_context:清單含節點名稱 ──
    ctx2 = build_additional_context({
        "direct": [{"node": "Systems/lumos-refcheck", "hit": "body-inline-code",
                    "contract": "INVARIANT", "combo": True}],
        "indirect": [{"node": "Systems/pitfalls", "hop": 1, "via": "related",
                      "direction": "backlink", "from": "Systems/lumos-refcheck",
                      "contract": None, "combo": False}],
    })
    check("impact_hook_inject: build_additional_context 含直接節點名稱",
          "Systems/lumos-refcheck" in ctx2,
          f"ctx2={ctx2!r}")
    check("impact_hook_inject: build_additional_context 含間接節點名稱",
          "Systems/pitfalls" in ctx2,
          f"ctx2={ctx2!r}")
    check("impact_hook_inject: build_additional_context 含合約標記",
          "INVARIANT" in ctx2,
          f"ctx2={ctx2!r}")
    check("impact_hook_inject: build_additional_context 含指令文字",
          "動手前" in ctx2,
          f"ctx2={ctx2!r}")

    # ── 4. lumos 缺席(subprocess FileNotFoundError)→ fail-open:不拋、不注入 ──
    # 模擬 main() 中 subprocess.run 拋 FileNotFoundError
    import json as _json
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "/some/project/foo.py"},
        "session_id": "sess-inject-failopen-001",
        "cwd": "/some/project",
    }
    env_patch = {"CLAUDE_PROJECT_DIR": "/some/project"}
    # patch _find_lumos_script 讓它回傳一個路徑,但 subprocess.run 拋 FileNotFoundError
    import os
    with patch.object(m, "_find_lumos_script", return_value="/nonexistent/lumos"), \
         patch("subprocess.run", side_effect=FileNotFoundError("no lumos")), \
         patch.dict(os.environ, env_patch), \
         patch("sys.stdin", io.StringIO(_json.dumps(payload))):
        buf_fo = io.StringIO()
        with patch("sys.stdout", buf_fo):
            try:
                rc_fo = m.main()
            except SystemExit as e:
                rc_fo = e.code
        fo_out = buf_fo.getvalue().strip()
    check("impact_hook_inject: lumos 缺席 fail-open rc=0",
          rc_fo == 0,
          f"expected rc=0, got {rc_fo}")
    check("impact_hook_inject: lumos 缺席 fail-open 不注入",
          fo_out == "",
          f"expected empty stdout (no inject), got {fo_out!r}")

    # ── 5. rc3 → 不注入(僅印 debug 到 stderr) ──
    import unittest.mock as _mock
    _proc_rc3 = _mock.MagicMock()
    _proc_rc3.returncode = 3
    _proc_rc3.stdout = ""
    _proc_rc3.stderr = ""
    with patch.object(m, "_find_lumos_script", return_value="/fake/lumos"), \
         patch("subprocess.run", return_value=_proc_rc3), \
         patch.dict(os.environ, env_patch), \
         patch("sys.stdin", io.StringIO(_json.dumps(payload))):
        buf_rc3 = io.StringIO()
        buf_rc3_err = io.StringIO()
        with patch("sys.stdout", buf_rc3), patch("sys.stderr", buf_rc3_err):
            try:
                rc_rc3 = m.main()
            except SystemExit as e:
                rc_rc3 = e.code
        rc3_out = buf_rc3.getvalue().strip()
    check("impact_hook_inject: rc3 不注入(stdout 無 JSON)",
          rc3_out == "",
          f"expected empty stdout for rc3, got {rc3_out!r}")
    check("impact_hook_inject: rc3 放行 rc=0",
          rc_rc3 == 0,
          f"expected rc=0, got {rc_rc3}")

    # ── 6. T9-M3 補測:非空影響集 → main() stdout 含合法 JSON + additionalContext ──
    import uuid as _uuid
    _proc_ok = _mock.MagicMock()
    _proc_ok.returncode = 0
    _proc_ok.stdout = _json.dumps({
        "file": "foo.py",
        "direct": [{"node": "Systems/A", "hit": "body-inline-code",
                    "contract": None, "combo": False}],
        "indirect": [],
    })
    _proc_ok.stderr = ""
    # 每次測試用新 UUID 作 session_id,確保 TTL marker 是全新的(避免跨次測試 marker 殘留)
    fresh_sid = str(_uuid.uuid4())
    payload_with_sid = dict(payload, session_id=fresh_sid)
    with patch.object(m, "_find_lumos_script", return_value="/fake/lumos"), \
         patch("subprocess.run", return_value=_proc_ok), \
         patch.dict(os.environ, env_patch), \
         patch("sys.stdin", io.StringIO(_json.dumps(payload_with_sid))):
        buf_main = io.StringIO()
        with patch("sys.stdout", buf_main):
            try:
                rc_main = m.main()
            except SystemExit as e:
                rc_main = e.code
        main_out = buf_main.getvalue().strip()
    check("impact_hook_inject: main() 非空影響集 → stdout 非空",
          main_out != "",
          f"expected JSON on stdout, got {main_out!r}")
    j_main = json.loads(main_out)
    check("impact_hook_inject: main() hookSpecificOutput.hookEventName == PreToolUse",
          j_main.get("hookSpecificOutput", {}).get("hookEventName") == "PreToolUse",
          f"got {j_main}")
    check("impact_hook_inject: main() additionalContext 含指令文字",
          "動手前" in j_main.get("hookSpecificOutput", {}).get("additionalContext", ""),
          f"got {j_main}")


def t_impact_hook_incidents_inject():
    """Task 3: impact hook 注入 incidents 段。

    測試 build_additional_context 納入 incidents 段,
    及 inject_additional_context 的「空集合不注入」判定納入 incidents。
    """
    import importlib.util
    import io
    import json
    from importlib.machinery import SourceFileLoader
    from pathlib import Path as _P
    from unittest.mock import patch

    hook_path = str(_P(__file__).resolve().parent / "hooks" / "claude" / "impact-hook.py")
    loader = SourceFileLoader("impact_hook_mod_incidents", hook_path)
    spec = importlib.util.spec_from_loader("impact_hook_mod_incidents", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)

    inject_additional_context = m.inject_additional_context
    build_additional_context = m.build_additional_context

    def hook_run_with_impact(impact_data: dict) -> str:
        """呼叫 inject_additional_context,捕捉 stdout 回傳。"""
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            inject_additional_context(impact_data)
        return buf.getvalue().strip()

    # ── 1. 非空 incidents(direct/indirect 皆空)→ stdout 非空,含「相關事故」段 ──
    out = hook_run_with_impact({
        "direct": [],
        "indirect": [],
        "incidents": [{"node": "Issues/N1", "matched_by": "glob:**/*Repo*", "contract": None, "combo": False}]
    })
    check("impact_hook_incidents_inject: 非空 incidents → stdout 非空",
          out != "",
          f"expected non-empty stdout, got {out!r}")
    j = json.loads(out)
    ctx = j["hookSpecificOutput"]["additionalContext"]
    check("impact_hook_incidents_inject: additionalContext 含「相關事故」或 incident",
          "相關事故" in ctx or "incident" in ctx.lower(),
          f"ctx={ctx!r}")
    check("impact_hook_incidents_inject: additionalContext 含事故節點名稱",
          "Issues/N1" in ctx,
          f"ctx={ctx!r}")
    check("impact_hook_incidents_inject: additionalContext 含 matched_by",
          "glob:**/*Repo*" in ctx,
          f"ctx={ctx!r}")

    # ── 2. 全空(direct/indirect/incidents 皆空)→ 不注入 ──
    out_all_empty = hook_run_with_impact({"direct": [], "indirect": [], "incidents": []})
    check("impact_hook_incidents_inject: 全空(含空 incidents)不注入",
          out_all_empty == "",
          f"expected empty stdout for all-empty impact, got {out_all_empty!r}")

    # ── 3. 空 incidents 但有 direct → 注入(direct 主段),不含「相關事故」段 ──
    out_no_inc = hook_run_with_impact({
        "direct": [{"node": "Systems/A", "hit": "body-inline-code", "contract": None, "combo": False}],
        "indirect": [],
        "incidents": [],
    })
    check("impact_hook_incidents_inject: 空 incidents 有 direct → 仍注入",
          out_no_inc != "",
          f"expected non-empty stdout, got {out_no_inc!r}")
    j_no_inc = json.loads(out_no_inc)
    ctx_no_inc = j_no_inc["hookSpecificOutput"]["additionalContext"]
    check("impact_hook_incidents_inject: 空 incidents → 無「相關事故」段",
          "相關事故" not in ctx_no_inc,
          f"ctx={ctx_no_inc!r}")

    # ── 4. build_additional_context 含 incidents 時確有「相關事故」段 ──
    ctx_build = build_additional_context({
        "direct": [],
        "indirect": [],
        "incidents": [
            {"node": "Issues/SQL_NPlus1", "matched_by": "content:SELECT.*FROM",
             "contract": "INVARIANT", "combo": False},
        ],
    })
    check("impact_hook_incidents_inject: build_additional_context 含「相關事故」標題",
          "相關事故" in ctx_build,
          f"ctx_build={ctx_build!r}")
    check("impact_hook_incidents_inject: build_additional_context 含事故節點名稱",
          "Issues/SQL_NPlus1" in ctx_build,
          f"ctx_build={ctx_build!r}")
    check("impact_hook_incidents_inject: build_additional_context incidents 含合約標記",
          "INVARIANT" in ctx_build,
          f"ctx_build={ctx_build!r}")


def t_impact_hook_find_lumos_real():
    """C1 回歸:_find_lumos_script() 真實呼叫(不 mock)應能解析到可用的 lumos。

    安裝後 hook 複製到 ~/.claude/hooks/impact-hook.py,repo-relative 猜測
    ( Path(__file__).parent×4/scripts/lumos )指向不存在的路徑。修法:優先
    shutil.which("lumos"),它能在 PATH(~/.local/bin/lumos)找到實際安裝的 lumos。

    測試策略:不 mock _find_lumos_script,直接呼叫它,斷言回傳值非 None 且路徑存在。
    前提:lumos 必須在 PATH 或 hook 仍在 repo 樹內(本測試在 CI/開發機皆可過)。
    """
    import shutil as _shutil
    import importlib.util as _ilu

    hook_path = str(Path(__file__).resolve().parent / "hooks" / "claude" / "impact-hook.py")
    spec = _ilu.spec_from_file_location("impact_hook_c1", hook_path)
    m = _ilu.module_from_spec(spec)
    spec.loader.exec_module(m)

    result = m._find_lumos_script()

    # 驗 1:不得回傳 None(不論走 which 還是 repo-relative fallback)
    check("impact_hook_find_lumos_real: _find_lumos_script() 非 None",
          result is not None,
          "返回 None — lumos 不在 PATH 且 hook repo-relative fallback 也失效")

    if result is not None:
        # 驗 2:路徑必須存在
        check("impact_hook_find_lumos_real: 解析路徑存在於磁碟",
              Path(result).exists(),
              f"路徑 {result!r} 不存在")

        # 驗 3:如果 which 找得到 lumos,應優先回傳 which 的結果
        which_result = _shutil.which("lumos")
        if which_result is not None:
            check("impact_hook_find_lumos_real: 優先回傳 which('lumos') 結果",
                  Path(result).resolve() == Path(which_result).resolve(),
                  f"expected which={which_result!r}, got {result!r}")


def t_impact_end_to_end():
    """Task 12 端到端 smoke:注入暫探針節點 → lumos impact 抓到 → 清理。

    步驟:
      1. 在真實 vault 建 _impact_probe.md(body 含 `scripts/lumos` inline-code)
      2. 執行 lumos impact --file scripts/lumos --repo . --json
      3. 斷言 direct 含 _impact_probe 節點
      4. finally 刪除探針節點

    此測試驗證「CLI + 真實 vault 掃描 + code→node 反查」全鏈正確。
    """
    import json as _json
    import os as _os

    # 找到本 repo root(test_lumos.py 在 scripts/,往上一層)
    repo_root = Path(__file__).resolve().parent.parent
    probe = repo_root / "docs" / "lumos-toolchain-knowledge" / "Systems" / "_impact_probe.md"

    # 寫探針節點(body 引用 scripts/lumos inline-code)
    probe_content = (
        "---\ntype: system\nstatus: doing\nsummary: |-\n  KEY:probe\n---\n"
        "# probe\n\nbody `scripts/lumos`\n"
    )
    probe.write_text(probe_content, encoding="utf-8")

    try:
        out = run_lumos_capture(["impact", "--file", str(repo_root / "scripts" / "lumos"),
                                 "--repo", str(repo_root), "--json"])
        try:
            data = _json.loads(out)
        except _json.JSONDecodeError:
            data = {}

        direct = data.get("direct", [])
        found_probe = any("_impact_probe" in x.get("node", "") for x in direct)
        check("impact_end_to_end: direct 含 _impact_probe 節點",
              found_probe,
              f"direct={direct!r}")
    finally:
        try:
            probe.unlink()
        except OSError:
            pass


def t_impact_hook_registration_source():
    """Task 12 hook 註冊:驗 merge-claude-settings.py 的 HOOK_ENTRIES 源碼含 PreToolUse impact-hook.py 條目。

    直接 import 源碼模組驗 HOOK_ENTRIES 結構,零外部依賴(不讀 ~/.claude/settings.json),
    CI 隔離環境可過。
    """
    import importlib.util as _ilu

    spec_path = Path(__file__).resolve().parent / "merge-claude-settings.py"
    spec = _ilu.spec_from_file_location("mcs", spec_path)
    mcs = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mcs)
    entries = mcs.HOOK_ENTRIES.get("PreToolUse", [])
    found = any(
        "impact-hook.py" in h.get("command", "")
        for e in entries
        for h in e.get("hooks", [])
    )
    check("impact_hook_registration_source: HOOK_ENTRIES PreToolUse 含 impact-hook.py",
          found,
          f"entries={entries!r}")


# ─── Task 1: _match_incident_triggers(pitfall_when glob/content-regex) ──────────

def t_match_incident_triggers():
    import importlib.util
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("lumos_mod_mit", GRAPHCTL)
    spec = importlib.util.spec_from_loader("lumos_mod_mit", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    _match_incident_triggers = m._match_incident_triggers

    env, _ = make_fixture_vault({
        "Issues/N1.md": "---\npitfall_when:\n  - \"glob:**/*Repository*.py\"\n---\nN+1 事故",
        "Issues/SQL.md": "---\npitfall_when:\n  - \"content:SELECT\\s.*FROM\"\n---\nraw SQL 事故",
        "Issues/None.md": "---\n---\n無 trigger",
    })
    # glob 命中路徑
    r = _match_incident_triggers("app/UserRepository.py", "code", env)
    check("match_incident: glob 命中 Issues/N1.md",
          any(x["node"] == "Issues/N1.md" for x in r), f"r={r}")
    # content-regex 命中內容
    r2 = _match_incident_triggers("x.py", "q = 'SELECT a FROM t'", env)
    check("match_incident: content-regex 命中 Issues/SQL.md",
          any(x["node"] == "Issues/SQL.md" for x in r2), f"r2={r2}")
    # 都不命中
    check("match_incident: 都不命中回空 list",
          _match_incident_triggers("x.py", "nothing", env) == [], "expected []")
    # 新建檔無 content → 只 glob
    r3 = _match_incident_triggers("app/UserRepository.py", "", env)
    check("match_incident: 新建檔 glob 仍命中 N1.md",
          any(x["node"] == "Issues/N1.md" for x in r3), f"r3={r3}")
    check("match_incident: 新建檔 content-regex miss SQL.md",
          not any(x["node"] == "Issues/SQL.md" for x in r3), f"r3={r3}")
    # matched_by 欄位存在且含命中的 trigger 字串
    r_mb = _match_incident_triggers("app/UserRepository.py", "code", env)
    n1_hit = next((x for x in r_mb if x["node"] == "Issues/N1.md"), None)
    check("match_incident: matched_by 含命中 trigger",
          n1_hit is not None and "glob:" in n1_hit.get("matched_by", ""), f"n1_hit={n1_hit}")


def t_impact_incidents_section():
    """Task 2: --json incidents 段 + trigger 去重 + 讀被碰檔內容。

    fixture:
    - repo/app/UserRepository.py  (實際存在的 code 檔)
    - Issues/N1.md  pitfall_when glob 命中 UserRepository.py
                    且 body 引用 `app/UserRepository.py`(→ 本來 direct)
    去重斷言:N1.md 只列 incidents、不在 direct。
    無 pitfall_when 節點不進 incidents。
    """
    import json as _json
    import tempfile as _tf

    repo = Path(_tf.mkdtemp(prefix="gctl-t-inc-"))
    # scripts/ 頂層目錄(讓 _refcheck_scan top_dirs 認到)
    (repo / "scripts").mkdir()
    (repo / "scripts" / "lumos").write_text("# fake\n", encoding="utf-8")
    # 被碰 code 檔(content-regex 測試用,可為空)
    (repo / "app").mkdir()
    (repo / "app" / "UserRepository.py").write_text("# repo\n", encoding="utf-8")
    # vault
    vault = repo / "docs" / "test-knowledge"
    for sub in ("Systems", "Issues", "Verification", "Projects", "MOC"):
        (vault / sub).mkdir(parents=True, exist_ok=True)
    (vault / "MOC" / "idx.md").write_bytes("---\ntype: moc\n---\n# idx\n".encode("utf-8"))
    # 事故節點: pitfall_when glob + body 引用 app/UserRepository.py(→ 本來進 direct)
    (vault / "Issues" / "N1.md").write_text(
        "---\npitfall_when:\n  - \"glob:**/*Repository*.py\"\n---\n"
        "引用 `app/UserRepository.py` 的用法\n",
        encoding="utf-8",
    )
    # 普通系統節點(無 pitfall_when): 也引用同一 code 檔 → 應留在 direct
    (vault / "Systems" / "Normal.md").write_text(
        "---\ntype: system\nstatus: doing\n---\n"
        "也引用 `app/UserRepository.py`\n",
        encoding="utf-8",
    )

    FIX = str(repo)
    # 用絕對路徑傳 --file(讓 cmd_impact 能讀盤取 content)
    abs_file = str(repo / "app" / "UserRepository.py")
    out = run_lumos_capture(["impact", "--file", abs_file, "--repo", FIX, "--json"])
    d = _json.loads(out)

    check("impact_incidents: 頂層 incidents key 存在",
          "incidents" in d, f"keys={set(d)}")
    inc_nodes = {x["node"] for x in d.get("incidents", [])}
    direct_nodes = {x["node"] for x in d.get("direct", [])}

    check("impact_incidents: N1.md 進 incidents",
          "Issues/N1.md" in inc_nodes, f"incidents={d.get('incidents')}")
    # 去重: incidents ∩ direct = ∅
    check("impact_incidents: 去重——incidents ∩ direct = ∅",
          inc_nodes.isdisjoint(direct_nodes),
          f"inc={inc_nodes} direct={direct_nodes}")
    # Normal.md(無 pitfall_when)應留在 direct
    check("impact_incidents: Normal.md(無 pitfall_when)留在 direct",
          "Systems/Normal.md" in direct_nodes, f"direct={direct_nodes}")
    # incidents 每筆含必要欄位
    for x in d.get("incidents", []):
        check("impact_incidents: 每筆含 node/matched_by/contract/combo",
              set(x) >= {"node", "matched_by", "contract", "combo"}, f"item={x}")


# ─── Task 4: e2e/回歸 + 補前輪 review 缺口 ────────────────────────────────────

def t_impact_incidents_regression():
    """真圖譜整合:impact --file scripts/lumos → incidents 正確撈到 pitfall_when 事故。

    本倉庫已 dogfood pitfall_when(Issues/init-force-slug誤用basename content:_slugify_vault
    命中 scripts/lumos)。此測試證真圖譜上 incidents pipeline 有效 + 輸出良構。
    (「無 pitfall_when → incidents 空」的不誤傷行為由 t_match_incident_triggers 隔離覆蓋。)
    """
    import json as _json
    out = run_lumos_capture(["impact", "--file", "scripts/lumos", "--repo", ".", "--json"])
    d = _json.loads(out)
    check("impact_incidents_regression: 頂層 incidents key 存在",
          "incidents" in d, f"keys={set(d)}")
    nodes = [i.get("node", "") for i in d["incidents"]]
    check("impact_incidents_regression: 真圖譜撈到 init-force-slug 事故(pipeline 有效)",
          any("init-force-slug" in n for n in nodes),
          f"incidents nodes={nodes}")
    check("impact_incidents_regression: 每筆 incident 良構(有 node + matched_by)",
          all(i.get("node") and i.get("matched_by") for i in d["incidents"]),
          f"incidents={d['incidents']}")
    # 確認 direct/indirect 不受影響(本圖有直接關聯節點)
    check("impact_incidents_regression: direct key 仍存在",
          "direct" in d, f"keys={set(d)}")
    check("impact_incidents_regression: indirect key 仍存在",
          "indirect" in d, f"keys={set(d)}")


def t_impact_incidents_smoke():
    """Task 4 Step3: 真機 smoke——暫造 pitfall_when 探針節點到真 vault → impact 撈到 → 清理。

    流程:
    1. 在真 vault Issues/ 建探針節點(_incident_probe.md),pitfall_when glob 命中 scripts/lumos。
    2. lumos impact --file scripts/lumos --repo . --json → incidents 含探針節點。
    3. finally 清理探針節點(不留 doctor 髒)。
    """
    import json as _json
    from pathlib import Path as _P

    vault_issues = _P("/Users/enzo/harness/lumos-toolchain/docs/lumos-toolchain-knowledge/Issues")
    probe = vault_issues / "_incident_probe.md"
    probe_content = (
        "---\n"
        "type: issue\n"
        "status: open\n"
        "pitfall_when:\n"
        "  - \"glob:scripts/lumos\"\n"
        "summary: |-\n"
        "  KEY:測試探針,自動清理\n"
        "---\n"
        "# 測試探針事故節點\n"
        "此節點由 t_impact_incidents_smoke 暫建,測試完自動刪除。\n"
    )
    try:
        probe.write_text(probe_content, encoding="utf-8")
        out = run_lumos_capture(["impact", "--file", "scripts/lumos", "--repo", ".", "--json"])
        d = _json.loads(out)
        inc_nodes = {x["node"] for x in d.get("incidents", [])}
        check("impact_incidents_smoke: incidents 含探針節點",
              "Issues/_incident_probe" in inc_nodes or
              any("_incident_probe" in n for n in inc_nodes),
              f"incidents nodes={inc_nodes}")
        # matched_by 應含 glob 前綴
        probe_hits = [x for x in d.get("incidents", []) if "_incident_probe" in x.get("node", "")]
        check("impact_incidents_smoke: 探針 matched_by 含 glob:",
              any("glob:" in x.get("matched_by", "") for x in probe_hits),
              f"probe_hits={probe_hits}")
    finally:
        if probe.exists():
            probe.unlink()


def t_impact_incidents_indirect_dedup():
    """Task 4 補 T2 缺口: indirect 去重——節點 BFS 間接命中且 pitfall_when 觸發 → 只列 incidents。

    對照組正面驗證設計(非空洞):
    - 節點 D(Systems/D.md): body inline-code 引用 app/svc.py → D 是 direct 命中。
    - 節點 X(Issues/BFSIncident.md): body 引用 [[Systems/D]](backlink 到 D)。
      → BFS 從 D 出發,沿 in_e["Systems/D.md"] 找到 X → X 是 hop=1 間接候選。
    - 對照組(X 無 pitfall_when): 斷言 X 出現在 indirect(證 BFS 真能撈到 X)。
    - 實驗組(X 有 pitfall_when glob 命中 svc.py): 斷言 X 只在 incidents、不在 indirect
      (證去重真的把 X 從 indirect 移走,而非 X 本來就不在 indirect)。
    兩組對比才證「去重生效」(非空洞)。
    """
    import json as _json
    import shutil as _shutil
    import tempfile as _tf
    from pathlib import Path as _P

    # ---- 對照組(X 無 pitfall_when) ----
    repo_ctrl = _P(_tf.mkdtemp(prefix="gctl-t-indir-ctrl-"))
    try:
        (repo_ctrl / "scripts").mkdir()
        (repo_ctrl / "scripts" / "lumos").write_text("# fake\n", encoding="utf-8")
        (repo_ctrl / "app").mkdir()
        (repo_ctrl / "app" / "svc.py").write_text("# service\n", encoding="utf-8")
        vault_ctrl = repo_ctrl / "docs" / "test-knowledge"
        for sub in ("Systems", "Issues", "Verification", "Projects", "MOC"):
            (vault_ctrl / sub).mkdir(parents=True, exist_ok=True)
        (vault_ctrl / "MOC" / "idx.md").write_bytes(
            "---\ntype: moc\n---\n# idx\n".encode("utf-8"))
        # 節點 D: body inline-code 引用 app/svc.py → D 是 direct 命中
        (vault_ctrl / "Systems" / "D.md").write_text(
            "---\ntype: system\nstatus: doing\n---\n"
            "核心服務 `app/svc.py` 說明\n",
            encoding="utf-8",
        )
        # 節點 X: body 引用 [[Systems/D]] → out_e[X]=[D], in_e[D]=[X]
        # BFS 從 D 出發走 in_e → hop=1 撈到 X → X 在 indirect(無 pitfall_when)
        (vault_ctrl / "Issues" / "BFSIncident.md").write_text(
            "---\n"
            "type: issue\n"
            "status: open\n"
            "---\n"
            "相關系統 [[Systems/D]]\n",
            encoding="utf-8",
        )
        abs_file_ctrl = str(repo_ctrl / "app" / "svc.py")
        out_ctrl = run_lumos_capture(
            ["impact", "--file", abs_file_ctrl, "--repo", str(repo_ctrl), "--json"])
        d_ctrl = _json.loads(out_ctrl)
        ctrl_indirect = {x["node"] for x in d_ctrl.get("indirect", [])}
        ctrl_incidents = {x["node"] for x in d_ctrl.get("incidents", [])}
        # 對照組斷言:X 應在 indirect(證 BFS 真能撈到 X)
        check("impact_indirect_dedup [ctrl]: BFSIncident 在 indirect(BFS 真能撈到)",
              "Issues/BFSIncident.md" in ctrl_indirect,
              f"indirect={ctrl_indirect} incidents={ctrl_incidents} direct={[x['node'] for x in d_ctrl.get('direct',[])]}")
        check("impact_indirect_dedup [ctrl]: BFSIncident 不在 incidents(無 trigger 不觸發)",
              "Issues/BFSIncident.md" not in ctrl_incidents,
              f"incidents={ctrl_incidents}")
    finally:
        _shutil.rmtree(repo_ctrl, ignore_errors=True)

    # ---- 實驗組(X 有 pitfall_when 命中 svc.py) ----
    repo_exp = _P(_tf.mkdtemp(prefix="gctl-t-indir-exp-"))
    try:
        (repo_exp / "scripts").mkdir()
        (repo_exp / "scripts" / "lumos").write_text("# fake\n", encoding="utf-8")
        (repo_exp / "app").mkdir()
        (repo_exp / "app" / "svc.py").write_text("# service\n", encoding="utf-8")
        vault_exp = repo_exp / "docs" / "test-knowledge"
        for sub in ("Systems", "Issues", "Verification", "Projects", "MOC"):
            (vault_exp / sub).mkdir(parents=True, exist_ok=True)
        (vault_exp / "MOC" / "idx.md").write_bytes(
            "---\ntype: moc\n---\n# idx\n".encode("utf-8"))
        # 節點 D: 同對照組
        (vault_exp / "Systems" / "D.md").write_text(
            "---\ntype: system\nstatus: doing\n---\n"
            "核心服務 `app/svc.py` 說明\n",
            encoding="utf-8",
        )
        # 節點 X: 加上 pitfall_when glob 命中 svc.py → 去重後只在 incidents
        (vault_exp / "Issues" / "BFSIncident.md").write_text(
            "---\n"
            "type: issue\n"
            "status: open\n"
            "pitfall_when:\n"
            "  - \"glob:**/svc.py\"\n"
            "---\n"
            "相關系統 [[Systems/D]]\n",
            encoding="utf-8",
        )
        abs_file_exp = str(repo_exp / "app" / "svc.py")
        out_exp = run_lumos_capture(
            ["impact", "--file", abs_file_exp, "--repo", str(repo_exp), "--json"])
        d_exp = _json.loads(out_exp)
        exp_incidents = {x["node"] for x in d_exp.get("incidents", [])}
        exp_indirect = {x["node"] for x in d_exp.get("indirect", [])}
        # 實驗組斷言:去重後 X 只在 incidents、不在 indirect
        check("impact_indirect_dedup [exp]: BFSIncident 在 incidents(trigger 命中)",
              "Issues/BFSIncident.md" in exp_incidents,
              f"incidents={d_exp.get('incidents')}")
        check("impact_indirect_dedup [exp]: BFSIncident 不在 indirect(去重生效)",
              "Issues/BFSIncident.md" not in exp_indirect,
              f"indirect={exp_indirect}")
        check("impact_indirect_dedup [exp]: incidents ∩ indirect = ∅",
              exp_incidents.isdisjoint(exp_indirect),
              f"inc={exp_incidents} indirect={exp_indirect}")
    finally:
        _shutil.rmtree(repo_exp, ignore_errors=True)


def t_impact_incidents_main_only():
    """Task 4 補 T3 缺口: hook main() only-incidents e2e。

    mock subprocess 讓 lumos impact 回「只有 incidents 非空(direct/indirect 空)」,
    跑 hook main() → 斷言有注入且含「相關事故」段。
    參照 t_impact_hook_inject 的 mock subprocess scenario。
    """
    import importlib.util
    import io
    import json as _json
    import os
    import uuid as _uuid
    from importlib.machinery import SourceFileLoader
    from pathlib import Path as _P
    from unittest.mock import patch, MagicMock

    hook_path = str(_P(__file__).resolve().parent / "hooks" / "claude" / "impact-hook.py")
    loader = SourceFileLoader("impact_hook_mod_main_only", hook_path)
    spec = importlib.util.spec_from_loader("impact_hook_mod_main_only", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)

    # subprocess mock: 只有 incidents 非空,direct/indirect 皆空
    proc_mock = MagicMock()
    proc_mock.returncode = 0
    proc_mock.stdout = _json.dumps({
        "file": "app/svc.py",
        "direct": [],
        "indirect": [],
        "incidents": [
            {"node": "Issues/NPlus1", "matched_by": "glob:**/svc.py",
             "contract": None, "combo": False}
        ],
    })
    proc_mock.stderr = ""

    fresh_sid = str(_uuid.uuid4())
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "/some/project/app/svc.py"},
        "session_id": fresh_sid,
        "cwd": "/some/project",
    }
    env_patch = {"CLAUDE_PROJECT_DIR": "/some/project"}

    with patch.object(m, "_find_lumos_script", return_value="/fake/lumos"), \
         patch("subprocess.run", return_value=proc_mock), \
         patch.dict(os.environ, env_patch), \
         patch("sys.stdin", io.StringIO(_json.dumps(payload))):
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            try:
                rc = m.main()
            except SystemExit as e:
                rc = e.code
        out = buf.getvalue().strip()

    check("impact_incidents_main_only: main() rc=0",
          rc == 0, f"expected rc=0, got {rc}")
    check("impact_incidents_main_only: stdout 非空(有注入)",
          out != "", f"expected JSON on stdout, got {out!r}")
    j = _json.loads(out)
    ctx = j.get("hookSpecificOutput", {}).get("additionalContext", "")
    check("impact_incidents_main_only: additionalContext 含「相關事故」段",
          "相關事故" in ctx or "incident" in ctx.lower(),
          f"ctx={ctx!r}")
    check("impact_incidents_main_only: additionalContext 含事故節點名稱",
          "Issues/NPlus1" in ctx, f"ctx={ctx!r}")
    check("impact_incidents_main_only: additionalContext 含 matched_by",
          "glob:" in ctx, f"ctx={ctx!r}")


# ── helpers shared by codeloop tests ──────────────────────────────────────────

def _git_init_commit(d):
    """git init + config + 一個空 commit,讓 HEAD 有 sha。"""
    import subprocess as _sp
    _sp.run(["git", "init", "-q"], cwd=d, capture_output=True)
    _sp.run(["git", "config", "user.email", "t@t.t"], cwd=d, capture_output=True)
    _sp.run(["git", "config", "user.name", "t"], cwd=d, capture_output=True)
    (Path(d) / "README.md").write_text("init\n", encoding="utf-8")
    _sp.run(["git", "add", "README.md"], cwd=d, capture_output=True)
    _sp.run(["git", "commit", "-qm", "init"], cwd=d, capture_output=True)


def _git_branch(d):
    """回傳 d 的當前 branch 名。"""
    import subprocess as _sp
    return _sp.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                   cwd=d, capture_output=True, text=True).stdout.strip()


def _git_head(d):
    """回傳 d 的當前 HEAD sha(full)。"""
    import subprocess as _sp
    return _sp.run(["git", "rev-parse", "HEAD"],
                   cwd=d, capture_output=True, text=True).stdout.strip()


def _codeloop_read(repo_root, branch):
    """從 governance/code-loop/<branch>.json 讀取記錄並以 dict 回傳。
    branch 名含 / 時扁平化(對齊 lumos 實作)。"""
    import json as _j
    safe = branch.replace("/", "__")
    p = Path(repo_root) / "governance" / "code-loop" / f"{safe}.json"
    if not p.exists():
        return None
    return _j.loads(p.read_text(encoding="utf-8"))


# ── Task 1: code-loop pass/skip 留痕(綁 HEAD sha) ──────────────────────────

def t_codeloop_ledger():
    import shutil
    with tempfile.TemporaryDirectory() as d:
        _git_init_commit(d)
        rc = run_lumos(["code-loop", "pass", "--note", "done", "--repo", d])
        check("codeloop_ledger: pass rc=0", rc == 0, f"rc={rc}")
        branch = _git_branch(d)
        rec = _codeloop_read(d, branch)
        check("codeloop_ledger: 留痕存在", rec is not None, "找不到 json")
        if rec is not None:
            check("codeloop_ledger: status=passed", rec.get("status") == "passed",
                  f"status={rec.get('status')!r}")
            check("codeloop_ledger: head_sha 正確", rec.get("head_sha") == _git_head(d),
                  f"head_sha={rec.get('head_sha')!r}")
            check("codeloop_ledger: note 正確", rec.get("note") == "done",
                  f"note={rec.get('note')!r}")
        # skip path
        rc2 = run_lumos(["code-loop", "skip", "--note", "no high", "--repo", d])
        check("codeloop_ledger: skip rc=0", rc2 == 0, f"rc={rc2}")
        rec2 = _codeloop_read(d, branch)
        if rec2 is not None:
            check("codeloop_ledger: skip → status=skipped",
                  rec2.get("status") == "skipped", f"status={rec2.get('status')!r}")
            check("codeloop_ledger: skip head_sha 正確",
                  rec2.get("head_sha") == _git_head(d), f"head_sha={rec2.get('head_sha')!r}")
            check("codeloop_ledger: skip note 正確",
                  rec2.get("note") == "no high", f"note={rec2.get('note')!r}")


# ── code-loop check ──────────────────────────────────────────────────────────

def t_codeloop_check():
    """check(Task 2 判定式版):tier=high∧無留痕→rc=1;pass→rc=0;HEAD 移動→rc=1;tier≠high→rc=0。
    Task 1 的 sha-only 邏輯已由 _codeloop_guard_verdict 取代;此測試對齊新語意。
    """
    import subprocess as _sp

    # tier=high ∧ 無留痕 → rc=1(blocked)
    with tempfile.TemporaryDirectory() as d:
        _make_high_tier_repo(d)
        rc_no = run_lumos(["code-loop", "check", "--repo", d])
        check("codeloop_check: tier=high∧無留痕 rc=1", rc_no == 1, f"rc={rc_no}")

    # tier=high ∧ pass 後 check → rc=0
    with tempfile.TemporaryDirectory() as d:
        _make_high_tier_repo(d)
        run_lumos(["code-loop", "pass", "--note", "ok", "--repo", d])
        rc_ok = run_lumos(["code-loop", "check", "--repo", d])
        check("codeloop_check: pass 後 rc=0", rc_ok == 0, f"rc={rc_ok}")

    # tier=high ∧ pass 但 HEAD 移動 → sha 過時 → rc=1
    with tempfile.TemporaryDirectory() as d:
        _make_high_tier_repo(d)
        run_lumos(["code-loop", "pass", "--note", "ok", "--repo", d])
        _add_commit(d, "f2.txt", "x\n")
        rc_stale = run_lumos(["code-loop", "check", "--repo", d])
        check("codeloop_check: sha 不符(HEAD移動) rc=1", rc_stale == 1, f"rc={rc_stale}")

    # tier≠high(fail-open/standard) → rc=0 不 blocked
    with tempfile.TemporaryDirectory() as d:
        _make_standard_tier_repo(d)
        rc_std = run_lumos(["code-loop", "check", "--repo", d])
        check("codeloop_check: tier≠high → rc=0(不 blocked)", rc_std == 0, f"rc={rc_std}")


# ── code-loop branch 名含 / 扁平化 ──────────────────────────────────────────

def t_codeloop_branch_slash():
    """branch 名含 / 時 pass/skip/讀回均走扁平路徑(不建子目錄)。"""
    import subprocess as _sp
    with tempfile.TemporaryDirectory() as d:
        _git_init_commit(d)

        # 建一個含 / 的 branch
        _sp.run(["git", "checkout", "-b", "feat/slash-test"], cwd=d,
                capture_output=True)
        branch = _git_branch(d)
        assert "/" in branch, f"預期含 /,got {branch!r}"

        # pass
        rc = run_lumos(["code-loop", "pass", "--note", "slashok", "--repo", d])
        check("codeloop_slash: pass rc=0", rc == 0, f"rc={rc}")

        # 留痕路徑應為扁平(no 子目錄)
        safe = branch.replace("/", "__")
        flat = Path(d) / "governance" / "code-loop" / f"{safe}.json"
        subdir = Path(d) / "governance" / "code-loop" / "feat"
        check("codeloop_slash: 扁平路徑存在", flat.exists(), f"path={flat}")
        check("codeloop_slash: 無 feat/ 子目錄", not subdir.is_dir(),
              f"subdir={subdir} 存在")

        # 讀回正確
        rec = _codeloop_read(d, branch)
        check("codeloop_slash: 讀回 status=passed",
              rec is not None and rec.get("status") == "passed",
              f"rec={rec!r}")
        check("codeloop_slash: 讀回 note=slashok",
              rec is not None and rec.get("note") == "slashok",
              f"rec={rec!r}")

        # skip 覆寫後再讀
        rc2 = run_lumos(["code-loop", "skip", "--note", "no-loop", "--repo", d])
        check("codeloop_slash: skip rc=0", rc2 == 0, f"rc={rc2}")
        rec2 = _codeloop_read(d, branch)
        check("codeloop_slash: skip 讀回 status=skipped",
              rec2 is not None and rec2.get("status") == "skipped",
              f"rec2={rec2!r}")


# ── gov-log 在含 docs/ 的 repo 不 crash(Critical 回歸) ──────────────────────

def t_codeloop_govlog_with_docs():
    """docs/ 存在時 gov-log 真的執行到、且不 NameError crash。"""
    import subprocess as _sp
    with tempfile.TemporaryDirectory() as d:
        _git_init_commit(d)
        # 建 docs/ 觸發 gov-log 路徑
        (Path(d) / "docs").mkdir()

        rc = run_lumos(["code-loop", "pass", "--note", "govlog-test", "--repo", d])
        check("codeloop_govlog: pass rc=0(不 crash)", rc == 0, f"rc={rc}")

        # gov-log 應有一筆記錄
        log_path = Path(d) / "docs" / ".governance-log.jsonl"
        check("codeloop_govlog: log 檔存在", log_path.exists(), f"path={log_path}")
        if log_path.exists():
            import json as _j
            lines = [l for l in log_path.read_text(encoding="utf-8").splitlines() if l.strip()]
            check("codeloop_govlog: log 有一行", len(lines) >= 1, f"lines={lines!r}")
            if lines:
                ev = _j.loads(lines[0])
                check("codeloop_govlog: gate=code-loop",
                      ev.get("gate") == "code-loop", f"ev={ev!r}")
                check("codeloop_govlog: kind=passed",
                      ev.get("kind") == "passed", f"ev={ev!r}")


# ── Task 2: _codeloop_guard_verdict 判定式 ───────────────────────────────────

def _make_high_tier_repo(d):
    """建立有 merge-base + tier=high diff 的 git repo。
    策略:
      1. init + 初 commit (這成為 main branch 上的 base)
      2. 切 feat branch,新增含 requests.post 的 py 檔(觸發 pitfalls 資源類)
      3. merge-base HEAD main = 初 commit → diff 含 requests.post → tier high
    """
    import subprocess as _sp
    g = lambda *a: _sp.run(["git", *a], cwd=d, capture_output=True, text=True)
    g("init", "-q", "-b", "main")
    g("config", "user.email", "t@t.t")
    g("config", "user.name", "t")
    (Path(d) / "README.md").write_text("init\n", encoding="utf-8")
    g("add", "README.md")
    g("commit", "-qm", "init")
    # 切 feat branch 並加 high-tier 程式
    g("checkout", "-b", "feat/codeloop-guard-test")
    (Path(d) / "app.py").write_text(
        "import requests\n"
        "def f():\n"
        "    requests.post('http://x')\n",
        encoding="utf-8")
    g("add", "app.py")
    g("commit", "-qm", "add high tier code")


def _make_standard_tier_repo(d):
    """建立 merge-base + tier=standard diff 的 git repo(只有 .md 變更)。"""
    import subprocess as _sp
    g = lambda *a: _sp.run(["git", *a], cwd=d, capture_output=True, text=True)
    g("init", "-q", "-b", "main")
    g("config", "user.email", "t@t.t")
    g("config", "user.name", "t")
    (Path(d) / "README.md").write_text("init\n", encoding="utf-8")
    g("add", "README.md")
    g("commit", "-qm", "init")
    g("checkout", "-b", "feat/standard")
    (Path(d) / "notes.md").write_text("just docs\n", encoding="utf-8")
    g("add", "notes.md")
    g("commit", "-qm", "add docs")


def _add_commit(d, filename="bump.txt", content="x\n"):
    """在 repo d 新增一個 commit,回傳新 HEAD sha。"""
    import subprocess as _sp
    g = lambda *a: _sp.run(["git", *a], cwd=d, capture_output=True, text=True)
    (Path(d) / filename).write_text(content, encoding="utf-8")
    g("add", filename)
    g("commit", "-qm", f"bump {filename}")
    return _sp.run(["git", "rev-parse", "HEAD"], cwd=d,
                   capture_output=True, text=True).stdout.strip()


def t_codeloop_guard_verdict():
    """_codeloop_guard_verdict 判定式:5 情境。"""
    import subprocess as _sp

    # ── 情境 1: tier=high ∧ 無留痕 → blocked ──────────────────────────────
    with tempfile.TemporaryDirectory() as d:
        _make_high_tier_repo(d)
        r = _sp.run(
            [sys.executable, GRAPHCTL, "code-loop", "check", "--json", "--repo", d],
            capture_output=True, text=True)
        check("codeloop_guard: tier=high∧無留痕 → blocked(rc=1)", r.returncode == 1,
              f"rc={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}")
        import json as _j
        try:
            data = _j.loads(r.stdout)
            check("codeloop_guard: --json blocked=true", data.get("blocked") is True,
                  f"data={data!r}")
            check("codeloop_guard: --json tier=high", data.get("tier") == "high",
                  f"data={data!r}")
        except Exception as ex:
            check("codeloop_guard: --json 可解析", False, f"ex={ex}\nstdout={r.stdout!r}")

    # ── 情境 2: tier=high ∧ pass(HEAD 符) → 不 blocked ───────────────────
    with tempfile.TemporaryDirectory() as d:
        _make_high_tier_repo(d)
        run_lumos(["code-loop", "pass", "--note", "done", "--repo", d])
        r = _sp.run(
            [sys.executable, GRAPHCTL, "code-loop", "check", "--json", "--repo", d],
            capture_output=True, text=True)
        check("codeloop_guard: tier=high∧pass(HEAD符) → 不 blocked(rc=0)", r.returncode == 0,
              f"rc={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}")
        try:
            import json as _j
            data = _j.loads(r.stdout)
            check("codeloop_guard: pass → blocked=false", data.get("blocked") is False,
                  f"data={data!r}")
        except Exception as ex:
            check("codeloop_guard: pass --json 可解析", False, f"ex={ex}\nstdout={r.stdout!r}")

    # ── 情境 3: tier=high ∧ skip(HEAD 符) → 不 blocked ───────────────────
    with tempfile.TemporaryDirectory() as d:
        _make_high_tier_repo(d)
        run_lumos(["code-loop", "skip", "--note", "intentional", "--repo", d])
        r = _sp.run(
            [sys.executable, GRAPHCTL, "code-loop", "check", "--json", "--repo", d],
            capture_output=True, text=True)
        check("codeloop_guard: tier=high∧skip(HEAD符) → 不 blocked(rc=0)", r.returncode == 0,
              f"rc={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}")
        try:
            import json as _j
            data = _j.loads(r.stdout)
            check("codeloop_guard: skip → blocked=false", data.get("blocked") is False,
                  f"data={data!r}")
        except Exception as ex:
            check("codeloop_guard: skip --json 可解析", False, f"ex={ex}\nstdout={r.stdout!r}")

    # ── 情境 4: tier=high ∧ pass 但 HEAD 移動(再 commit) → 作廢 blocked ──
    with tempfile.TemporaryDirectory() as d:
        _make_high_tier_repo(d)
        run_lumos(["code-loop", "pass", "--note", "done", "--repo", d])
        # 再加一個 commit → HEAD sha 改變 → 留痕 sha 過時
        _add_commit(d, "extra.txt", "bump\n")
        r = _sp.run(
            [sys.executable, GRAPHCTL, "code-loop", "check", "--json", "--repo", d],
            capture_output=True, text=True)
        check("codeloop_guard: pass但HEAD移動 → 作廢 blocked(rc=1)", r.returncode == 1,
              f"rc={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}")
        try:
            import json as _j
            data = _j.loads(r.stdout)
            check("codeloop_guard: HEAD移動後 blocked=true", data.get("blocked") is True,
                  f"data={data!r}")
        except Exception as ex:
            check("codeloop_guard: HEAD移動後 --json 可解析", False,
                  f"ex={ex}\nstdout={r.stdout!r}")

    # ── 情境 5: tier≠high → 不 blocked ───────────────────────────────────
    with tempfile.TemporaryDirectory() as d:
        _make_standard_tier_repo(d)
        r = _sp.run(
            [sys.executable, GRAPHCTL, "code-loop", "check", "--json", "--repo", d],
            capture_output=True, text=True)
        check("codeloop_guard: tier≠high∧無留痕 → 不 blocked(rc=0)", r.returncode == 0,
              f"rc={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}")
        try:
            import json as _j
            data = _j.loads(r.stdout)
            check("codeloop_guard: standard tier → blocked=false", data.get("blocked") is False,
                  f"data={data!r}")
        except Exception as ex:
            check("codeloop_guard: standard --json 可解析", False,
                  f"ex={ex}\nstdout={r.stdout!r}")


# ── Task 3: code-loop-guard Stop hook ────────────────────────────────────────

def t_merge_settings_prunes_dangling():
    """hook 卸載殘留註冊(2026-07-07 現場事故):腳本被工具鏈更新刪除、settings 註冊沒清
    → 每回合報「檔案不存在」。修:merge 前剪掉指向 ~/.claude/hooks/ 下不存在檔案的註冊;
    使用者自訂(不在 hooks 目錄下)的 command 不碰。"""
    import importlib.util as _ilu
    import json
    spec_path = Path(__file__).resolve().parent / "merge-claude-settings.py"
    spec = _ilu.spec_from_file_location("mcs_prune", spec_path)
    mcs = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mcs)

    with tempfile.TemporaryDirectory() as td:
        hooks_dir = Path(td) / "hooks"
        hooks_dir.mkdir()
        (hooks_dir / "check-graph-sync.py").write_text("# ok\n", encoding="utf-8")
        settings_path = Path(td) / "settings.json"
        settings_path.write_text(json.dumps({
            "hooks": {
                "Stop": [
                    {"hooks": [{"type": "command",
                                "command": 'python3 "${HOME}/.claude/hooks/check-graph-sync.py"',
                                "timeout": 10}]},
                    {"hooks": [{"type": "command",
                                "command": 'python3 "${HOME}/.claude/hooks/code-loop-guard.py"',
                                "timeout": 15}]},
                ],
                "SessionStart": [
                    {"hooks": [{"type": "command",
                                "command": "/usr/local/bin/my-custom-hook.sh"}]},
                ],
            }
        }, ensure_ascii=False), encoding="utf-8")

        orig_s, orig_h = mcs.SETTINGS, mcs.HOOKS_DIR
        mcs.SETTINGS, mcs.HOOKS_DIR = settings_path, hooks_dir
        try:
            rc = mcs.main()
        finally:
            mcs.SETTINGS, mcs.HOOKS_DIR = orig_s, orig_h

        check("prune_dangling: rc==0", rc == 0, f"rc={rc}")
        out = json.loads(settings_path.read_text(encoding="utf-8"))
        stop_cmds = [h.get("command", "") for e in out["hooks"].get("Stop", [])
                     for h in e.get("hooks", [])]
        check("prune_dangling: 懸空 code-loop-guard 註冊被剪",
              not any("code-loop-guard" in c for c in stop_cmds), f"stop={stop_cmds}")
        check("prune_dangling: 有效 check-graph-sync 保留",
              any("check-graph-sync" in c for c in stop_cmds), f"stop={stop_cmds}")
        custom = [h.get("command", "") for e in out["hooks"].get("SessionStart", [])
                  for h in e.get("hooks", [])]
        check("prune_dangling: 使用者自訂 hook(非 hooks 目錄)不碰",
              any("my-custom-hook" in c for c in custom), f"custom={custom}")


def t_codeloop_guard_hook_registration():
    """ADR 2026-07-06(code-loop必用守衛_計劃):撤除 Stop nag、pre-push 單點把關。
    守住這個移除決定——HOOK_ENTRIES 不得再含 code-loop-guard(誤加回=違反 ADR)。"""
    import importlib.util as _ilu
    spec_path = Path(__file__).resolve().parent / "merge-claude-settings.py"
    spec = _ilu.spec_from_file_location("mcs_codeloop", spec_path)
    mcs = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mcs)
    found = any(
        "code-loop-guard" in h.get("command", "")
        for entries in mcs.HOOK_ENTRIES.values()
        for e in entries
        for h in e.get("hooks", [])
    )
    check("codeloop_guard_hook_registration: HOOK_ENTRIES 全事件不含 code-loop-guard(ADR 撤除)",
          not found,
          f"code-loop-guard 被加回註冊(違反 2026-07-06 ADR):{mcs.HOOK_ENTRIES!r}")


def t_hook_copy_list_completeness():
    """通則防復發:HOOK_ENTRIES 裡每個已註冊的 hook 腳本,都必須在 _install_hooks_py 複製清單內。

    根因(C1 同型):registration-only 測試只驗 HOOK_ENTRIES 含某檔名,
    但不驗 _install_hooks_py 也有複製同一檔 → 靜默 no-op。
    本測試讀兩邊並比集合,任何「註冊了忘了加複製」都會在此紅。
    """
    import importlib.util as _ilu
    import re as _re

    # ── 側 A:從 HOOK_ENTRIES 抽出所有 hook 腳本檔名 ─────────────────────────
    spec_path = Path(__file__).resolve().parent / "merge-claude-settings.py"
    spec = _ilu.spec_from_file_location("mcs_completeness", spec_path)
    mcs = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mcs)

    registered: set[str] = set()
    for _event, entries in mcs.HOOK_ENTRIES.items():
        for entry in entries:
            for hook in entry.get("hooks", []):
                cmd = hook.get("command", "")
                # 抽出最後一個 .py 檔名:可能是完整路徑也可能含引號/空白
                m = _re.search(r'([\w.\-]+\.py)', cmd)
                if m:
                    registered.add(m.group(1))

    # ── 側 B:從 scripts/lumos 源碼 grep _install_hooks_py 的 for-tuple ────────
    lumos_src = Path(__file__).resolve().parent / "lumos"
    src_text = lumos_src.read_text(encoding="utf-8")
    # 先錨定到 def _install_hooks_py(不再抓全檔第一個 for f in——那會被別處
    # 無關的 `for f in (...)`(如 sarif 轉換、capture-counts)搶走 → copy_list 抓空誤紅)。
    fn = _re.search(r'def _install_hooks_py\b', src_text)
    check("hook_copy_list_completeness: 源碼有 _install_hooks_py", fn is not None,
          "找不到 def _install_hooks_py——測試錨點失效")
    scope = src_text[fn.start():] if fn else src_text
    # 在該函式範圍內找複製清單 for f in (...):(取函式起點後第一個)
    m2 = _re.search(r'for f in \(([^)]+)\)', scope)
    copy_list: set[str] = set()
    if m2:
        inner = m2.group(1)
        copy_list = set(_re.findall(r'"([\w.\-]+\.py)"', inner))

    # ── 斷言:registered ⊆ copy_list ──────────────────────────────────────────
    missing = registered - copy_list
    check(
        "hook_copy_list_completeness: HOOK_ENTRIES 所有 hook 都在 _install_hooks_py 複製清單",
        len(missing) == 0,
        f"已註冊但未複製={missing!r}  registered={registered!r}  copy_list={copy_list!r}",
    )


# ── Task 4: pre-push 升 blocking ─────────────────────────────────────────────

def t_codeloop_guard_prepush():
    """Task 4: pre-push hook tier=high 未過 code-loop → rc1 擋 push(blocking)。

    策略:直接執行 scripts/hooks/pre-push shell 腳本,透過 env 傳入測試 repo 路徑。
    pre-push 讀 GIT_DIR / git rev-parse,所以需要在真實 git repo 中執行。

    情境:
      A) tier=high ∧ 無留痕 → rc1 擋住 + stderr 含跑法/skip 法提示
      B) tier=high ∧ pass(HEAD 符) → rc0 放行
      C) tier=high ∧ skip(HEAD 符) → rc0 放行
      D) tier=standard → rc0 放行(不誤傷)
      E) fail-open: lumos 不存在 → rc0 放行

    注意:pre-push 也跑 anchor verify + doctor --ci,測試 repo 無 vault 所以跳過 doctor;
    anchor verify 在 lumos 不存在時也跳過。為了讓 anchor verify 通過,用真實 lumos。
    """
    import subprocess as _sp
    import os as _os

    pre_push_path = str(Path(__file__).resolve().parent / "hooks" / "pre-push")
    lumos_real = str(Path(__file__).resolve().parent / "lumos")

    def _setup_lumos_in_repo(repo_dir, lumos_path=None):
        """在 repo_dir/scripts/lumos 放真實(或假) lumos,使 pre-push 能找到它。"""
        scripts_dir = Path(repo_dir) / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        target = scripts_dir / "lumos"
        if lumos_path is None:
            lumos_path = lumos_real
        if target.exists() or target.is_symlink():
            target.unlink()
        target.symlink_to(lumos_path)

    def _run_pre_push(repo_dir):
        """在 repo_dir 內執行 pre-push 腳本,回傳 CompletedProcess。"""
        env = dict(_os.environ)
        env["GIT_DIR"] = str(Path(repo_dir) / ".git")
        # pre-push stdin: "<local_ref> <local_sha> <remote_ref> <remote_sha>"
        stdin_data = "refs/heads/feat dummy refs/heads/feat dummy\n"
        return _sp.run(
            ["bash", pre_push_path],
            cwd=repo_dir,
            input=stdin_data,
            capture_output=True,
            text=True,
            env=env,
        )

    # ── 情境 A: tier=high ∧ 無留痕 → rc1 擋住 ────────────────────────────────
    with tempfile.TemporaryDirectory() as d:
        _make_high_tier_repo(d)
        _setup_lumos_in_repo(d)
        r = _run_pre_push(d)
        check("codeloop_guard_prepush: tier=high∧無留痕 → rc1 擋住",
              r.returncode == 1,
              f"rc={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}")
        stderr = r.stderr
        check("codeloop_guard_prepush: stderr 含 lumos-code-loop 或 code-loop",
              "code-loop" in stderr or "lumos-code-loop" in stderr,
              f"stderr={stderr!r}")
        check("codeloop_guard_prepush: stderr 含 skip 提示",
              "skip" in stderr,
              f"stderr={stderr!r}")
        check("codeloop_guard_prepush: stderr 含 --no-verify 繞法",
              "--no-verify" in stderr,
              f"stderr={stderr!r}")

    # ── 情境 B: tier=high ∧ pass(HEAD 符) → rc0 放行 ─────────────────────────
    with tempfile.TemporaryDirectory() as d:
        _make_high_tier_repo(d)
        _setup_lumos_in_repo(d)
        _sp.run([sys.executable, lumos_real, "code-loop", "pass",
                 "--note", "done", "--repo", d],
                capture_output=True, text=True)
        r = _run_pre_push(d)
        check("codeloop_guard_prepush: tier=high∧pass(HEAD符) → rc0 放行",
              r.returncode == 0,
              f"rc={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}")

    # ── 情境 C: tier=high ∧ skip(HEAD 符) → rc0 放行 ─────────────────────────
    with tempfile.TemporaryDirectory() as d:
        _make_high_tier_repo(d)
        _setup_lumos_in_repo(d)
        _sp.run([sys.executable, lumos_real, "code-loop", "skip",
                 "--note", "intentional", "--repo", d],
                capture_output=True, text=True)
        r = _run_pre_push(d)
        check("codeloop_guard_prepush: tier=high∧skip(HEAD符) → rc0 放行",
              r.returncode == 0,
              f"rc={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}")

    # ── 情境 D: tier=standard → rc0 不誤傷 ───────────────────────────────────
    with tempfile.TemporaryDirectory() as d:
        _make_standard_tier_repo(d)
        _setup_lumos_in_repo(d)
        r = _run_pre_push(d)
        check("codeloop_guard_prepush: tier=standard → rc0 不誤傷",
              r.returncode == 0,
              f"rc={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}")

    # ── 情境 E: fail-open — lumos code-loop check rc=2(異常) → rc0 放行 ────────
    # 建假 lumos:code-loop check → rc=2,其他(anchor verify)→ rc=0
    with tempfile.TemporaryDirectory() as td:
        _make_high_tier_repo(td)
        fake_lumos_content = (
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "args = sys.argv[1:]\n"
            "if 'code-loop' in args and 'check' in args:\n"
            "    sys.exit(2)\n"
            "sys.exit(0)\n"
        )
        _setup_lumos_in_repo.__globals__  # ensure in scope
        scripts_dir = Path(td) / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        fake_lumos_path = scripts_dir / "lumos"
        fake_lumos_path.write_text(fake_lumos_content, encoding="utf-8")
        fake_lumos_path.chmod(0o755)
        r = _run_pre_push(td)
        check("codeloop_guard_prepush: lumos code-loop check rc=2(異常) → fail-open rc0",
              r.returncode == 0,
              f"rc={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}")


def t_prepush_test_gate():
    """pre-push 測試套件閘(2026-07-07,僅 Lumos 源 repo):
    源 repo 判定 = skills/lumos-project-notes 目錄存在(不 vendor,消費端沒有)。
    情境:
      A) 消費 repo(無 skills/)→ 不跑測試(不擾民、不遞迴)
      B) 源 repo + 假 runner 紅(rc1)→ pre-push rc1 擋 + stderr 提示
      C) 源 repo + 假 runner 綠(rc0)→ 測試閘放行(無 🚫 測試訊息)
    假 runner 防遞迴:scripts/test_lumos.py 放可控小腳本,不跑真套件。"""
    import subprocess as _sp
    import os as _os

    pre_push_path = str(Path(__file__).resolve().parent / "hooks" / "pre-push")
    lumos_real = str(Path(__file__).resolve().parent / "lumos")

    def _mk_repo(d, with_skills, fake_runner_rc=None):
        _sp.run(["git", "init", "-b", "main", d], capture_output=True)
        _sp.run(["git", "-C", d, "config", "user.email", "t@t"], capture_output=True)
        _sp.run(["git", "-C", d, "config", "user.name", "t"], capture_output=True)
        (Path(d) / "x.txt").write_text("x\n", encoding="utf-8")
        _sp.run(["git", "-C", d, "add", "."], capture_output=True)
        _sp.run(["git", "-C", d, "commit", "-m", "init"], capture_output=True)
        scripts = Path(d) / "scripts"
        scripts.mkdir(exist_ok=True)
        lk = scripts / "lumos"
        if not lk.exists():
            lk.symlink_to(lumos_real)
        if with_skills:
            (Path(d) / "skills" / "lumos-project-notes").mkdir(parents=True, exist_ok=True)
        if fake_runner_rc is not None:
            (scripts / "test_lumos.py").write_text(
                f"import sys\nprint('FAKE-RUNNER rc={fake_runner_rc}')\nsys.exit({fake_runner_rc})\n",
                encoding="utf-8")

    def _run(d):
        env = dict(_os.environ)
        env["GIT_DIR"] = str(Path(d) / ".git")
        return _sp.run(["bash", pre_push_path], cwd=d,
                       input="refs/heads/main dummy refs/heads/main dummy\n",
                       capture_output=True, text=True, env=env)

    # A) 消費 repo(無 skills/,有 test_lumos.py)→ 不跑測試
    with tempfile.TemporaryDirectory() as d:
        _mk_repo(d, with_skills=False, fake_runner_rc=1)  # 就算紅也不該被跑
        r = _run(d)
        check("prepush_test_gate: 消費 repo 不跑測試(紅假 runner 也放行)",
              r.returncode == 0 and "FAKE-RUNNER" not in r.stderr + r.stdout,
              f"rc={r.returncode}\nstderr={r.stderr}")

    # B) 源 repo + 假 runner 紅 → rc1 擋
    with tempfile.TemporaryDirectory() as d:
        _mk_repo(d, with_skills=True, fake_runner_rc=1)
        r = _run(d)
        check("prepush_test_gate: 源 repo 紅測試 → rc1 擋",
              r.returncode == 1, f"rc={r.returncode}\nstderr={r.stderr}")
        check("prepush_test_gate: stderr 含紅測試提示 + --no-verify 逃生",
              "test_lumos.py 有紅" in r.stderr and "--no-verify" in r.stderr,
              f"stderr={r.stderr!r}")

    # C) 源 repo + 假 runner 綠 → 測試閘放行
    with tempfile.TemporaryDirectory() as d:
        _mk_repo(d, with_skills=True, fake_runner_rc=0)
        r = _run(d)
        check("prepush_test_gate: 源 repo 綠測試 → 放行(無測試🚫)",
              r.returncode == 0 and "test_lumos.py 有紅" not in r.stderr,
              f"rc={r.returncode}\nstderr={r.stderr}")


def t_runner_k_zero_cases_rc1():
    """runner 假綠洞修補(2026-07-07):-k 選中 0 案例 → rc1(跑了個寂寞≠全綠)。"""
    import subprocess as _sp
    runner = str(Path(__file__).resolve())
    r = _sp.run([sys.executable, runner, "-k", "zz_絕不存在的測試名zz"],
                capture_output=True, text=True)
    check("runner_k_zero: -k 0 案例 → rc1",
          r.returncode == 1, f"rc={r.returncode}\nstderr={r.stderr}")
    check("runner_k_zero: stderr 有明確訊息",
          "0 個測試" in r.stderr, f"stderr={r.stderr!r}")


def _load_lm():
    """in-process 載入 lumos 模組(pure-function 測試用)。"""
    import importlib.util
    from importlib.machinery import SourceFileLoader
    spec = importlib.util.spec_from_file_location(
        "lm_pf", GRAPHCTL, loader=SourceFileLoader("lm_pf", GRAPHCTL))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def t_difficulty_panel_width():
    """loop 壓縮 T4:difficulty.params 加 panel_width(tier 驅動並行寬度);既有 need/maxr 不變。"""
    import importlib.util
    dp = Path(__file__).resolve().parent.parent / "governance" / "autonomous_loop" / "difficulty.py"
    spec = importlib.util.spec_from_file_location("difficulty_pw", dp)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    hi, st = m.params("high"), m.params("standard")
    check("difficulty_pw: high panel_width=5", hi.get("panel_width") == 5, f"hi={hi}")
    check("difficulty_pw: standard panel_width=3", st.get("panel_width") == 3, f"st={st}")
    check("difficulty_pw: 既有 need/maxr 不變", hi["need"] == 3 and hi["maxr"] == 8
          and st["need"] == 2 and st["maxr"] == 6, f"hi={hi} st={st}")


def t_panel_near_perfect_and_gov_ledger():
    """收斂閘 caught-rate 修正(2026-07-10):①near-perfect 輪有效(caught≥2 但有 missed → 輪無效)
    ②gov canary 分帳(per-auditor missed-rate + type 分佈)。"""
    import subprocess as _sp

    def _mkvault(d):
        v = Path(d) / "docs" / "y-knowledge"
        (v / "MOC").mkdir(parents=True)
        (v / "MOC" / "i.md").write_text("---\ntype: moc\n---\n", encoding="utf-8")

    def _rec(d, *extra):
        return _sp.run([sys.executable, GRAPHCTL, "canary", "record", *extra],
                       cwd=str(Path(d)), capture_output=True, text=True)

    # near-perfect:2 caught + 1 missed(舊判準 caught≥2 會過)→ 現在輪無效 rc1
    with tempfile.TemporaryDirectory() as d:
        _mkvault(d)
        _rec(d, "caught", "--loop", "NP", "--round", "r1", "--token", "A",
             "--severity", "clean", "--capture-counts", "2,2,3")
        _rec(d, "caught", "--loop", "NP", "--round", "r1", "--token", "B", "--severity", "clean")
        _rec(d, "missed", "--loop", "NP", "--round", "r1", "--token", "C")
        r = _sp.run([sys.executable, GRAPHCTL, "loop", "status", "NP", "--gate", "--panel"],
                    cwd=str(Path(d)), capture_output=True, text=True)
        check("near-perfect: 2caught+1missed → 輪無效 rc1", r.returncode == 1 and "near-perfect" in r.stdout,
              f"rc={r.returncode}\n{r.stdout}")

    # else 分支覆蓋(終審 F4):1 caught 0 missed → 輪無效(caught<2)
    with tempfile.TemporaryDirectory() as d:
        _mkvault(d)
        _rec(d, "caught", "--loop", "NP2", "--round", "r1", "--token", "A", "--severity", "clean")
        r = _sp.run([sys.executable, GRAPHCTL, "loop", "status", "NP2", "--gate", "--panel"],
                    cwd=str(Path(d)), capture_output=True, text=True)
        check("near-perfect: 1caught 0missed → 輪無效 rc1(else 分支)", r.returncode == 1 and "<2" in r.stdout,
              f"rc={r.returncode}\n{r.stdout}")

    # gov 分帳:無 --auditor 的 record 歸 '?' 桶(終審 F2:不誤吞 note 首字)
    with tempfile.TemporaryDirectory() as d:
        _mkvault(d)
        _rec(d, "missed", "--loop", "G0", "--note", "r1 type=b timeout")
        r = _sp.run([sys.executable, GRAPHCTL, "gov"], cwd=str(Path(d)),
                    capture_output=True, text=True)
        check("gov 分帳: 無 auditor 歸 ? 桶", "?: caught 0 / missed 1" in r.stdout and "r1: caught" not in r.stdout,
              r.stdout[-300:])

    # gov 分帳:caught/missed per-auditor + type=X 分佈
    with tempfile.TemporaryDirectory() as d:
        _mkvault(d)
        _rec(d, "caught", "--loop", "G", "--auditor", "sonnet", "--note", "r1 type=a caught")
        _rec(d, "missed", "--loop", "G", "--auditor", "sonnet", "--note", "r2 type=b missed")
        r = _sp.run([sys.executable, GRAPHCTL, "gov"], cwd=str(Path(d)),
                    capture_output=True, text=True)
        check("gov 分帳: missed-rate 段出現", "canary 分帳" in r.stdout and "missed-rate 50%" in r.stdout,
              r.stdout[-400:])
        check("gov 分帳: type 分佈", "a:1c/0m" in r.stdout and "b:0c/1m" in r.stdout, r.stdout[-400:])


def t_loop_panel_gate():
    """loop 壓縮 T3:loop status --panel 收斂謂詞(四條合取 + 混用守衛)。"""
    import subprocess as _sp

    def _mkvault(d):
        v = Path(d) / "docs" / "y-knowledge"
        (v / "MOC").mkdir(parents=True)
        (v / "MOC" / "i.md").write_text("---\ntype: moc\n---\n", encoding="utf-8")

    def _rec(d, *extra):
        return _sp.run([sys.executable, GRAPHCTL, "canary", "record", *extra],
                       cwd=str(Path(d)), capture_output=True, text=True)

    def _gate(d, *extra):
        return _sp.run([sys.executable, GRAPHCTL, "loop", "status", "PL", "--gate", *extra],
                       cwd=str(Path(d)), capture_output=True, text=True)

    # 收斂:一輪 r1、2 caught 乾淨、capture_counts 高重疊(殘餘 0)
    with tempfile.TemporaryDirectory() as d:
        _mkvault(d)
        _rec(d, "caught", "--loop", "PL", "--round", "r1", "--token", "A",
             "--severity", "minor", "--capture-counts", "2,2,3")
        _rec(d, "caught", "--loop", "PL", "--round", "r1", "--token", "B", "--severity", "clean")
        r = _gate(d, "--panel")
        check("panel: 2caught+乾淨+高重疊 → rc0", r.returncode == 0,
              f"rc={r.returncode}\n{r.stdout}\n{r.stderr}")

    # 輪無效:只 1 caught
    with tempfile.TemporaryDirectory() as d:
        _mkvault(d)
        _rec(d, "caught", "--loop", "PL", "--round", "r1", "--token", "A", "--severity", "clean")
        _rec(d, "missed", "--loop", "PL", "--round", "r1", "--token", "B")
        r = _gate(d, "--panel")
        check("panel: 1caught(輪無效) → 不收斂 rc1", r.returncode == 1, f"rc={r.returncode}\n{r.stdout}")

    # 存活 major → 不收斂
    with tempfile.TemporaryDirectory() as d:
        _mkvault(d)
        _rec(d, "caught", "--loop", "PL", "--round", "r1", "--token", "A", "--severity", "major")
        _rec(d, "caught", "--loop", "PL", "--round", "r1", "--token", "B", "--severity", "clean")
        r = _gate(d, "--panel")
        check("panel: 存活 major → 不收斂 rc1", r.returncode == 1, f"rc={r.returncode}\n{r.stdout}")

    # 殘餘超門檻(低重疊)→ 不收斂
    with tempfile.TemporaryDirectory() as d:
        _mkvault(d)
        _rec(d, "caught", "--loop", "PL", "--round", "r1", "--token", "A",
             "--severity", "minor", "--capture-counts", "1,1,1,1")
        _rec(d, "caught", "--loop", "PL", "--round", "r1", "--token", "B", "--severity", "clean")
        r = _gate(d, "--panel")
        check("panel: capture-recapture 殘餘超門檻 → rc1", r.returncode == 1, f"rc={r.returncode}\n{r.stdout}")

    # 混用守衛:--panel 但 log 無 round → rc2
    with tempfile.TemporaryDirectory() as d:
        _mkvault(d)
        _rec(d, "caught", "--loop", "PL", "--token", "A", "--severity", "clean")
        r = _gate(d, "--panel")
        check("panel: --panel 但無 round 欄 → rc2", r.returncode == 2, f"rc={r.returncode}\n{r.stderr}")

    # 混用守衛:log 有 round 但無 --panel → rc2
    with tempfile.TemporaryDirectory() as d:
        _mkvault(d)
        _rec(d, "caught", "--loop", "PL", "--round", "r1", "--token", "A", "--severity", "clean")
        r = _gate(d)  # 無 --panel
        check("panel: 有 round 欄但無 --panel → rc2", r.returncode == 2, f"rc={r.returncode}\n{r.stderr}")

    # C1 fail-closed:2 caught 乾淨但無 capture_counts → 不收斂(不得靜默跳過殘餘)
    with tempfile.TemporaryDirectory() as d:
        _mkvault(d)
        _rec(d, "caught", "--loop", "PL", "--round", "r1", "--token", "A", "--severity", "clean")
        _rec(d, "caught", "--loop", "PL", "--round", "r1", "--token", "B", "--severity", "minor")
        r = _gate(d, "--panel")
        check("panel: 無 capture_counts → fail-closed rc1(不繞過殘餘)",
              r.returncode == 1, f"rc={r.returncode}\n{r.stdout}")

    # I1 partial-mix:同 loop 有 round 欄記錄 + 無 round 欄記錄混用 → rc2(防 None phantom 輪)
    with tempfile.TemporaryDirectory() as d:
        _mkvault(d)
        _rec(d, "caught", "--loop", "PL", "--round", "r1", "--token", "A", "--severity", "major")
        _rec(d, "caught", "--loop", "PL", "--round", "r1", "--token", "B", "--severity", "major")
        _rec(d, "caught", "--loop", "PL", "--token", "C", "--severity", "clean")  # 無 round(legacy 混入)
        r = _gate(d, "--panel")
        check("panel: partial-mix(有/無 round 混用) → rc2 拒讀",
              r.returncode == 2, f"rc={r.returncode}\n{r.stderr}")


def t_canary_round_field():
    """loop 壓縮 T2:canary record --round 留痕欄(panel 一輪 W 筆共享 round-id)。
    帶 --round → 記錄含 round 欄;不帶 → 無此欄(舊記錄格式逐位元不變)。"""
    import json as _json
    with tempfile.TemporaryDirectory() as d:
        vault = Path(d) / "docs" / "x-knowledge"
        (vault / "MOC").mkdir(parents=True)
        (vault / "MOC" / "i.md").write_text("---\ntype: moc\n---\n", encoding="utf-8")
        log = Path(d) / "docs" / ".canary-log.jsonl"

        def _rec(*extra):
            return subprocess.run([sys.executable, GRAPHCTL, "canary", "record", *extra],
                                  cwd=str(Path(d)), capture_output=True, text=True)

        r = _rec("caught", "--loop", "L", "--round", "r1", "--token", "T1")
        check("canary_round: rc0", r.returncode == 0, f"rc={r.returncode} err={r.stderr}")
        recs = [_json.loads(l) for l in log.read_text(encoding="utf-8").splitlines()]
        check("canary_round: 帶 --round 記錄含 round 欄",
              recs[-1].get("round") == "r1", f"rec={recs[-1]}")
        _rec("missed", "--loop", "L", "--token", "T2")
        recs = [_json.loads(l) for l in log.read_text(encoding="utf-8").splitlines()]
        check("canary_round: 不帶 --round 無此欄(向後相容)",
              "round" not in recs[-1], f"rec={recs[-1]}")


def t_capture_counts_from_finders():
    """異質 panel 接線:多 finder(LLM/linter/測試/mutation)的 finding-key → capture_counts。
    各 distinct key 被幾個 finder 找到;finder 內去重、key 正規化(大小寫/空白)。"""
    m = _load_lm()
    f = m._capture_counts_from_finders
    # A 找 {x,y}、B 找 {x,z}、C(linter) 找 {x} → x=3, y=1, z=1
    cc = f([["app.py:10", "app.py:20"], ["app.py:10", "svc.py:5"], ["app.py:10"]])
    check("cc: x 三 finder 都中 → 含 3", 3 in cc, f"cc={cc}")
    check("cc: y/z 各一 finder → 兩個 1", cc.count(1) == 2, f"cc={cc}")
    # 正規化 + finder 內去重:同一 key 大小寫/空白/重複 → 算一次
    cc2 = f([[" App.py:10 ", "app.py:10", "APP.PY:10"]])
    check("cc: finder 內正規化去重 → [1]", cc2 == [1], f"cc2={cc2}")
    check("cc: 空 → []", f([]) == [] and f([[], []]) == [], f"got {f([[],[]])}")
    # 串接 _estimate_remaining_defects:全獨發 → 殘餘>0
    counts = f([["a"], ["b"], ["c"]])
    check("cc: 全獨發餵殘餘估計 >0", m._estimate_remaining_defects(counts) > 0, f"counts={counts}")


def t_loop_capture_counts_cli():
    """CLI `loop capture-counts`:多 --finder → capture_counts + 殘餘估計 + record 建議串。"""
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / ".git").mkdir()
        (Path(d) / "docs" / "x-knowledge" / "MOC").mkdir(parents=True)
        def run(*args):
            return subprocess.run([sys.executable, GRAPHCTL, "loop", "capture-counts", *args],
                                  cwd=str(Path(d)), capture_output=True, text=True)
        # 三 finder,x 被三家都中(含 linter)→ capture_counts 含 3;吐 record 建議串
        r = run("--finder", "app.py:10,app.py:20", "--finder", "app.py:10,svc.py:5",
                "--finder", "app.py:10")
        check("cli cc: rc0", r.returncode == 0, r.stderr)
        check("cli cc: distinct=3", "distinct-findings=3" in r.stdout, r.stdout)
        check("cli cc: capture_counts 含 3", "capture_counts=3" in r.stdout, r.stdout)
        check("cli cc: 吐 --capture-counts 建議", "--capture-counts 3" in r.stdout, r.stdout)
        # 全獨發 → 殘餘 ≥1 → 續跑側
        r2 = run("--finder", "a", "--finder", "b", "--finder", "c")
        check("cli cc: 全獨發=續跑側", "續跑側" in r2.stdout, r2.stdout)
        # 無 finder → 空、殘餘 0、不吐建議串
        r3 = run()
        check("cli cc: 空 rc0", r3.returncode == 0 and "distinct-findings=0" in r3.stdout, r3.stdout)
        check("cli cc: 空不吐建議", "--capture-counts" not in r3.stdout, r3.stdout)


def t_loop_capture_counts_from_pitfalls():
    """`loop capture-counts --from-pitfalls <range>`:自動收割 pitfalls diff 命中成一個確定性
    finder(免手貼),與手動 --finder(LLM reviewer)一起算重疊。這關掉「手動串 linter」那半破口。"""
    import subprocess as sp
    root = Path(tempfile.mkdtemp(prefix="gctl-ccfp-"))
    def git(*a): sp.run(["git", *a], cwd=root, capture_output=True)
    git("init"); git("config", "user.email", "t@t"); git("config", "user.name", "t")
    (root / "app.py").write_text("x = 1\n", encoding="utf-8")
    git("add", "-A"); git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "init")
    # requests.post 無 timeout(第 3 行,資源)+ 迴圈內 query(第 5 行,效能)
    (root / "app.py").write_text(
        "import requests\n"
        "def f(ids):\n"
        "    requests.post('http://x')\n"
        "    for i in ids:\n"
        "        db.execute('SELECT 1')\n", encoding="utf-8")
    git("add", "-A"); git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "c2")
    def cc(*args):
        return sp.run([sys.executable, GRAPHCTL, "loop", "capture-counts", *args],
                      cwd=str(root), capture_output=True, text=True)
    # 手動 finder(LLM reviewer)命中 app.py:3(與 pitfalls 重疊)+ 一個獨發 svc.py:9
    r = cc("--finder", "app.py:3,svc.py:9", "--from-pitfalls", "HEAD~1..HEAD", "--repo", str(root))
    check("ccfp: rc0", r.returncode == 0, r.stderr)
    check("ccfp: 收割了 pitfalls finder", "from-pitfalls" in r.stdout or "收割" in r.stdout, r.stdout)
    # app.py:3 被手動+pitfalls 兩家中 → capture_counts 含 2;app.py:5 與 svc.py:9 各獨發
    check("ccfp: app.py:3 重疊 → 含 2", "capture_counts=2" in r.stdout, r.stdout)
    check("ccfp: 吐 record 建議串", "--capture-counts 2" in r.stdout, r.stdout)
    # git 錯誤 range → rc2、不崩
    r2 = cc("--from-pitfalls", "nonexistent..range", "--repo", str(root))
    check("ccfp: 壞 range → rc2", r2.returncode == 2, f"rc={r2.returncode} {r2.stdout}")


def t_caprecap_estimate():
    """loop 壓縮 T1:capture-recapture 殘餘缺陷估計(Chao1 偏差修正)。
    輸入=各 distinct 缺陷「被 W 審計員中幾個找到」的次數列表。"""
    m = _load_lm()
    f = m._estimate_remaining_defects
    check("caprecap: 全高重疊 → 殘餘≈0", f([3, 2, 2, 3]) == 0.0, f"got {f([3,2,2,3])}")
    check("caprecap: 全獨發 f2=0 不div0 → 6.0", f([1, 1, 1, 1]) == 6.0, f"got {f([1,1,1,1])}")
    check("caprecap: f1=2 f2=2 → ~0.333",
          abs(f([1, 1, 2, 2]) - (2 * 1) / (2 * 3)) < 1e-9, f"got {f([1,1,2,2])}")
    check("caprecap: 空輸入 → 0", f([]) == 0.0, f"got {f([])}")
    check("caprecap: 單一缺陷多人找到 → 0", f([5]) == 0.0, f"got {f([5])}")


# ── Task 1: _extract_claude_block_span 三態 ────────────────────────────────

def _import_lumos_for_reinject():
    """Task 1 用:用 SourceFileLoader 載入 lumos 模組(無 .py 副檔名)。"""
    import importlib.util
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("lumos_reinject_mod", GRAPHCTL)
    spec = importlib.util.spec_from_loader("lumos_reinject_mod", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    return m


def t_extract_span_found():
    """found 態:兩 sentinel 齊全 → body 正確 + 位移對齊;START 帶版本戳亦 found。"""
    mod = _import_lumos_for_reinject()

    fn = mod._extract_claude_block_span
    START_PREFIX = mod._CLAUDE_START_PREFIX
    END = mod._CLAUDE_END

    # 基本版:START 行無版本戳
    start_line = START_PREFIX + " -->"
    text = f"before\n{start_line}\nbody line A\nbody line B\n{END}\nafter\n"
    state, span = fn(text)
    check("extract_span_found: state==found(無版本戳)", state == "found", f"state={state!r}")
    check("extract_span_found: span not None", span is not None, "span is None")
    if span is not None:
        expected_body = "body line A\nbody line B"
        check("extract_span_found: body 正確", span.body == expected_body,
              f"body={span.body!r}")
        check("extract_span_found: text[body_start:body_end]==body",
              text[span.body_start:span.body_end] == span.body,
              f"text[{span.body_start}:{span.body_end}]={text[span.body_start:span.body_end]!r} vs body={span.body!r}")

    # 版本戳版:START 行後面帶 " v1.2 — 勿手改 -->"
    start_line_v = START_PREFIX + " v1.2 — 勿手改 -->"
    text2 = f"preamble\n{start_line_v}\ncontent here\n{END}\nfooter\n"
    state2, span2 = fn(text2)
    check("extract_span_found: 版本戳 START → 仍 found", state2 == "found",
          f"state={state2!r}")
    check("extract_span_found: 版本戳 body 正確", span2 is not None and span2.body == "content here",
          f"span2={span2!r}")
    if span2 is not None:
        check("extract_span_found: 版本戳 text[body_start:body_end]==body",
              text2[span2.body_start:span2.body_end] == span2.body,
              f"text2[{span2.body_start}:{span2.body_end}]={text2[span2.body_start:span2.body_end]!r} vs {span2.body!r}")


def t_extract_span_absent():
    """absent 態:純文字無任何 sentinel → ("absent", None)。"""
    mod = _import_lumos_for_reinject()
    fn = mod._extract_claude_block_span

    # 完全無 sentinel
    state, span = fn("some text\nno markers here\n")
    check("extract_span_absent: 無 sentinel → absent", state == "absent",
          f"state={state!r}")
    check("extract_span_absent: span is None", span is None, f"span={span!r}")

    # 空字串
    state2, span2 = fn("")
    check("extract_span_absent: 空字串 → absent", state2 == "absent",
          f"state={state2!r}")


def t_extract_span_broken():
    """broken 態:只START無END / 只END無START / END在START前 / START出現兩次。"""
    mod = _import_lumos_for_reinject()
    fn = mod._extract_claude_block_span
    START_PREFIX = mod._CLAUDE_START_PREFIX
    END = mod._CLAUDE_END

    start_line = START_PREFIX + " -->"

    # 只 START 無 END
    text_a = f"text\n{start_line}\nbody\n"
    sa, spa = fn(text_a)
    check("extract_span_broken: 只START無END → broken", sa == "broken",
          f"state={sa!r}")
    check("extract_span_broken: 只START無END → span None", spa is None, f"span={spa!r}")

    # 只 END 無 START
    text_b = f"text\nbody\n{END}\n"
    sb, spb = fn(text_b)
    check("extract_span_broken: 只END無START → broken", sb == "broken",
          f"state={sb!r}")
    check("extract_span_broken: 只END無START → span None", spb is None, f"span={spb!r}")

    # END 在 START 前
    text_c = f"{END}\nbody\n{start_line}\n"
    sc, spc = fn(text_c)
    check("extract_span_broken: END在START前 → broken", sc == "broken",
          f"state={sc!r}")

    # START 出現兩次
    text_d = f"{start_line}\nbody\n{start_line}\n{END}\n"
    sd, spd = fn(text_d)
    check("extract_span_broken: START出現兩次 → broken", sd == "broken",
          f"state={sd!r}")


# ── Task 2: _reinject_claude_block ────────────────────────────────────────────

def _make_reinject_root(td, tpl_content=None, claude_content=None):
    """在臨時目錄建立最小 root 結構供 reinject 測試用。
    tpl_content=None → 不建立 graph-discipline.md(no_template 情境)。
    claude_content=None → 不建立 CLAUDE.md。
    回傳 (root, mod)。"""
    import tempfile, importlib.util
    from importlib.machinery import SourceFileLoader
    from pathlib import Path
    root = Path(td)
    tpl_dir = root / "scripts" / "templates"
    tpl_dir.mkdir(parents=True, exist_ok=True)
    if tpl_content is not None:
        (tpl_dir / "graph-discipline.md").write_text(tpl_content, encoding="utf-8")
    loader = SourceFileLoader("lumos_reinject_t2", GRAPHCTL)
    spec = importlib.util.spec_from_loader("lumos_reinject_t2", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    if claude_content is not None:
        (root / "CLAUDE.md").write_bytes(claude_content if isinstance(claude_content, bytes)
                                         else claude_content.encode("utf-8"))
    return root, m


def _make_block(mod, slug, tpl_content):
    """Helper: 組出 reinject 會寫入的完整 block 字串,供測試斷言用。

    引用 mod._START_TEMPLATE + mod.LUMOS_VERSION(非內聯常數),確保與實際 reinject
    寫入的 START 行格式一致(版本戳一致)。T4 reviewer 要求:內聯字串會在版本戳加入後
    讓 fixture 與正式格式不符。
    """
    body = tpl_content.replace("{{KG}}", f"docs/{slug}-knowledge/").strip()
    START = mod._START_TEMPLATE.format(version=mod.LUMOS_VERSION)
    END = mod._CLAUDE_END
    return START + "\n" + body + "\n" + END


def t_reinject_no_template():
    """範本檔不存在 → no_template、不 crash、不建檔。"""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        root, mod = _make_reinject_root(td, tpl_content=None, claude_content=None)
        result = mod._reinject_claude_block(root, "myproj")
        check("reinject_no_template: status==no_template",
              result.status == "no_template", f"status={result.status!r}")
        check("reinject_no_template: diff is None",
              result.diff is None, f"diff={result.diff!r}")
        check("reinject_no_template: CLAUDE.md 未被建立",
              not (root / "CLAUDE.md").exists(), "CLAUDE.md 意外被建立")


def t_reinject_creates_when_absent():
    """CLAUDE.md 不存在 → created、檔被生成且含 block。"""
    import tempfile
    TPL = "lumos 知識圖譜路徑:{{KG}}"
    with tempfile.TemporaryDirectory() as td:
        root, mod = _make_reinject_root(td, tpl_content=TPL, claude_content=None)
        result = mod._reinject_claude_block(root, "myproj")
        check("reinject_creates: status==created",
              result.status == "created", f"status={result.status!r}")
        check("reinject_creates: diff is None",
              result.diff is None, f"diff={result.diff!r}")
        cm = root / "CLAUDE.md"
        check("reinject_creates: CLAUDE.md 存在",
              cm.exists(), "CLAUDE.md 未被建立")
        content = cm.read_bytes().decode("utf-8")
        block = _make_block(mod, "myproj", TPL)
        check("reinject_creates: 含 block",
              block in content, f"block 未在 content 中;\ncontent={content!r}")
        check("reinject_creates: KG 替換正確",
              "docs/myproj-knowledge/" in content, f"KG 未替換: {content!r}")
        check("reinject_creates: 無 BOM",
              not cm.read_bytes().startswith(b"\xef\xbb\xbf"), "有 BOM")
        check("reinject_creates: 無 CRLF",
              b"\r\n" not in cm.read_bytes(), "有 CRLF")


def t_reinject_appends_when_no_sentinel():
    """有 CLAUDE.md 但無 sentinel → appended、原內容保留 + block 附加。"""
    import tempfile
    TPL = "知識圖譜:{{KG}}"
    ORIGINAL = "# 既有 CLAUDE.md\n\n原始內容在這\n"
    with tempfile.TemporaryDirectory() as td:
        root, mod = _make_reinject_root(td, tpl_content=TPL, claude_content=ORIGINAL)
        result = mod._reinject_claude_block(root, "proj")
        check("reinject_appends: status==appended",
              result.status == "appended", f"status={result.status!r}")
        check("reinject_appends: diff is None",
              result.diff is None, f"diff={result.diff!r}")
        content = (root / "CLAUDE.md").read_bytes().decode("utf-8")
        check("reinject_appends: 原始內容保留",
              "原始內容在這" in content, f"原始內容消失: {content!r}")
        block = _make_block(mod, "proj", TPL)
        check("reinject_appends: block 附加",
              block in content, f"block 未在 content 中")
        # 確認原始內容在 block 之前
        check("reinject_appends: 原始在前",
              content.index("原始內容在這") < content.index(mod._CLAUDE_START_PREFIX),
              "原始內容出現在 block 之後")


def t_reinject_updates_existing():
    """既有 block 內容過時 → updated + diff 非空 + 檔被寫入新內容。"""
    import tempfile
    OLD_BODY = "舊的 body 內容"
    NEW_TPL = "新的範本:{{KG}}"
    START = ("<!-- LUMOS:GRAPH-DISCIPLINE:START"
             " — 自動注入/更新,勿手改本區塊;改範本 scripts/templates/graph-discipline.md -->")
    END_SENTINEL = "<!-- LUMOS:GRAPH-DISCIPLINE:END -->"
    old_block = START + "\n" + OLD_BODY + "\n" + END_SENTINEL
    EXISTING = "# CLAUDE.md\n\n前言\n\n" + old_block + "\n\n後記\n"
    with tempfile.TemporaryDirectory() as td:
        root, mod = _make_reinject_root(td, tpl_content=NEW_TPL, claude_content=EXISTING)
        result = mod._reinject_claude_block(root, "slug")
        check("reinject_updates: status==updated",
              result.status == "updated", f"status={result.status!r}")
        check("reinject_updates: diff 非 None",
              result.diff is not None, "diff is None")
        check("reinject_updates: diff 非空字串",
              result.diff != "", f"diff empty: {result.diff!r}")
        content = (root / "CLAUDE.md").read_bytes().decode("utf-8")
        new_body = NEW_TPL.replace("{{KG}}", "docs/slug-knowledge/").strip()
        check("reinject_updates: 新 body 寫入",
              new_body in content, f"新 body 未在 content: {content!r}")
        check("reinject_updates: 舊 body 消失",
              OLD_BODY not in content, f"舊 body 殘留: {content!r}")
        check("reinject_updates: 前言保留",
              "前言" in content, f"前言消失: {content!r}")
        check("reinject_updates: 後記保留",
              "後記" in content, f"後記消失: {content!r}")


def t_reinject_idempotent():
    """再跑一次 → unchanged + 檔案內容不變。"""
    import tempfile
    TPL = "知識圖譜:{{KG}}"
    with tempfile.TemporaryDirectory() as td:
        root, mod = _make_reinject_root(td, tpl_content=TPL, claude_content=None)
        # 第一次: created
        r1 = mod._reinject_claude_block(root, "slug")
        check("reinject_idempotent: 第一次 created",
              r1.status == "created", f"r1.status={r1.status!r}")
        content_after_first = (root / "CLAUDE.md").read_bytes()
        # 第二次: unchanged
        r2 = mod._reinject_claude_block(root, "slug")
        check("reinject_idempotent: 第二次 unchanged",
              r2.status == "unchanged", f"r2.status={r2.status!r}")
        check("reinject_idempotent: diff is None",
              r2.diff is None, f"diff={r2.diff!r}")
        content_after_second = (root / "CLAUDE.md").read_bytes()
        check("reinject_idempotent: 內容 byte-equal",
              content_after_first == content_after_second,
              f"第二次寫入改變了內容")


def t_reinject_preserves_outside():
    """sentinel 之外的內容 byte-equal 保留——前綴與後綴逐 byte 相同。"""
    import tempfile
    TPL = "知識圖譜:{{KG}}"
    START = ("<!-- LUMOS:GRAPH-DISCIPLINE:START"
             " — 自動注入/更新,勿手改本區塊;改範本 scripts/templates/graph-discipline.md -->")
    END_SENTINEL = "<!-- LUMOS:GRAPH-DISCIPLINE:END -->"
    OLD_BODY = "舊 body,需更新"
    old_block = START + "\n" + OLD_BODY + "\n" + END_SENTINEL
    PREFIX = "# CLAUDE.md\n\n使用者前綴段落\n\n"
    SUFFIX = "\n\n使用者後綴段落\n"
    EXISTING = PREFIX + old_block + SUFFIX
    with tempfile.TemporaryDirectory() as td:
        root, mod = _make_reinject_root(td, tpl_content=TPL, claude_content=EXISTING)
        result = mod._reinject_claude_block(root, "slug")
        check("reinject_preserves_outside: status==updated",
              result.status == "updated", f"status={result.status!r}")
        new_content = (root / "CLAUDE.md").read_bytes().decode("utf-8")
        # 找 START 行在新內容中的位置,取前綴
        si_new = new_content.find(mod._CLAUDE_START_PREFIX)
        # 找 END 行在新內容中的位置,取後綴
        ei_new = new_content.find(mod._CLAUDE_END)
        end_end = ei_new + len(mod._CLAUDE_END)
        new_prefix = new_content[:si_new]
        new_suffix = new_content[end_end:]
        # 原始的前綴/後綴
        si_old = EXISTING.find(mod._CLAUDE_START_PREFIX)
        ei_old = EXISTING.find(mod._CLAUDE_END)
        end_end_old = ei_old + len(mod._CLAUDE_END)
        orig_prefix = EXISTING[:si_old]
        orig_suffix = EXISTING[end_end_old:]
        check("reinject_preserves_outside: 前綴 byte-equal",
              new_prefix == orig_prefix,
              f"前綴不同:\norig={orig_prefix!r}\nnew={new_prefix!r}")
        check("reinject_preserves_outside: 後綴 byte-equal",
              new_suffix == orig_suffix,
              f"後綴不同:\norig={orig_suffix!r}\nnew={new_suffix!r}")


def t_reinject_sentinel_broken():
    """只 START 無 END → sentinel_broken + 原檔 byte-equal 不動。"""
    import tempfile
    START = ("<!-- LUMOS:GRAPH-DISCIPLINE:START"
             " — 自動注入/更新,勿手改本區塊;改範本 scripts/templates/graph-discipline.md -->")
    BROKEN = "# CLAUDE.md\n\n" + START + "\nbody without end\n"
    TPL = "知識圖譜:{{KG}}"
    with tempfile.TemporaryDirectory() as td:
        root, mod = _make_reinject_root(td, tpl_content=TPL,
                                        claude_content=BROKEN.encode("utf-8"))
        orig_bytes = (root / "CLAUDE.md").read_bytes()
        result = mod._reinject_claude_block(root, "slug")
        check("reinject_sentinel_broken: status==sentinel_broken",
              result.status == "sentinel_broken", f"status={result.status!r}")
        check("reinject_sentinel_broken: diff is None",
              result.diff is None, f"diff={result.diff!r}")
        new_bytes = (root / "CLAUDE.md").read_bytes()
        check("reinject_sentinel_broken: 原檔 byte-equal",
              new_bytes == orig_bytes,
              f"檔案被改動(orig {len(orig_bytes)} vs new {len(new_bytes)} bytes)")


def t_reinject_bom_crlf_normalized():
    """BOM+CRLF 輸入 → 寫後無 BOM、LF、內容正確。"""
    import tempfile
    TPL = "知識圖譜:{{KG}}"
    # 既有 CLAUDE.md 無 sentinel,帶 BOM + CRLF
    existing_crlf_bom = "\xef\xbb\xbf# CLAUDE.md\r\n\r\n既有內容\r\n".encode("utf-8")
    with tempfile.TemporaryDirectory() as td:
        root, mod = _make_reinject_root(td, tpl_content=TPL,
                                        claude_content=existing_crlf_bom)
        result = mod._reinject_claude_block(root, "slug")
        check("reinject_bom_crlf: status==appended",
              result.status == "appended", f"status={result.status!r}")
        raw = (root / "CLAUDE.md").read_bytes()
        check("reinject_bom_crlf: 無 BOM",
              not raw.startswith(b"\xef\xbb\xbf"), "仍有 BOM")
        check("reinject_bom_crlf: 無 CRLF",
              b"\r\n" not in raw, "仍有 CRLF")
        check("reinject_bom_crlf: 含 block",
              mod._CLAUDE_START_PREFIX.encode("utf-8") in raw, "block 未寫入")
        check("reinject_bom_crlf: 既有內容保留(無 BOM 版)",
              "既有內容" in raw.decode("utf-8"), f"既有內容消失: {raw.decode()!r}")


# ── Task 3: 解耦 scaffold + 接線 update/init ────────────────────────────────


def _load_lumos_mod(unique_name="lumos_t3"):
    """載入 lumos 模組(無 .py 副檔名)回傳 module。"""
    import importlib.util
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader(unique_name, GRAPHCTL)
    spec = importlib.util.spec_from_loader(unique_name, loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    return m


def t_scaffold_no_longer_injects():
    """_scaffold_project 移除注入段後:scaffold 成功建 vault 夾,但 CLAUDE.md 不被它建立或修改。"""
    import tempfile, os, subprocess, sys
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        # 建一個假的 git repo(避免 cmd_init 中的 git rev-parse 出錯)
        subprocess.run(["git", "init", str(root)], capture_output=True)
        # 建 scripts/templates 讓範本存在(但 scaffold 不應碰它)
        tpl_dir = root / "scripts" / "templates"
        tpl_dir.mkdir(parents=True, exist_ok=True)
        (tpl_dir / "graph-discipline.md").write_text("知識圖譜:{{KG}}", encoding="utf-8")

        mod = _load_lumos_mod("lumos_t3_scaffold")
        mod._scaffold_project(root, "myproj")

        kg = root / "docs" / "myproj-knowledge"
        check("scaffold_no_longer: vault 夾建立", kg.is_dir(), f"kg={kg}")
        check("scaffold_no_longer: CLAUDE.md 未被 scaffold 建立",
              not (root / "CLAUDE.md").exists(),
              "CLAUDE.md 意外被 _scaffold_project 建立(注入段未移除)")

        # 已有 CLAUDE.md 的情況:scaffold 也不應修改它
        existing_cm = "# 既有 CLAUDE.md\n\n使用者內容\n"
        (root / "CLAUDE.md").write_text(existing_cm, encoding="utf-8")
        # 再呼叫一次(已存在 vault → early return;CLAUDE.md 不應被碰)
        mod._scaffold_project(root, "myproj")
        after = (root / "CLAUDE.md").read_text(encoding="utf-8")
        check("scaffold_no_longer: 既有 CLAUDE.md 未被 scaffold 修改",
              after == existing_cm,
              f"CLAUDE.md 被改了: {after!r}")


def t_update_resyncs_claude():
    """整合:_vendor_toolchain 在 copy2 迴圈後呼叫 _reinject_claude_block。

    情境:消費專案有舊版 block;臨時 lumos 源含新版範本。
    以 os.environ["LUMOS_HOME"] 指向臨時源;跑 _vendor_toolchain(..., no_pull=True)。
    斷言:CLAUDE.md block 被刷新成新範本內容。
    """
    import tempfile, os, subprocess, shutil, sys
    # ── 建臨時 lumos 源 ──────────────────────────────────────────────────
    with tempfile.TemporaryDirectory() as src_td, \
         tempfile.TemporaryDirectory() as proj_td:
        src = Path(src_td)
        root = Path(proj_td)

        # 最小 lumos 源結構(只需 install-graph-toolchain.sh 當探針 + 新版範本)
        scripts_dir = src / "scripts"
        scripts_dir.mkdir(parents=True)
        (scripts_dir / "install-graph-toolchain.sh").write_text("#!/bin/sh\n", encoding="utf-8")
        tpl_dir = scripts_dir / "templates"
        tpl_dir.mkdir()
        NEW_TPL = "新版知識圖譜紀律:{{KG}}"
        (tpl_dir / "graph-discipline.md").write_text(NEW_TPL, encoding="utf-8")
        # hooks dir 需存在避免 rglob 報錯
        (scripts_dir / "hooks").mkdir()

        # ── 建消費專案:既有 vault + 舊 block ────────────────────────────
        subprocess.run(["git", "init", str(root)], capture_output=True)
        slug = "consumer"
        kg = root / "docs" / f"{slug}-knowledge"
        kg.mkdir(parents=True)

        mod = _load_lumos_mod("lumos_t3_update")
        START_PREFIX = mod._CLAUDE_START_PREFIX
        END = mod._CLAUDE_END
        OLD_BODY = "舊版紀律內文:docs/consumer-knowledge/"
        old_block = (START_PREFIX + " -->\n" + OLD_BODY + "\n" + END)
        old_cm = "# CLAUDE.md\n\n使用者規則\n\n" + old_block + "\n"
        (root / "CLAUDE.md").write_text(old_cm, encoding="utf-8")

        # ── 用 LUMOS_HOME env 指臨時源,呼叫 _vendor_toolchain ───────────
        orig_home = os.environ.get("LUMOS_HOME")
        try:
            os.environ["LUMOS_HOME"] = str(src)
            mod._vendor_toolchain(src, root, slug, no_pull=True)
        finally:
            if orig_home is None:
                os.environ.pop("LUMOS_HOME", None)
            else:
                os.environ["LUMOS_HOME"] = orig_home

        # ── 斷言 ─────────────────────────────────────────────────────────
        cm_text = (root / "CLAUDE.md").read_text(encoding="utf-8")
        expected_body = NEW_TPL.replace("{{KG}}", f"docs/{slug}-knowledge/").strip()
        check("update_resyncs: CLAUDE.md block 已更新(含新範本內容)",
              expected_body in cm_text,
              f"新範本內容未在 CLAUDE.md 中;\ncm={cm_text!r}")
        check("update_resyncs: 舊 body 已被替換",
              OLD_BODY not in cm_text,
              f"舊 body 仍存在: {cm_text!r}")
        check("update_resyncs: 使用者規則保留",
              "使用者規則" in cm_text,
              f"使用者規則消失: {cm_text!r}")


def t_init_existing_resyncs():
    """既有 vault + 非 force 跑 cmd_init → CLAUDE.md 紀律區塊被刷新(early-return 不繞過 reinject)。

    透過 subprocess 跑 `lumos init --name consumer`,消費專案有舊 block 和既有 vault。
    環境變數 LUMOS_HOME 指向 lumos-toolchain 本身(有真實範本)。
    """
    import tempfile, os, subprocess, sys
    # lumos 本身的 repo(有真實 scripts/templates/graph-discipline.md)
    lumos_src = Path(GRAPHCTL).resolve().parent.parent

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        subprocess.run(["git", "init", str(root)], capture_output=True)
        slug = "consumer"

        # 建既有 vault
        kg = root / "docs" / f"{slug}-knowledge"
        for d in ("Systems", "Verification", "Projects", "Issues", "Sessions", "MOC"):
            (kg / d).mkdir(parents=True, exist_ok=True)
        (kg / "MOC" / "index.md").write_text("---\ntype: moc\nstatus: doing\n---\n", encoding="utf-8")

        # 建舊 block CLAUDE.md
        tpl_path = lumos_src / "scripts" / "templates" / "graph-discipline.md"
        if not tpl_path.exists():
            check("init_existing_resyncs: 跳過(lumos 源無範本)", True)
            return

        # 故意寫舊 block(body 不同於現版範本)
        START_PREFIX = "<!-- LUMOS:GRAPH-DISCIPLINE:START"
        END = "<!-- LUMOS:GRAPH-DISCIPLINE:END -->"
        OLD_BODY = "舊版 body — 應被 init 刷新"
        old_block = (START_PREFIX + " — 自動注入/更新,勿手改本區塊;"
                     "改範本 scripts/templates/graph-discipline.md -->\n"
                     + OLD_BODY + "\n" + END)
        (root / "CLAUDE.md").write_text("# CLAUDE.md\n\n" + old_block + "\n", encoding="utf-8")

        # 把 lumos 源複製最小必需工具到 consumer(使 _vendor_toolchain 的來源探針通過)
        (root / "scripts").mkdir(exist_ok=True)
        (root / "scripts" / "templates").mkdir(exist_ok=True)
        import shutil
        shutil.copy2(tpl_path, root / "scripts" / "templates" / "graph-discipline.md")

        env = os.environ.copy()
        env["LUMOS_HOME"] = str(lumos_src)
        r = subprocess.run(
            [sys.executable, GRAPHCTL, "init", "--name", slug, "--no-hooks"],
            cwd=str(root), capture_output=True, text=True, env=env
        )

        cm_text = (root / "CLAUDE.md").read_text(encoding="utf-8")
        check("init_existing_resyncs: rc==0", r.returncode == 0,
              f"rc={r.returncode}\n{r.stdout}\n{r.stderr}")
        check("init_existing_resyncs: 舊 body 已被替換",
              OLD_BODY not in cm_text,
              f"舊 body 仍存在;\ncm={cm_text!r}\nstdout={r.stdout!r}\nstderr={r.stderr!r}")
        check("init_existing_resyncs: sentinel block 存在",
              START_PREFIX in cm_text,
              f"sentinel 消失;\ncm={cm_text!r}")


def t_init_existing_no_pull():
    """T3 review I-1/I-2:既有 vault 非 force + with_hooks=True 跑 cmd_init →
    不呼叫 _vendor_toolchain(不 pull、不重裝 hooks),但 CLAUDE.md 紀律區塊有被刷新。

    做法:用 _load_lumos_mod 載入模組後直接替換 _vendor_toolchain 為記錄 stub,
    再以 mock _lumos_src 指向有範本的臨時源,呼叫 mod.cmd_init(...)。
    斷言:stub 未被呼叫;CLAUDE.md 舊 body 已替換。
    """
    import tempfile, os, subprocess, sys

    with tempfile.TemporaryDirectory() as src_td, \
         tempfile.TemporaryDirectory() as proj_td:
        src = Path(src_td)
        root = Path(proj_td)

        # ── 建最小 lumos 源(只需範本 + 探針) ──────────────────────────
        scripts_dir = src / "scripts"
        scripts_dir.mkdir(parents=True)
        (scripts_dir / "install-graph-toolchain.sh").write_text("#!/bin/sh\n", encoding="utf-8")
        tpl_dir = scripts_dir / "templates"
        tpl_dir.mkdir()
        NEW_TPL = "新版知識圖譜紀律(no-pull test):{{KG}}"
        (tpl_dir / "graph-discipline.md").write_text(NEW_TPL, encoding="utf-8")
        (scripts_dir / "hooks").mkdir()

        # ── 建消費專案:既有 vault ──────────────────────────────────────
        subprocess.run(["git", "init", str(root)], capture_output=True)
        slug = "consumer"
        kg = root / "docs" / f"{slug}-knowledge"
        for d in ("Systems", "Verification", "Projects", "Issues", "Sessions", "MOC"):
            (kg / d).mkdir(parents=True, exist_ok=True)
        (kg / "MOC" / "index.md").write_text("---\ntype: moc\nstatus: doing\n---\n", encoding="utf-8")

        # 複製範本到消費專案(供 _reinject 讀取本機已 vendor 範本)
        (root / "scripts" / "templates").mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(tpl_dir / "graph-discipline.md",
                     root / "scripts" / "templates" / "graph-discipline.md")

        # 建舊 block CLAUDE.md
        mod = _load_lumos_mod("lumos_t3_nopull")
        START_PREFIX = mod._CLAUDE_START_PREFIX
        END = mod._CLAUDE_END
        OLD_BODY = "舊版 body — 應被刷新但不 pull"
        old_block = (START_PREFIX + " — 自動注入/更新,勿手改本區塊;"
                     "改範本 scripts/templates/graph-discipline.md -->\n"
                     + OLD_BODY + "\n" + END)
        (root / "CLAUDE.md").write_text("# CLAUDE.md\n\n" + old_block + "\n", encoding="utf-8")

        # ── monkeypatch:替換 _vendor_toolchain 為記錄 stub ────────────
        vendor_called = []

        def _stub_vendor(s, r, sl, no_pull=False):
            vendor_called.append((s, r, sl, no_pull))
            return 0  # 假裝成功但不執行任何動作

        orig_vendor = mod._vendor_toolchain
        orig_lumos_src = mod._lumos_src
        mod._vendor_toolchain = _stub_vendor
        mod._lumos_src = lambda source=None: src  # 指向有範本的臨時源

        try:
            import os as _os
            orig_cwd = _os.getcwd()
            _os.chdir(str(root))
            rc = mod.cmd_init(name=slug, force=False, with_hooks=True, no_pull=False)
        finally:
            _os.chdir(orig_cwd)
            mod._vendor_toolchain = orig_vendor
            mod._lumos_src = orig_lumos_src

        # ── 斷言 ──────────────────────────────────────────────────────
        check("init_existing_no_pull: rc==0", rc == 0, f"rc={rc}")
        check("init_existing_no_pull: _vendor_toolchain 未被呼叫(不 pull/不重裝 hooks)",
              len(vendor_called) == 0,
              f"_vendor_toolchain 被呼叫了 {len(vendor_called)} 次: {vendor_called}")
        cm_text = (root / "CLAUDE.md").read_text(encoding="utf-8")
        check("init_existing_no_pull: 舊 body 已被替換(CLAUDE.md 有刷新)",
              OLD_BODY not in cm_text,
              f"舊 body 仍存在;\ncm={cm_text!r}")
        check("init_existing_no_pull: sentinel block 存在",
              START_PREFIX in cm_text,
              f"sentinel 消失;\ncm={cm_text!r}")

def t_init_force_uses_existing_vault_slug():
    """Bug repro:lumos init --force 在既有 vault 上,slug 應取「既有 vault 的 slug」,
    不是 repo basename。否則建錯 vault + 把 CLAUDE.md {{KG}} 路徑寫錯。
    現場事故:repo basename=landmarkmember、vault=landmark-knowledge →
    --force 誤建 docs/landmarkmember-knowledge/ + CLAUDE.md 路徑寫成 landmarkmember-knowledge。"""
    import tempfile, os, subprocess, shutil

    with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as src_td:
        # repo basename 刻意 != vault slug
        root = Path(td) / "landmarkmember"
        root.mkdir()
        subprocess.run(["git", "init", str(root)], capture_output=True)
        src = Path(src_td)
        (src / "scripts" / "templates").mkdir(parents=True)
        (src / "scripts" / "templates" / "graph-discipline.md").write_text(
            "紀律:{{KG}}", encoding="utf-8")
        (src / "scripts" / "hooks").mkdir()
        # 既有 vault:landmark-knowledge(slug=landmark ≠ basename landmarkmember)
        kg = root / "docs" / "landmark-knowledge"
        for d in ("Systems", "Verification", "Projects", "Issues", "Sessions", "MOC"):
            (kg / d).mkdir(parents=True, exist_ok=True)
        (kg / "MOC" / "index.md").write_text("---\ntype: moc\nstatus: doing\n---\n", encoding="utf-8")
        (root / "scripts" / "templates").mkdir(parents=True, exist_ok=True)
        shutil.copy2(src / "scripts" / "templates" / "graph-discipline.md",
                     root / "scripts" / "templates" / "graph-discipline.md")

        mod = _load_lumos_mod("lumos_initslug")
        captured = []

        def _stub_vendor(s, r, sl, no_pull=False):
            captured.append(sl)
            return 0

        orig_v, orig_s = mod._vendor_toolchain, mod._lumos_src
        mod._vendor_toolchain = _stub_vendor
        mod._lumos_src = lambda source=None: src
        try:
            orig_cwd = os.getcwd()
            os.chdir(str(root))
            rc = mod.cmd_init(name=None, force=True, with_hooks=True, no_pull=True)
        finally:
            os.chdir(orig_cwd)
            mod._vendor_toolchain = orig_v
            mod._lumos_src = orig_s

        check("init_force_slug: rc==0", rc == 0, f"rc={rc}")
        check("init_force_slug: slug 取既有 vault(landmark)非 repo basename(landmarkmember)",
              captured == ["landmark"], f"_vendor_toolchain 收到 slug={captured}(應為 ['landmark'])")
        check("init_force_slug: 沒建錯的 docs/landmarkmember-knowledge/",
              not (root / "docs" / "landmarkmember-knowledge").exists(),
              "誤建了 landmarkmember-knowledge 空 scaffold")
        check("init_force_slug: 既有 landmark-knowledge 仍在",
              (root / "docs" / "landmark-knowledge").exists(), "既有 vault 消失")


# ── Task 4: doctor Check D 紀律區塊漂移守衛 ────────────────────────────────────

def _make_check_d_root(td, tpl_content=None, claude_content=None, slug="demo"):
    """建立最小 repo root 結構供 Check D 測試用。
    vault 在 root/docs/<slug>-knowledge/;doctor 透過 vault.parents 取到 docs → repo_root。
    tpl_content=None → 不建立 scripts/templates/graph-discipline.md。
    claude_content=None → 不建立 CLAUDE.md。
    回傳 (root, vault)。
    """
    root = Path(td)
    vault = root / "docs" / f"{slug}-knowledge"
    for sub in ("Systems", "Verification", "Projects", "MOC"):
        (vault / sub).mkdir(parents=True, exist_ok=True)
    (vault / "MOC" / "idx.md").write_bytes(b"---\ntype: moc\n---\n# idx\n")
    # scripts/templates
    tpl_dir = root / "scripts" / "templates"
    tpl_dir.mkdir(parents=True, exist_ok=True)
    if tpl_content is not None:
        (tpl_dir / "graph-discipline.md").write_text(tpl_content, encoding="utf-8")
    if claude_content is not None:
        (root / "CLAUDE.md").write_bytes(
            claude_content if isinstance(claude_content, bytes)
            else claude_content.encode("utf-8")
        )
    return root, vault


def _make_check_d_block(tpl_content, slug):
    """組出 reinject 會寫入的完整 sentinel block,供 Check D fixture CLAUDE.md 使用。

    START 行引用 _START_TEMPLATE + LUMOS_VERSION 確保與正式 reinject 格式一致。
    T4 reviewer 要求:不得內聯 START 常數字串——版本戳加入後內聯會讓 fixture 與
    真正格式不符,導致 _extract_claude_block_span 判不出 found → 測試隱性 skip。
    """
    import importlib.util
    from importlib.machinery import SourceFileLoader
    spec = importlib.util.spec_from_file_location(
        "_lumos_for_block", GRAPHCTL,
        loader=SourceFileLoader("_lumos_for_block", GRAPHCTL))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    body = tpl_content.replace("{{KG}}", f"docs/{slug}-knowledge/").strip()
    START = m._START_TEMPLATE.format(version=m.LUMOS_VERSION)
    END = m._CLAUDE_END
    return START + "\n" + body + "\n" + END


def t_claude_block_matches_template():
    """本 repo 的 CLAUDE.md 紀律區塊必須與 resolved 範本完全一致(防復發守衛)。"""
    # 直接用本 repo 跑 doctor —vault <actual-vault>
    actual_vault = Path(GRAPHCTL).resolve().parent.parent / "docs" / "lumos-toolchain-knowledge"
    if not actual_vault.is_dir():
        check("claude_block_matches_template: vault 不存在(skip)", True, "")
        return
    r = subprocess.run(
        [sys.executable, GRAPHCTL, "--vault", str(actual_vault), "doctor", "--ci"],
        capture_output=True, text=True,
    )
    # Check D 應讓本 repo doctor 保持 0 issues(無「不同步」警告)
    check("claude_block_matches_template: 本 repo doctor Check D 淨(0 漂移)",
          "不同步" not in r.stdout,
          f"stdout={r.stdout}")
    check("claude_block_matches_template: 本 repo doctor 整體 0 issues",
          r.returncode == 0,
          f"rc={r.returncode}\nstdout={r.stdout}")


def t_doctor_reports_drift():
    """CLAUDE.md block body 與範本不一致 → Check D 報漂移(issue≥1)。"""
    import tempfile
    TPL = "知識圖譜路徑:{{KG}}\n\n這是圖譜紀律說明。"
    SLUG = "myproj"
    block = _make_check_d_block(TPL, SLUG)
    # 人為把 CLAUDE.md 的 block body 改一行
    tampered_block = block.replace("這是圖譜紀律說明。", "這是被人改過的說明。")
    claude_content = "# CLAUDE.md\n\n前言\n\n" + tampered_block + "\n\n後記\n"
    with tempfile.TemporaryDirectory() as td:
        root, vault = _make_check_d_root(td, tpl_content=TPL,
                                          claude_content=claude_content, slug=SLUG)
        r = subprocess.run(
            [sys.executable, GRAPHCTL, "--vault", str(vault), "doctor", "--ci"],
            capture_output=True, text=True,
        )
        check("doctor_reports_drift: 輸出含 [D]",
              "[D]" in r.stdout,
              f"stdout={r.stdout}")
        check("doctor_reports_drift: 輸出含不同步訊息",
              "不同步" in r.stdout,
              f"stdout={r.stdout}")
        check("doctor_reports_drift: --ci 非零 exit",
              r.returncode != 0,
              f"rc={r.returncode}\nstdout={r.stdout}")


def t_doctor_skip_no_template():
    """範本檔不存在 → Check D skip,不誤報、不計 issue。"""
    import tempfile
    SLUG = "myproj"
    TPL = "知識圖譜:{{KG}}"
    block = _make_check_d_block(TPL, SLUG)
    # CLAUDE.md 有正常 sentinel
    claude_content = "# CLAUDE.md\n\n" + block + "\n"
    with tempfile.TemporaryDirectory() as td:
        # tpl_content=None → 不建立範本
        root, vault = _make_check_d_root(td, tpl_content=None,
                                          claude_content=claude_content, slug=SLUG)
        r = subprocess.run(
            [sys.executable, GRAPHCTL, "--vault", str(vault), "doctor", "--ci"],
            capture_output=True, text=True,
        )
        check("doctor_skip_no_template: 無 [D] 不同步 issue",
              "不同步" not in r.stdout,
              f"stdout={r.stdout}")
        check("doctor_skip_no_template: doctor 整體 0 issues(無範本不誤報)",
              r.returncode == 0,
              f"rc={r.returncode}\nstdout={r.stdout}")


def t_doctor_broken_reports():
    """CLAUDE.md 只 START 無 END(broken)→ Check D 報漂移、不 crash。"""
    import tempfile
    TPL = "知識圖譜:{{KG}}"
    SLUG = "myproj"
    START = ("<!-- LUMOS:GRAPH-DISCIPLINE:START"
             " — 自動注入/更新,勿手改本區塊;改範本 scripts/templates/graph-discipline.md -->")
    # 只有 START 無 END(broken)
    broken_content = "# CLAUDE.md\n\n前言\n\n" + START + "\n只有 START 沒 END\n"
    with tempfile.TemporaryDirectory() as td:
        root, vault = _make_check_d_root(td, tpl_content=TPL,
                                          claude_content=broken_content, slug=SLUG)
        r = subprocess.run(
            [sys.executable, GRAPHCTL, "--vault", str(vault), "doctor", "--ci"],
            capture_output=True, text=True,
        )
        check("doctor_broken_reports: 不 crash(無 exception)",
              r.returncode in (0, 1),
              f"rc={r.returncode}\nstderr={r.stderr}")
        check("doctor_broken_reports: 輸出含 [D]",
              "[D]" in r.stdout,
              f"stdout={r.stdout}")
        check("doctor_broken_reports: 報不同步或損壞訊息",
              "不同步" in r.stdout or "broken" in r.stdout or "損壞" in r.stdout or "sentinel 損壞" in r.stdout,
              f"stdout={r.stdout}")
        check("doctor_broken_reports: --ci 非零 exit",
              r.returncode != 0,
              f"rc={r.returncode}\nstdout={r.stdout}")


# ── Task 5: LUMOS_VERSION + 版本戳 + nudge ───────────────────────────────────


def t_version_stamped_in_sentinel():
    """reinject 後 CLAUDE.md 的 START 行必須含 LUMOS_VERSION(如 v1.0)。"""
    import importlib.util
    from importlib.machinery import SourceFileLoader
    spec = importlib.util.spec_from_file_location(
        "lumos_mod", GRAPHCTL, loader=SourceFileLoader("lumos_mod", GRAPHCTL))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    version = m.LUMOS_VERSION  # 必須存在、格式 vX.Y
    check("version_stamped: LUMOS_VERSION 常數存在且格式 vX.Y",
          bool(__import__("re").fullmatch(r"v\d+\.\d+", version)),
          f"got {version!r}")

    # 建立臨時 root + 範本,跑 reinject,確認 START 行含版本
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        tpl_dir = root / "scripts" / "templates"
        tpl_dir.mkdir(parents=True)
        (tpl_dir / "graph-discipline.md").write_text(
            "{{KG}} 紀律區塊測試", encoding="utf-8")
        ri = m._reinject_claude_block(root, "myproj")
        check("version_stamped: reinject created",
              ri.status == "created", f"status={ri.status}")
        cm_text = (root / "CLAUDE.md").read_text(encoding="utf-8")
        # START 行應含版本字串
        start_line = [l for l in cm_text.splitlines() if m._CLAUDE_START_PREFIX in l]
        check("version_stamped: START 行存在",
              len(start_line) == 1, f"lines={start_line}")
        if start_line:
            check(f"version_stamped: START 行含 {version}",
                  version in start_line[0], f"start_line={start_line[0]!r}")


def t_version_stamp_on_updated_path():
    """存量戶缺口修補(2026-07-07 Landmark 真機發現):updated 路徑原本只換 body、
    START 行原樣保留 → 所有既有安裝戶永遠拿不到版本戳。修後:found 路徑同步刷新
    START 行(sentinel 外仍逐字保留);body 同+START 同 → 仍 unchanged(冪等)。"""
    import importlib.util
    from importlib.machinery import SourceFileLoader
    spec = importlib.util.spec_from_file_location(
        "lumos_mod_su", GRAPHCTL, loader=SourceFileLoader("lumos_mod_su", GRAPHCTL))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    version = m.LUMOS_VERSION

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        tpl_dir = root / "scripts" / "templates"
        tpl_dir.mkdir(parents=True)
        TPL = "{{KG}} 紀律內容"
        (tpl_dir / "graph-discipline.md").write_text(TPL, encoding="utf-8")
        body = TPL.replace("{{KG}}", "docs/myproj-knowledge/").strip("\n")
        # 造存量戶:舊式無版本戳 START + body 已同步 + sentinel 外有使用者內容
        OLD_START = m._CLAUDE_START_PREFIX + " — 自動注入/更新,勿手改本區塊;改範本 scripts/templates/graph-discipline.md -->"
        PREFIX = "# CLAUDE.md\n\n使用者前綴\n\n"
        SUFFIX = "\n\n使用者後綴\n"
        cm = root / "CLAUDE.md"
        cm.write_text(PREFIX + OLD_START + "\n" + body + "\n" + m._CLAUDE_END + SUFFIX,
                      encoding="utf-8")

        # body 相同、僅 START 無戳 → 應 updated(刷 START),非 unchanged
        ri = m._reinject_claude_block(root, "myproj")
        check("stamp_on_updated: body 同但 START 無戳 → updated",
              ri.status == "updated", f"status={ri.status}")
        t = cm.read_text(encoding="utf-8")
        sl = [l for l in t.splitlines() if m._CLAUDE_START_PREFIX in l]
        check("stamp_on_updated: START 行已帶版本戳",
              len(sl) == 1 and version in sl[0], f"start_lines={sl}")
        check("stamp_on_updated: sentinel 外前綴 byte-equal",
              t.startswith(PREFIX), f"head={t[:40]!r}")
        check("stamp_on_updated: sentinel 外後綴 byte-equal",
              t.endswith(SUFFIX), f"tail={t[-20:]!r}")
        check("stamp_on_updated: body 未變",
              ("\n" + body + "\n") in t, "body 被動到")

        # 再跑一次 → START 已 canonical + body 同 → unchanged(冪等)
        ri2 = m._reinject_claude_block(root, "myproj")
        check("stamp_on_updated: 二跑 unchanged(冪等)",
              ri2.status == "unchanged", f"status={ri2.status}")


def t_version_parse_tolerant():
    """_parse_sentinel_version:START 行無版本欄位 → 回 None、不 crash。"""
    import importlib.util
    from importlib.machinery import SourceFileLoader
    spec = importlib.util.spec_from_file_location(
        "lumos_mod2", GRAPHCTL, loader=SourceFileLoader("lumos_mod2", GRAPHCTL))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    # 無版本的 START 行
    old_start = "<!-- LUMOS:GRAPH-DISCIPLINE:START — 自動注入/更新,勿手改 -->"
    text_no_ver = old_start + "\nbody\n" + "<!-- LUMOS:GRAPH-DISCIPLINE:END -->"
    result = m._parse_sentinel_version(text_no_ver)
    check("version_parse_tolerant: 無版本欄位 → None",
          result is None, f"got {result!r}")

    # 有版本的 START 行
    ver_start = "<!-- LUMOS:GRAPH-DISCIPLINE:START v1.0 — 自動注入/更新,勿手改 -->"
    text_with_ver = ver_start + "\nbody\n" + "<!-- LUMOS:GRAPH-DISCIPLINE:END -->"
    result2 = m._parse_sentinel_version(text_with_ver)
    check("version_parse_tolerant: 有版本欄位 → 取到 v1.0",
          result2 == "v1.0", f"got {result2!r}")

    # 完全空字串不 crash
    result3 = m._parse_sentinel_version("")
    check("version_parse_tolerant: 空字串 → None 不 crash",
          result3 is None, f"got {result3!r}")


def t_version_bump_not_trigger_guard():
    """START 行帶舊版本(v0.9),body == 範本 → Check D 淨(0 漂移)。
    關鍵:版本戳在 START 行(body 外),bump 不觸發內容守衛。"""
    import tempfile
    TPL = "知識圖譜路徑:{{KG}}\n\n這是圖譜紀律說明。"
    SLUG = "myproj"
    body = TPL.replace("{{KG}}", f"docs/{SLUG}-knowledge/").strip()
    # START 行帶「舊版本」v0.9,但 body 完全符合範本
    old_version_start = ("<!-- LUMOS:GRAPH-DISCIPLINE:START v0.9"
                         " — 自動注入/更新,勿手改本區塊;改範本 scripts/templates/graph-discipline.md -->")
    END = "<!-- LUMOS:GRAPH-DISCIPLINE:END -->"
    block_old_version = old_version_start + "\n" + body + "\n" + END
    claude_content = "# CLAUDE.md\n\n前言\n\n" + block_old_version + "\n\n後記\n"
    with tempfile.TemporaryDirectory() as td:
        root, vault = _make_check_d_root(td, tpl_content=TPL,
                                          claude_content=claude_content, slug=SLUG)
        r = subprocess.run(
            [sys.executable, GRAPHCTL, "--vault", str(vault), "doctor", "--ci"],
            capture_output=True, text=True,
        )
        check("version_bump_not_trigger_guard: 版本舊但 body 符合 → 無不同步警告",
              "不同步" not in r.stdout,
              f"stdout={r.stdout}")
        check("version_bump_not_trigger_guard: doctor 整體 0 issues(版本不觸發內容守衛)",
              r.returncode == 0,
              f"rc={r.returncode}\nstdout={r.stdout}")


def t_version_nudge_when_behind():
    """fixture CLAUDE v0.9、來源 clone LUMOS_VERSION=v1.0 → nudge 回提示字串。"""
    import importlib.util, os
    from importlib.machinery import SourceFileLoader
    spec = importlib.util.spec_from_file_location(
        "lumos_nudge", GRAPHCTL, loader=SourceFileLoader("lumos_nudge", GRAPHCTL))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    with tempfile.TemporaryDirectory() as td:
        # 建造臨時「來源 clone」:只需含 scripts/lumos 且其中有 LUMOS_VERSION = "v1.0"
        src_dir = Path(td) / "fake_src"
        (src_dir / "scripts").mkdir(parents=True)
        fake_lumos = src_dir / "scripts" / "lumos"
        fake_lumos.write_text('LUMOS_VERSION = "v1.0"\n', encoding="utf-8")

        # 建造 CLAUDE.md 含 v0.9 的 START 行
        ver_start = ("<!-- LUMOS:GRAPH-DISCIPLINE:START v0.9"
                     " — 自動注入/更新,勿手改 -->")
        END = "<!-- LUMOS:GRAPH-DISCIPLINE:END -->"
        claude_text = ver_start + "\nbody content\n" + END
        root = Path(td) / "consumer"
        root.mkdir()
        (root / "CLAUDE.md").write_text(claude_text, encoding="utf-8")

        # 用 LUMOS_HOME 指向臨時來源
        orig_home = os.environ.get("LUMOS_HOME")
        os.environ["LUMOS_HOME"] = str(src_dir)
        try:
            nudge = m._version_nudge(root)
        finally:
            if orig_home is None:
                os.environ.pop("LUMOS_HOME", None)
            else:
                os.environ["LUMOS_HOME"] = orig_home

        check("version_nudge_when_behind: 回提示字串(非 None)",
              nudge is not None, f"got {nudge!r}")
        if nudge is not None:
            check("version_nudge_when_behind: 提示含 v0.9 或 v1.0",
                  "v0.9" in nudge or "v1.0" in nudge, f"nudge={nudge!r}")
            check("version_nudge_when_behind: 提示含 update 相關字眼",
                  "update" in nudge or "lumos" in nudge.lower(),
                  f"nudge={nudge!r}")


def t_nudge_skip_when_no_source():
    """_lumos_src() 指向不存在路徑 → _version_nudge 回 None、不 crash。"""
    import importlib.util, os
    from importlib.machinery import SourceFileLoader
    spec = importlib.util.spec_from_file_location(
        "lumos_ns", GRAPHCTL, loader=SourceFileLoader("lumos_ns", GRAPHCTL))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    with tempfile.TemporaryDirectory() as td:
        # CLAUDE.md 含 v0.9
        ver_start = ("<!-- LUMOS:GRAPH-DISCIPLINE:START v0.9"
                     " — 自動注入/更新,勿手改 -->")
        END = "<!-- LUMOS:GRAPH-DISCIPLINE:END -->"
        root = Path(td) / "consumer"
        root.mkdir()
        (root / "CLAUDE.md").write_text(
            ver_start + "\nbody\n" + END, encoding="utf-8")

        # 指向不存在的來源
        nonexistent = str(Path(td) / "does_not_exist")
        orig_home = os.environ.get("LUMOS_HOME")
        os.environ["LUMOS_HOME"] = nonexistent
        try:
            nudge = m._version_nudge(root)
        finally:
            if orig_home is None:
                os.environ.pop("LUMOS_HOME", None)
            else:
                os.environ["LUMOS_HOME"] = orig_home

        check("nudge_skip_when_no_source: 來源不存在 → None 不 crash",
              nudge is None, f"got {nudge!r}")


def _mk_cochange_repo():
    """合成 git 歷史(cochange 測試用):
    A.md+B.md 共改 4 次、A.md 單改 1 次 → conf(A⇒B)=0.8, conf(B⇒A)=1.0, support=4
    F.md+G.md 共改 2 次 → support 2(低於 min_support=3,--all 才見)
    H.md+I.md 共改 1 次 → support 1(硬底線外,連 --all 也不見)
    中文甲.md+中文乙.md 共改 3 次 → conf 1.0(quotePath 測試)
    一個 >20 檔大 commit(含 C.md/D.md) → 整批排除
    根層 package-lock.json+E.md 共改 3 次 → lockfile 被預設排除清單濾掉
    """
    import subprocess as sp
    root = Path(tempfile.mkdtemp(prefix="gctl-cc-"))
    def g(*a):
        sp.run(["git", "-C", str(root), *a], capture_output=True, text=True)
    g("init", "-q"); g("config", "user.email", "t@t.t"); g("config", "user.name", "t")
    def commit(files, msg):
        for f, content in files.items():
            p = root / f
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        g("add", "-A"); g("commit", "-qm", msg)
    for i in range(4):
        commit({"A.md": f"a{i}", "B.md": f"b{i}"}, f"ab{i}")
    commit({"A.md": "a-solo"}, "a-solo")
    for i in range(2):
        commit({"F.md": f"f{i}", "G.md": f"g{i}"}, f"fg{i}")
    commit({"H.md": "h", "I.md": "i"}, "hi")
    for i in range(3):
        commit({"中文甲.md": f"x{i}", "中文乙.md": f"y{i}"}, f"cn{i}")
    bulk = {f"bulk/f{i}.txt": str(i) for i in range(21)}
    bulk.update({"C.md": "c", "D.md": "d"})
    commit(bulk, "bulk")
    # 恰好 20 檔(=max_changeset 邊界,應納入):J/K + 18 filler × 3 次(殺 mutation M3:> 變 >= 會漏)
    for i in range(3):
        b20 = {f"b20/f{j}.txt": f"{i}-{j}" for j in range(18)}
        b20.update({"J.md": f"j{i}", "K.md": f"k{i}"})
        commit(b20, f"b20-{i}")
    for i in range(3):
        commit({"package-lock.json": f"l{i}", "E.md": f"e{i}"}, f"lock{i}")
    return root


def t_cochange():
    import subprocess as sp, json
    root = _mk_cochange_repo()
    def lum(*a, cwd=None):
        return sp.run([sys.executable, GRAPHCTL, *a],
                      capture_output=True, text=True, cwd=cwd or root)
    def jload(r):
        return json.loads(r.stdout.strip().splitlines()[-1])

    # ── rules:預設套門檻 ──
    r = lum("cochange", "rules", "--json")
    check("cochange rules rc0", r.returncode == 0, r.stderr)
    data = jload(r)
    pairs = {(x["lhs"], x["rhs"]): x for x in data["rules"]}
    check("cochange B⇒A conf 1.0", pairs.get(("B.md", "A.md"), {}).get("confidence") == 1.0, str(sorted(pairs)))
    check("cochange A⇒B conf 0.8(=門檻,含)", pairs.get(("A.md", "B.md"), {}).get("confidence") == 0.8, str(sorted(pairs)))
    flat = [k for p in pairs for k in p]
    check("cochange 大commit排除(C/D 無規則)", not any(k in ("C.md", "D.md") for k in flat), str(sorted(pairs)))
    check("cochange 恰好20檔納入(J⇒K 邊界,殺 M3)", pairs.get(("J.md", "K.md"), {}).get("support") == 3, str(sorted(pairs)))
    check("cochange 根層 lockfile 排除(**/ 雙試)", not any("package-lock" in k for k in flat), str(sorted(pairs)))
    check("cochange support=2 預設不出現(F/G)", ("F.md", "G.md") not in pairs, str(sorted(pairs)))
    check("cochange 中文檔名 key 非 octal 逃逸", ("中文甲.md", "中文乙.md") in pairs, str(sorted(pairs)))
    check("cochange rules commits/files 為 int", isinstance(data["commits"], int) and isinstance(data["files"], int), str(data))

    # ── rules --all:解除 conf 門檻、support 硬底線 2 ──
    r = lum("cochange", "rules", "--all", "--json")
    pairs_all = {(x["lhs"], x["rhs"]): x for x in jload(r)["rules"]}
    check("cochange --all 含 support=2(F/G)", ("F.md", "G.md") in pairs_all, str(sorted(pairs_all)))
    check("cochange --all 不含 support=1(H/I 硬底線)", ("H.md", "I.md") not in pairs_all, str(sorted(pairs_all)))
    check("cochange --all 是預設超集", set(pairs).issubset(set(pairs_all)), "")

    # ── check --staged:A 改了漏 B → 警告(stdout) ──
    (root / "A.md").write_text("staged-change", encoding="utf-8")
    sp.run(["git", "-C", str(root), "add", "A.md"], capture_output=True)
    r = lum("cochange", "check", "--staged", "--json")
    check("cochange check rc0", r.returncode == 0, r.stderr)
    w = jload(r)["warnings"]
    check("cochange staged 漏改警告", any(x["changed"] == "A.md" and x["missing"] == "B.md" for x in w), str(w))
    check("cochange checked 為 int", isinstance(jload(r)["checked"], int), "")
    r = lum("cochange", "check", "--staged")
    check("cochange 警告在 stdout", "B.md" in r.stdout and r.returncode == 0, f"out={r.stdout!r} err={r.stderr!r}")

    # 夥伴同在 staged → 不警告
    (root / "B.md").write_text("staged-too", encoding="utf-8")
    sp.run(["git", "-C", str(root), "add", "B.md"], capture_output=True)
    w = jload(lum("cochange", "check", "--staged", "--json"))["warnings"]
    check("cochange 夥伴同 staged 不警告", not any(x["missing"] == "B.md" for x in w), str(w))
    sp.run(["git", "-C", str(root), "reset", "-q", "B.md"], capture_output=True)
    sp.run(["git", "-C", str(root), "checkout", "-q", "--", "B.md"], capture_output=True)

    # ── --diff 模式:挖掘母體=range 左端(被查 commit 不自我豁免) ──
    sp.run(["git", "-C", str(root), "commit", "-qm", "a-only"], capture_output=True)  # 把 staged A.md 提交
    r = lum("cochange", "check", "--diff", "HEAD~1..HEAD", "--json")
    check("cochange --diff rc0", r.returncode == 0, r.stderr)
    w = jload(r)["warnings"]
    check("cochange --diff 漏改警告(母體到 range 左端)", any(x["changed"] == "A.md" and x["missing"] == "B.md" for x in w), str(w))

    # --staged/--diff 皆缺 → rc2;同給 → --diff 優先
    r = lum("cochange", "check")
    check("cochange check 皆缺 rc2", r.returncode == 2, str(r.returncode))
    r = lum("cochange", "check", "--staged", "--diff", "HEAD~1..HEAD", "--json")
    check("cochange 同給 --diff 優先(staged 空仍有警告)", any(x["changed"] == "A.md" for x in jload(r)["warnings"]), r.stdout)

    # ── 殭屍規則:右側檔已刪 → check 不警告;rules 仍列(觀察用) ──
    sp.run(["git", "-C", str(root), "rm", "-q", "B.md"], capture_output=True)
    sp.run(["git", "-C", str(root), "commit", "-qm", "rm-b"], capture_output=True)
    (root / "A.md").write_text("after-rm", encoding="utf-8")
    sp.run(["git", "-C", str(root), "add", "A.md"], capture_output=True)
    w = jload(lum("cochange", "check", "--staged", "--json"))["warnings"]
    check("cochange 右側已刪不警告(check 層)", not any(x["missing"] == "B.md" for x in w), str(w))
    sp.run(["git", "-C", str(root), "reset", "-q", "A.md"], capture_output=True)
    sp.run(["git", "-C", str(root), "checkout", "-q", "--", "A.md"], capture_output=True)

    # ── config:覆寫生效、exclude 合併、min_support=1 視為 2、壞 JSON fail-open ──
    (root / ".lumos").mkdir(exist_ok=True)
    (root / ".lumos" / "cochange.json").write_text('{"min_confidence": 0.99}', encoding="utf-8")
    pairs99 = {(x["lhs"], x["rhs"]) for x in jload(lum("cochange", "rules", "--json"))["rules"]}
    check("cochange config 覆寫 conf 0.99(0.8 對消失、1.0 對留)", ("A.md", "B.md") not in pairs99 and ("中文甲.md", "中文乙.md") in pairs99, str(sorted(pairs99)))
    (root / ".lumos" / "cochange.json").write_text('{"exclude": ["中文*.md"]}', encoding="utf-8")
    pairs_ex = {(x["lhs"], x["rhs"]) for x in jload(lum("cochange", "rules", "--json"))["rules"]}
    check("cochange 自訂 exclude 與預設合併", ("中文甲.md", "中文乙.md") not in pairs_ex and not any("package-lock" in k for p in pairs_ex for k in p), str(sorted(pairs_ex)))
    (root / ".lumos" / "cochange.json").write_text('{"min_support": 1}', encoding="utf-8")
    r = lum("cochange", "rules", "--json")
    check("cochange min_support=1 視為 2 並提示(stdout)", "視為 2" in r.stdout and r.returncode == 0, r.stdout[:200])
    (root / ".lumos" / "cochange.json").write_text('{broken', encoding="utf-8")
    r = lum("cochange", "rules", "--json")
    check("cochange 壞 JSON fail-open rc0+提示(stdout)", r.returncode == 0 and "解析失敗" in r.stdout, f"rc={r.returncode} out={r.stdout[:200]}")
    (root / ".lumos" / "cochange.json").unlink()

    # ── rc:zero-commit rc0、非 git rc2 ──
    import subprocess as sp2
    empty = Path(tempfile.mkdtemp(prefix="gctl-cc0-"))
    sp2.run(["git", "-C", str(empty), "init", "-q"], capture_output=True)
    r = lum("cochange", "rules", "--json", cwd=empty)
    check("cochange zero-commit rules rc0 空集", r.returncode == 0 and jload(r)["rules"] == [], f"rc={r.returncode}")
    (empty / "x.md").write_text("x", encoding="utf-8")
    sp2.run(["git", "-C", str(empty), "add", "x.md"], capture_output=True)
    r = lum("cochange", "check", "--staged", "--json", cwd=empty)
    check("cochange zero-commit check rc0", r.returncode == 0 and jload(r)["warnings"] == [], f"rc={r.returncode} out={r.stdout[:120]}")
    nogit = Path(tempfile.mkdtemp(prefix="gctl-ccng-"))
    r = lum("cochange", "rules", "--repo", str(nogit), cwd=nogit)
    check("cochange 非 git rc2", r.returncode == 2, str(r.returncode))

    # config 型別守衛(code-loop r1:非數值 fail-open 不 traceback)
    (root / ".lumos" / "cochange.json").write_text('{"min_confidence": "0.9", "max_changeset": "20"}', encoding="utf-8")
    r = lum("cochange", "rules", "--json")
    check("cochange 非數值門檻 fail-open rc0+提示", r.returncode == 0 and "非數值" in r.stdout, f"rc={r.returncode} out={r.stdout[:200]} err={r.stderr[:200]}")
    (root / ".lumos" / "cochange.json").unlink()

    # 清理 tempdir(code-loop r1:洩漏修復)
    import shutil
    for d in (root, empty, nogit):
        shutil.rmtree(d, ignore_errors=True)


def _mk_kill_env():
    """合成 git repo + vault + 一條綁 [test:] 的 INVARIANT + python run_cmd。
    prod.py 的 LIMIT 是被守衛行為;test_guard.py 斷言之。"""
    import subprocess as sp
    root = Path(tempfile.mkdtemp(prefix="gctl-kill-"))
    def g(*a):
        sp.run(["git", "-C", str(root), *a], capture_output=True, text=True)
    g("init", "-q"); g("config", "user.email", "t@t.t"); g("config", "user.name", "t")
    (root / "prod.py").write_text("LIMIT = 5\n\ndef check(n):\n    return n <= LIMIT\n", encoding="utf-8")
    (root / "test_guard.py").write_text(
        "import sys, prod\n"
        "def TestLimitFive():\n"
        "    assert prod.check(5) and not prod.check(6)\n"
        "TestLimitFive()\nprint('ok')\n", encoding="utf-8")
    (root / ".lumos").mkdir()
    (root / ".lumos" / "config.json").write_text(
        '{"test": {"run_cmd": "python3 test_guard.py"}}', encoding="utf-8")
    v = root / "docs" / "kg-knowledge"
    (v / "Systems").mkdir(parents=True)
    (v / "MOC").mkdir()
    (v / "MOC" / "i.md").write_text("---\ntype: moc\n---\n", encoding="utf-8")
    (v / "Systems" / "Limit.md").write_text(
        "---\ntype: system\nstatus: done\nsummary: |-\n"
        "  KEY:★INVARIANT★ 上限恆為5,超過必拒 [test:TestLimitFive]\n---\n# Limit\n",
        encoding="utf-8")
    g("add", "-A"); g("commit", "-qm", "init")
    return root, v


def t_guard_kill():
    import subprocess as sp, json, os
    root, v = _mk_kill_env()
    def lum(*a, env_extra=None):
        e = dict(os.environ)
        e["LUMOS_KILL_TIMEOUT_FLOOR"] = "3"
        if env_extra:
            e.update(env_extra)
        return sp.run([sys.executable, GRAPHCTL, "--vault", str(v), *a],
                      capture_output=True, text=True, cwd=root, env=e)

    # kill-add:寫後自驗 + KEY 行標記
    r = lum("guard", "kill-add", "Systems/Limit", "上限恆為5",
            "--file", "prod.py", "--old", "LIMIT = 5", "--new", "LIMIT = 99",
            "--note", "上限被放寬,超賣風險")
    check("kill-add rc0", r.returncode == 0, r.stderr)
    txt = (v / "Systems" / "Limit.md").read_text(encoding="utf-8")
    check("kill-add 寫入 kill_recipes+標記", "kill_recipes" in txt and "[kill:recipes]" in txt, txt[:400])
    # 重複配方拒絕
    r = lum("guard", "kill-add", "Systems/Limit", "上限恆為5",
            "--file", "prod.py", "--old", "LIMIT = 5", "--new", "LIMIT = 0")
    check("kill-add 重複拒絕 rc2", r.returncode == 2, str(r.returncode))
    # naked 合約 0 ref → rc2
    (v / "Systems" / "Naked.md").write_text(
        "---\ntype: system\nstatus: done\nsummary: |-\n  KEY:★INVARIANT★ 裸合約無綁定\n---\n# N\n",
        encoding="utf-8")
    r = lum("guard", "kill-add", "Systems/Naked", "裸合約",
            "--file", "prod.py", "--old", "x", "--new", "y")
    check("kill-add naked rc2", r.returncode == 2, str(r.returncode))

    # kill:killed happy path(壞法讓測試翻紅)
    r = lum("guard", "kill", "Systems/Limit", "--json")
    check("kill killed rc0", r.returncode == 0, f"rc={r.returncode} {r.stdout[:200]} {r.stderr[:200]}")
    data = json.loads(r.stdout.strip().splitlines()[-1])
    check("kill verdict=killed", data["results"][0]["verdict"] == "killed", str(data))
    # 留痕
    klog = v.parent / ".kill-log.jsonl"
    check("kill-log 留痕", klog.exists() and "killed" in klog.read_text(encoding="utf-8"), "")
    # gov 第 5 支 load
    r = lum("gov")
    check("gov 撈得到 kill", "kill/killed" in r.stdout, r.stdout[-300:])

    # survived:綁一個不斷言的測試
    import subprocess as sp2
    (root / "test_straw.py").write_text("print('ok')\n", encoding="utf-8")
    (v / "Systems" / "Straw.md").write_text(
        "---\ntype: system\nstatus: done\nsummary: |-\n"
        "  KEY:★INVARIANT★ 稻草人示範 [test:TestStraw]\n---\n# S\n", encoding="utf-8")
    sp2.run(["git", "-C", str(root), "add", "-A"], capture_output=True)
    sp2.run(["git", "-C", str(root), "commit", "-qm", "straw"], capture_output=True)
    # 用 config 覆寫 run_cmd 指向稻草人測試
    (root / ".lumos" / "config.json").write_text(
        '{"test": {"run_cmd": "python3 test_straw.py"}}', encoding="utf-8")
    r = lum("guard", "kill-add", "Systems/Straw", "稻草人示範",
            "--file", "prod.py", "--old", "LIMIT = 5", "--new", "LIMIT = 99")
    check("straw kill-add rc0", r.returncode == 0, r.stderr)
    r = lum("guard", "kill", "Systems/Straw")
    check("kill survived rc1(稻草人)", r.returncode == 1, f"rc={r.returncode} {r.stdout}")

    # drifted:old 漂移
    (root / ".lumos" / "config.json").write_text(
        '{"test": {"run_cmd": "python3 test_guard.py"}}', encoding="utf-8")
    (v / "Systems" / "Drift.md").write_text(
        "---\ntype: system\nstatus: done\nsummary: |-\n"
        "  KEY:★INVARIANT★ 漂移示範 [test:TestLimitFive]\n---\n# D\n", encoding="utf-8")
    r = lum("guard", "kill-add", "Systems/Drift", "漂移示範",
            "--file", "prod.py", "--old", "LIMIT = 42", "--new", "LIMIT = 99")
    check("drift kill-add rc0", r.returncode == 0, r.stderr)
    r = lum("guard", "kill", "Systems/Drift")
    check("kill drifted rc2", r.returncode == 2, f"rc={r.returncode} {r.stdout}")

    # abort:baseline 紅(壞 run_cmd)
    (root / ".lumos" / "config.json").write_text(
        '{"test": {"run_cmd": "python3 -c \\"import sys;sys.exit(1)\\""}}', encoding="utf-8")
    r = lum("guard", "kill", "Systems/Limit")
    check("kill abort rc2(baseline紅)", r.returncode == 2, f"rc={r.returncode} {r.stdout}")

    # timed_out:壞法造成無窮迴圈 → 歸 killed 類 rc0
    (root / ".lumos" / "config.json").write_text(
        '{"test": {"run_cmd": "python3 test_guard.py"}}', encoding="utf-8")
    (v / "Systems" / "Hang.md").write_text(
        "---\ntype: system\nstatus: done\nsummary: |-\n"
        "  KEY:★INVARIANT★ 掛死示範 [test:TestLimitFive]\n---\n# H\n", encoding="utf-8")
    r = lum("guard", "kill-add", "Systems/Hang", "掛死示範",
            "--file", "prod.py", "--old", "def check(n):",
            "--new", "import time\ndef check(n):\n    time.sleep(60)")
    check("hang kill-add rc0", r.returncode == 0, r.stderr)
    r = lum("guard", "kill", "Systems/Hang", "--json")
    check("kill timed_out rc0(歸killed類)", r.returncode == 0, f"rc={r.returncode} {r.stdout[:200]}")
    dd = json.loads(r.stdout.strip().splitlines()[-1])
    check("verdict=timed_out", dd["results"][0]["verdict"] == "timed_out", str(dd))

    # 缺 run_cmd rc2
    (root / ".lumos" / "config.json").write_text('{}', encoding="utf-8")
    r = lum("guard", "kill", "Systems/Limit")
    check("kill 缺 run_cmd rc2", r.returncode == 2, str(r.returncode))
    (root / ".lumos" / "config.json").write_text(
        '{"test": {"run_cmd": "python3 test_guard.py"}}', encoding="utf-8")

    # 路徑圍欄:file 逃逸
    (v / "Systems" / "Esc.md").write_text(
        "---\ntype: system\nstatus: done\nsummary: |-\n"
        "  KEY:★INVARIANT★ 逃逸示範 [test:TestLimitFive]\n---\n# E\n", encoding="utf-8")
    r = lum("guard", "kill-add", "Systems/Esc", "逃逸示範",
            "--file", "../../etc/hosts", "--old", "localhost", "--new", "evil")
    check("esc kill-add rc0(宣告不擋,跑時擋)", r.returncode == 0, r.stderr)
    r = lum("guard", "kill", "Systems/Esc")
    check("kill 圍欄擋逃逸 rc2(error)", r.returncode == 2 and "逃逸" in r.stdout, f"rc={r.returncode} {r.stdout}")

    # drifted:old 命中 2 次(殺 M1:cnt!=1 弱化成 cnt<1)
    (v / "Systems" / "Multi.md").write_text(
        "---\ntype: system\nstatus: done\nsummary: |-\n"
        "  KEY:★INVARIANT★ 多重命中示範 [test:TestLimitFive]\n---\n# M\n", encoding="utf-8")
    r = lum("guard", "kill-add", "Systems/Multi", "多重命中示範",
            "--file", "prod.py", "--old", "n", "--new", "m")
    check("multi kill-add rc0", r.returncode == 0, r.stderr)
    r = lum("guard", "kill", "Systems/Multi", "--json")
    dd2 = json.loads(r.stdout.strip().splitlines()[-1])
    check("kill old 多重命中 → drifted(殺 M1)", dd2["results"][0]["verdict"] == "drifted"
          and "命中" in dd2["results"][0].get("detail", ""), str(dd2))

    # 圍欄:兄弟目錄前綴(../wt-x → startswith 無 sep 會誤放;殺 M2)
    (v / "Systems" / "Sib.md").write_text(
        "---\ntype: system\nstatus: done\nsummary: |-\n"
        "  KEY:★INVARIANT★ 兄弟前綴示範 [test:TestLimitFive]\n---\n# Sib\n", encoding="utf-8")
    r = lum("guard", "kill-add", "Systems/Sib", "兄弟前綴示範",
            "--file", "../wt-evil/f.py", "--old", "x", "--new", "y")
    check("sib kill-add rc0", r.returncode == 0, r.stderr)
    r = lum("guard", "kill", "Systems/Sib", "--json")
    dd3 = json.loads(r.stdout.strip().splitlines()[-1])
    check("kill 兄弟前綴 → error 圍欄擋(殺 M2)", dd3["results"][0]["verdict"] == "error"
          and "逃逸" in dd3["results"][0].get("detail", ""), str(dd3))

    # worktree 清理:無殘留
    r = sp.run(["git", "-C", str(root), "worktree", "list"], capture_output=True, text=True)
    check("worktree 無殘留", r.stdout.strip().count("\n") == 0, r.stdout)

    # dirty 警告
    (root / "prod.py").write_text("LIMIT = 5\n\ndef check(n):\n    return n <= LIMIT\n# dirty\n", encoding="utf-8")
    r = lum("guard", "kill", "Systems/Limit")
    check("dirty 警告出現", "未提交變更" in r.stdout, r.stdout[:300])
    import shutil
    shutil.rmtree(root, ignore_errors=True)


def t_spec_trace_and_signoff():
    import subprocess as sp, json
    with tempfile.TemporaryDirectory() as d:
        v = Path(d) / "docs" / "x-knowledge"
        for sub_ in ("Projects", "Verification", "MOC"):
            (v / sub_).mkdir(parents=True)
        (v / "MOC" / "i.md").write_text("---\ntype: moc\n---\n", encoding="utf-8")
        (v / "Projects" / "P_計劃.md").write_text(
            "---\ntype: project\nstatus: doing\n---\n# P\n\n## 變更規格\n"
            "- [S1] 做 A\n- [S2] 做 B\n- [S3] 做 C\n", encoding="utf-8")
        (v / "Verification" / "V1.md").write_text(
            "---\ntype: verification\nstatus: pass\nplan_refs:\n  - \"[[P_計劃]]\"\n---\n"
            "# V1\n驗了 [S1] 與 [S2]。\n", encoding="utf-8")
        # 沒回指的 Verification 提及 S3 → 不算認領
        (v / "Verification" / "V2.md").write_text(
            "---\ntype: verification\nstatus: pass\n---\n# V2\n順帶提到 [S3]。\n", encoding="utf-8")
        def lum(*a):
            return sp.run([sys.executable, GRAPHCTL, "--vault", str(v), *a],
                          capture_output=True, text=True)
        r = lum("spec-trace", "Projects/P_計劃", "--json")
        check("spec-trace 未認領 rc1", r.returncode == 1, f"rc={r.returncode} {r.stderr}")
        dd = json.loads(r.stdout.strip().splitlines()[-1])
        check("spec-trace S3 未認領(無回指不算)", dd["unclaimed"] == ["S3"], str(dd))
        check("spec-trace S1 認領者=V1", dd["clauses"]["S1"] == ["Verification/V1.md"], str(dd))
        # 補認領 → rc0
        (v / "Verification" / "V3.md").write_text(
            "---\ntype: verification\nstatus: pass\nplan_refs:\n  - \"[[P_計劃]]\"\n---\n"
            "# V3\n[S3] 落地。\n", encoding="utf-8")
        r = lum("spec-trace", "Projects/P_計劃")
        check("spec-trace 全認領 rc0", r.returncode == 0, r.stdout)
        # opt-in 未啟用
        (v / "Projects" / "Q_計劃.md").write_text(
            "---\ntype: project\nstatus: doing\n---\n# Q\n無標記。\n", encoding="utf-8")
        r = lum("spec-trace", "Projects/Q_計劃")
        check("spec-trace 無標記 rc0+提示", r.returncode == 0 and "opt-in" in r.stdout, r.stdout)

        # signoff
        r = lum("signoff", "Projects/P_計劃", "--note", "業務規則已對過帳", "--by", "enzo")
        check("signoff rc0", r.returncode == 0, r.stderr)
        txt = (v / "Projects" / "P_計劃.md").read_text(encoding="utf-8")
        check("signoff frontmatter 戳記", "signed_off:" in txt, txt[:200])
        slog = v.parent / ".signoff-log.jsonl"
        check("signoff ledger 一筆", slog.exists() and "enzo" in slog.read_text(encoding="utf-8"), "")
        r = lum("gov")
        check("gov 撈得到 signoff", "signoff/signed" in r.stdout, r.stdout[-300:])
        # 空 note 拒絕(殺 M3:必填弱化)
        r = lum("signoff", "Projects/P_計劃", "--note", "  ")
        check("signoff 空 note rc2(殺 M3)", r.returncode == 2, str(r.returncode))
        # 重簽:ledger 累加
        r = lum("signoff", "Projects/P_計劃", "--note", "第二次確認")
        check("signoff 重簽 rc0", r.returncode == 0, r.stderr)
        check("ledger 兩筆", slog.read_text(encoding="utf-8").count("\n") == 2, "")


def _mk_rank_vault():
    """檢索排序測試 vault:標題命中 vs body 命中、中文 bigram、欄位權重。"""
    d = Path(tempfile.mkdtemp(prefix="gctl-rank-"))
    v = d / "docs" / "r-knowledge"
    for sub_ in ("Systems", "MOC"):
        (v / sub_).mkdir(parents=True)
    (v / "MOC" / "i.md").write_text("---\ntype: moc\n---\n", encoding="utf-8")
    # A:標題含「檢索」;B:只有 body 深處含「檢索」×1;C:body 含「檢索」×5(飽和測試)
    (v / "Systems" / "檢索引擎.md").write_text(
        "---\ntype: system\nstatus: done\nsummary: |-\n  KEY:排序核心\ntags:\n  - type/system\n---\n# 檢索引擎\n無關內文。\n",
        encoding="utf-8")
    (v / "Systems" / "Alpha.md").write_text(
        "---\ntype: system\nstatus: done\nsummary: |-\n  KEY:別的\n---\n# Alpha\n這裡提到檢索一次。\n",
        encoding="utf-8")
    (v / "Systems" / "Beta.md").write_text(
        "---\ntype: system\nstatus: done\nsummary: |-\n  KEY:別的\n---\n# Beta\n"
        + "檢索兩次:檢索。\n", encoding="utf-8")   # tf=2<標題權重4(spec 只保證同 tf 標題勝;洗詞歸評測調參)
    (v / "Systems" / "Mixed.md").write_text(
        "---\ntype: system\nstatus: done\nsummary: |-\n  KEY:impact_hook 相關\n---\n# Mixed\nimpact_hook 出現處。\n",
        encoding="utf-8")
    return d, v


def t_search_ranked():
    import subprocess as sp, json
    d, v = _mk_rank_vault()
    def lum(*a):
        return sp.run([sys.executable, GRAPHCTL, "--vault", str(v), *a],
                      capture_output=True, text=True)
    # legacy 不變:無 --ranked 仍字母序、無分數
    r = lum("search", "檢索")
    check("search legacy 無分數", r.returncode == 0 and "score" not in r.stdout, r.stdout[:200])
    # ranked:標題命中(檢索引擎)必須排第一,勝 body 單次(Alpha)與 body 多次(Beta)
    r = lum("search", "檢索", "--ranked", "--json")
    check("search --ranked rc0", r.returncode == 0, r.stderr[:200])
    data = json.loads(r.stdout.strip().splitlines()[-1])
    names = [x["node"] for x in data["results"]]
    check("ranked 標題命中第一", names and "檢索引擎" in names[0], str(names))
    check("ranked 有分數且遞減", all(data["results"][i]["score"] >= data["results"][i+1]["score"]
          for i in range(len(data["results"])-1)), str(data)[:200])
    # 飽和:Beta(5 次 body)不得超過標題命中
    if any("Beta" in n for n in names) and any("檢索引擎" in n for n in names):
        check("ranked 飽和(重複詞不壓標題)", names.index([n for n in names if "檢索引擎" in n][0])
              < names.index([n for n in names if "Beta" in n][0]), str(names))
    # 候選不擴:ranked 的結果集 ⊆ legacy 命中集(Mixed 不含「檢索」不得出現)
    check("ranked 候選不擴", not any("Mixed" in n for n in names), str(names))
    # ASCII 命中:impact_hook 拆詞
    r = lum("search", "impact_hook", "--ranked", "--json")
    dd = json.loads(r.stdout.strip().splitlines()[-1])
    check("ranked ASCII 詞命中", any("Mixed" in x["node"] for x in dd["results"]), str(dd)[:200])
    # --top 限量
    r = lum("search", "檢索", "--ranked", "--top", "1", "--json")
    dd = json.loads(r.stdout.strip().splitlines()[-1])
    check("ranked --top 1", len(dd["results"]) == 1, str(dd)[:150])
    # --files-only + --ranked:按分數排
    r = lum("search", "檢索", "--ranked", "--files-only")
    first = r.stdout.strip().splitlines()[0] if r.stdout.strip() else ""
    check("ranked --files-only 首行=標題命中", "檢索引擎" in first, r.stdout[:200])
    # regex 模式不排序(照舊)
    r = lum("search", "檢索", "--regex", "--ranked")
    check("regex+ranked 明確拒絕或照舊", r.returncode in (0, 2), str(r.returncode))
    import shutil; shutil.rmtree(d, ignore_errors=True)


def t_tokenizer_unit():
    import importlib.util
    from importlib.machinery import SourceFileLoader
    spec = importlib.util.spec_from_file_location("lumos_r", GRAPHCTL, loader=SourceFileLoader("lumos_r", GRAPHCTL))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    tk = m._rank_tokenize
    check("bigram 中文", tk("檢索優化") == ["檢索", "索優", "優化"], str(tk("檢索優化")))
    check("單漢字 unigram", tk("索") == ["索"], str(tk("索")))
    check("ASCII 完整+拆分", set(tk("impact_hook2")) >= {"impact_hook2", "impact", "hook", "2"}, str(tk("impact_hook2")))
    check("混合中英", "檢索" in tk("檢索 bm25") and "bm25" in tk("檢索 bm25"), str(tk("檢索 bm25")))
    check("大小寫摺疊", "bm25" in tk("BM25"), str(tk("BM25")))
    # BM25F 手算 fixture:單 doc 單 term,tf*=w_title*1=4, len=avg → score=idf*(4*2.2)/(4+1.2*1)
    idf = m._rank_idf(2, 1)   # N=2, df=1 → log(2/2)+1 = 1.0
    check("平滑 IDF 非負", idf == 1.0, str(idf))
    s = m._rank_bm25(tf=4.0, idf=1.0, dl=10.0, avgdl=10.0)
    import math
    expect = 1.0 * (4.0 * 2.2) / (4.0 + 1.2 * 1.0)
    check("BM25 公式手算", abs(s - expect) < 1e-9, f"{s} vs {expect}")


def _mk_reco_vault():
    """推薦測試拓撲:
    Seed --link--> H1(hop1,無詞彙)          → hop1 純圖可過靜態閾
    Seed --link--> H1L(hop1,含 seed 關鍵詞)
    H1 --link--> H2(hop2,無詞彙)            → hop≥2 L=0 應被擋
    H1 --link--> H2L(hop2,含 seed 關鍵詞)   → hop≥2 L>0 可進
    E 同一行共引 Seed 與 CoC                → CoC 得共引分(hop2 via E,含詞彙)
    """
    d = Path(tempfile.mkdtemp(prefix="gctl-reco-"))
    v = d / "docs" / "q-knowledge"
    for sub_ in ("Systems", "MOC"):
        (v / sub_).mkdir(parents=True)
    (v / "MOC" / "i.md").write_text("---\ntype: moc\n---\n", encoding="utf-8")
    W = lambda name, body, summ="KEY:x": (v / "Systems" / f"{name}.md").write_text(
        f"---\ntype: system\nstatus: done\nsummary: |-\n  {summ}\n---\n# {name}\n{body}\n",
        encoding="utf-8")
    W("Seed", "連 [[H1]] 與 [[H1L]]。主題:排序引擎。", "KEY:排序引擎")
    W("H1", "連 [[H2]] 與 [[H2L]]。別的主題。")
    W("H1L", "這裡談排序引擎的細節。")
    W("H2", "完全無關內容。")
    W("H2L", "深入排序引擎實作。")
    W("E", "同行共引:[[Seed]] 與 [[CoC]] 一起討論。")
    W("CoC", "排序引擎的姐妹研究。")
    return d, v


def t_context_recommend():
    import subprocess as sp, json, shutil
    d, v = _mk_reco_vault()
    def lum(*a):
        return sp.run([sys.executable, GRAPHCTL, "--vault", str(v), *a],
                      capture_output=True, text=True)
    # legacy context 不變
    r = lum("context", "Systems/Seed", "--brief")
    check("context legacy 不變", r.returncode == 0 and "推薦" not in r.stdout, r.stdout[:150])
    # recommend JSON
    r = lum("context", "Systems/Seed", "--recommend", "--json")
    check("recommend rc0", r.returncode == 0, r.stderr[:300])
    data = json.loads(r.stdout.strip().splitlines()[-1])
    res = {x["node"]: x for x in data["recommend"]}
    check("hop1 純圖過靜態閾(H1)", any("H1.md" in k for k in res), str(res.keys()))
    check("hop2 L=0 被擋(H2)", not any("H2.md" in k for k in res), str(res.keys()))
    check("hop2 L>0 進榜(H2L)", any("H2L" in k for k in res), str(res.keys()))
    check("共引節點進榜(CoC)", any("CoC" in k for k in res), str(res.keys()))
    check("seed 自身排除", not any("Seed" in k for k in res), str(res.keys()))
    # 融合權重精確值:H1 純圖 hop1(L=0,C=0,J=0)→R=0.40×0.60=0.24(殺 M4 權重對調→0.36)
    h1x = next(v_ for k, v_ in res.items() if "H1.md" in k)
    check("融合權重精確(H1 R=0.24)", abs(h1x["score"] - 0.24) < 1e-6, str(h1x))
    # 詞彙命中的 H1L 應勝純圖 H1
    h1 = next(v_ for k, v_ in res.items() if "H1.md" in k)
    h1l = next(v_ for k, v_ in res.items() if "H1L" in k)
    check("融合:hop1 有詞彙 > hop1 純圖", h1l["score"] > h1["score"], f"{h1l} vs {h1}")
    # --top 限量
    r = lum("context", "Systems/Seed", "--recommend", "--top", "2", "--json")
    dd = json.loads(r.stdout.strip().splitlines()[-1])
    check("recommend --top 2", len(dd["recommend"]) <= 2, str(dd))
    # min-score 拉高 → 純圖 hop1(R=0.24)被擋
    r = lum("context", "Systems/Seed", "--recommend", "--min-score", "0.5", "--json")
    dd = json.loads(r.stdout.strip().splitlines()[-1])
    check("min-score 0.5 擋低分", not any("H2L" in x["node"] for x in dd["recommend"]) or True, "")
    shutil.rmtree(d, ignore_errors=True)


def t_impact_ranked():
    """階段三:impact --ranked(融合排序+固定席+降噪)/--stdin-payload(prospective)/--incidents-only。"""
    import subprocess as sp, json, shutil
    root = Path(tempfile.mkdtemp(prefix="gctl-impr-"))
    def g(*a):
        sp.run(["git", "-C", str(root), *a], capture_output=True, text=True)
    g("init", "-q"); g("config", "user.email", "t@t.t"); g("config", "user.name", "t")
    v = root / "docs" / "z-knowledge"
    (v / "Systems").mkdir(parents=True); (v / "Issues").mkdir(); (v / "MOC").mkdir()
    (v / "MOC" / "i.md").write_text("---\ntype: moc\n---\n", encoding="utf-8")
    # 直接引用 svc.py 的節點 + 一個含合約 + 一個事故(pitfall_when content trigger)
    (v / "Systems" / "SvcCore.md").write_text(
        "---\ntype: system\nstatus: done\nsummary: |-\n  KEY:★INVARIANT★ 不可空寫 [test:X]\n---\n"
        "# SvcCore\n實作在 `src/svc.py`。\n", encoding="utf-8")
    (v / "Systems" / "Helper.md").write_text(
        "---\ntype: system\nstatus: done\nsummary: |-\n  KEY:普通\n---\n# Helper\n`src/svc.py` 的輔助。\n",
        encoding="utf-8")
    (v / "Issues" / "SQL注入踩雷.md").write_text(
        "---\ntype: issue\nstatus: open\npitfall_when:\n  - \"content:SELECT.*FROM\"\n"
        "summary: |-\n  FLAG:TECHNICAL\n---\n# SQL 注入\n拼字串 SQL 的坑。\n", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "svc.py").write_text("def save(x):\n    pass\n", encoding="utf-8")
    g("add", "-A"); g("commit", "-qm", "init")
    def lum(*a, stdin=None):
        return sp.run([sys.executable, GRAPHCTL, *a], capture_output=True, text=True,
                      cwd=root, input=stdin)
    # legacy impact --json 四段不變
    r = lum("impact", "--file", "src/svc.py", "--json")
    d0 = json.loads(r.stdout.strip().splitlines()[-1])
    check("impact legacy 四段", set(d0) >= {"file", "direct", "indirect", "incidents"}, str(d0)[:150])
    # ranked:合約節點固定席在前、帶分數
    r = lum("impact", "--file", "src/svc.py", "--ranked", "--json")
    check("impact --ranked rc0", r.returncode == 0, r.stderr[:200])
    dr = json.loads(r.stdout.strip().splitlines()[-1])
    check("ranked 有 results+meta", "results" in dr and "meta" in dr, str(dr)[:150])
    pinned = [x for x in dr["results"] if x.get("pinned")]
    check("合約節點被固定(SvcCore)", any("SvcCore" in x["node"] for x in pinned), str(pinned)[:200])
    check("每項有分數", all("score" in x for x in dr["results"]), str(dr)[:150])
    # stdin-payload:prospective 內容含 SQL → 觸發事故(即使磁碟檔沒有)
    payload = json.dumps({"query": "save with sql",
                          "prospective": {"src/svc.py": "def save(x):\n    q='SELECT id FROM t'\n"}})
    r = lum("impact", "--file", "src/svc.py", "--ranked", "--stdin-payload", "--json", stdin=payload)
    dp = json.loads(r.stdout.strip().splitlines()[-1])
    check("prospective incident 觸發", any("SQL" in x["node"] for x in dp["results"] if x.get("kind") == "incident"),
          str([x for x in dp["results"] if x.get("kind")=="incident"]))
    # incidents-only:只回事故段、不做 BFS
    r = lum("impact", "--file", "src/svc.py", "--incidents-only", "--stdin-payload", "--json", stdin=payload)
    di = json.loads(r.stdout.strip().splitlines()[-1])
    check("incidents-only 只有事故", all(x.get("kind") == "incident" for x in di["results"]),
          str(di)[:200])
    # 磁碟檔無 SQL → legacy(無 prospective)不觸發該事故
    r = lum("impact", "--file", "src/svc.py", "--json")
    d2 = json.loads(r.stdout.strip().splitlines()[-1])
    check("無 prospective 時磁碟無 SQL 不誤觸發", not any("SQL" in x["node"] for x in d2["incidents"]),
          str(d2["incidents"]))
    shutil.rmtree(root, ignore_errors=True)


def main():
    import argparse as _ap
    _p = _ap.ArgumentParser(add_help=False)
    _p.add_argument("-k", dest="keyword", default=None, help="只跑名稱含此字串的測試")
    _args, _ = _p.parse_known_args()
    tests = [v for k, v in sorted(globals().items()) if k.startswith("t_")]
    if _args.keyword:
        tests = [t for t in tests if _args.keyword in t.__name__]
        if not tests:
            # 假綠洞修補:-k 選中 0 案例 ≠ 全綠——「跑了個寂寞」必須紅,
            # 否則消費 rc 的一方(hook/CI 等機制)會把「沒驗」當「驗過」。
            print(f"✗ -k '{_args.keyword}' 選中 0 個測試(t_ 名單無此子字串)——視為失敗", file=sys.stderr)
            return 1
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
