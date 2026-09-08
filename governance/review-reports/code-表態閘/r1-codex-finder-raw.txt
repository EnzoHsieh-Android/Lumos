severity: major

### f1 反向行號能清掉已查出的違規並放行
severity: major
blocking: 是
file: `scripts/lumos:15030`
引句:「if file_lines is None or lo < 1 or hi > len(file_lines):」
`satisfied` 填入 `scripts/lumos:999999-1` 會通過形狀驗證，接著索引越界；外層例外處理把整份判定重設為不擋，連先前已發現的缺題也消失，standard 推送因此放行。重現 R1 實得 `False list index out of range []`，斷言翻紅。

```python
# 各重現使用文末共同前置；均不寫檔。
pf = {"tier": "standard",
      "stack_questions_applicable": {"kt": ["q1", "q2"]},
      "stack_questions_meta": {"kt": [
          {"id": "kt-compose", "applicable": True},
          {"id": "kt-coroutines", "applicable": True}]}}
answers = {"kt-coroutines": {
    "status": "satisfied", "question": "q",
    "evidence": "scripts/lumos:999999-1"}}
assert m["_disp_validate"](answers) == []
rec = {"head_sha": H, "dispositions": answers}
v, d = gate(pf, {"_codeloop_read_dispositions": lambda *a: rec})
print(v["blocked"], d["error"], d["problems"])
assert v["blocked"]
```

### f2 完整刪檔的改動行漏出適用性掃描
severity: major
blocking: 是
file: `scripts/lumos:16916`
引句:「if cur_file and _stack_changed_ok(cur_file):」
完整刪除 `Screen.kt` 時，Git 輸出 `+++ /dev/null`，但解析器只從 `+++ b/` 設定檔名，因此首檔的刪行全部被跳過；若前面已有檔案，還會沿用前檔名稱而錯歸棧別。重現 R2 刪掉含 `viewModelScope.launch` 的唯一檔案，實得 `{}`，斷言翻紅；新增測試只刪檔內一行，未覆蓋此路徑。

```python
delta = ("diff --git a/Screen.kt b/Screen.kt\n"
         "deleted file mode 100644\n--- a/Screen.kt\n"
         "+++ /dev/null\n@@ -1 +0,0 @@\n"
         "-viewModelScope.launch { work() }\n")
with patch("subprocess.run",
           return_value=sp.CompletedProcess([], 0, delta, "")):
    p = m["_pitfall_diff_collect"]("old..new", R, no_lint=True)
print(p["stack_questions_applicable"])
assert "kt" in p["stack_questions_applicable"]
```

### f3 測試證據文字本身能充當已提交測試
severity: major
blocking: 是
file: `scripts/lumos:21333`
引句:「["git", "grep", "-w", "-F", "-q", "-e", name, at_sha, "--", str(rel) if str(rel) != "." else "."]」
平台 root 是 repo 根目錄時，保留未追蹤測試、填入 `test:<名>`、只提交表態治理帳，就會讓 discovery 從工作樹找到測試，而 Git 從帳本的 evidence 字串找到同名，放行未提交的測試。重現 R3 使用現有 HEAD 中僅作夾具文字的 `test_untracked`，真跑 Git 得到 `(True, '')`，斷言翻紅；佐證 file: `scripts/test_lumos.py:33088`，帳本寫入 evidence 的位置 file: `scripts/lumos:21216`。

```python
# methods_for 模擬工作樹中的未追蹤測試；Git 查詢使用真實 HEAD。
name = "test_untracked"
pidx = ({"platforms": {"python": {"root": R}}},
        {}, "python", lambda p: {name}, None)
ok, why = m["_disp_check_test"](R, H, "test:" + name, pidx)
print(ok, repr(why))
assert not ok
```

### f4 advisory 旗標也會放過高風險的紅測試
severity: major
blocking: 是
file: `scripts/lumos:21514`
引句:「if bt["status"] == "red" and not bound_advisory:」
pre-push 第一次 pitfalls 暫時失敗時，空輸出會讓它帶上 `--bound-tests-advisory`，即使 check 內重新判為 high，也不會恢復紅測試的硬擋；已有有效 pass 的推送因此放行。重現 R4 對同一組 high／紅測試／有效 pass，未帶旗標會擋，帶旗標實得 `high False`，斷言翻紅。

```python
pf = {"tier": "high", "stack_questions_applicable": {}}
overrides = {
    "_bound_tests_check": lambda *a, **kw:
        {"status": "red", "reason": "failed"},
    "_codeloop_read": lambda *a:
        {"status": "passed", "head_sha": H}}
assert gate(pf, overrides, advisory=False)[0]["blocked"]
v, _ = gate(pf, overrides, advisory=True)
print(v["tier"], v["blocked"])
assert v["blocked"]
```

### f5 推非目前分支時照修復指令重填仍然過期
severity: major
blocking: 是
file: `scripts/lumos:21763`
引句:「return _cmd_codeloop_dispositions(repo_root, marker_branch or branch, head_sha, ts, disp_file)」
checkout 在 main、推送另有程式改動的 feature 時，check 按 feature 的 SHA 查帳，但提示的 `dispositions --branch feature` 仍綁 main 的 HEAD，因此照指令反覆重填都被判過期，必須額外切換 checkout 才解得開。重現 R5 用兩個真實 commit 模擬此座標，連續兩次都得到 `False／之後動了代碼`；新增 release 測試的 tip 已在主線上，3.5 步先清空適用題，其 rc0 沒驗到讀帳，佐證 file: `scripts/test_lumos.py:33188`。

```python
base = sp.run(["git", "rev-parse", "280b34a"],
              capture_output=True, text=True).stdout.strip()
written = {}
def record(repo, branch, sha, ts, file):
    written.update(branch=branch, head_sha=sha)
    return 0
with patch.dict(g, {
    "_codeloop_git_head": lambda *a: base,
    "_codeloop_git_branch": lambda *a: "main",
    "_cmd_codeloop_dispositions": record}):
    for _ in range(2):
        m["cmd_code_loop"]("dispositions", repo=".",
            marker_branch="feature", disp_file="filled.json")
        valid, why = m["_codeloop_record_valid"](
            R, written["head_sha"], H)
        print(valid, why)
assert valid
```

### f6 同 commit 的多筆表態仍被治理時間軸合併
severity: minor
blocking: 否
file: `scripts/lumos:4734`
引句:「else d.get("ts", "") if (d.get("gate") == "code-loop" and d.get("kind") in ("dispositions", "recall-miss")) else ""),」
dispositions 的 `ts` 來自 HEAD 的 committer date，同一 commit 重填多久都相同，因此新增的去重鍵仍把多筆表態折成第一筆，佐證 file: `scripts/lumos:20663`。程序內重播兩筆相同 HEAD 時戳、不同內容的事件，`gov --full` 只印第一筆並報「共 1 筆治理事件」；新四值統計使用原始列，該段計數不受此洞影響。

### f7 字串剝除破壞題表自己的觸發規則
severity: minor
blocking: 否
file: `scripts/lumos:15296`
引句:「return _strip_string_literals(code)」
`socket.on("error", handleError)` 的 error 被剝掉，題表明列的 error 監聽規則永遠命不中；`WHERE name LIKE '%foo'` 同樣漏掉 `sql-sargable`，而相對匯入的空引號又被 `[^./]` 當成外部依賴。實跑 `_stack_applicability`，三者分別得到 `[]`、只有 `sql-index`、以及錯誤的 `vue-bundle`。

### f8 派工單把尚未核對的證據說成已驗證
severity: minor
blocking: 否
file: `scripts/lumos:19619`
引句:「工具只驗了證據存在,沒驗答案對不對;審查時把這些答案當可反駁的宣稱」
規定流程是先寫 dispositions、再派席，而寫側只驗形狀，dispatch-lens 也未呼叫錨點驗證，因此此句向審查席提供了錯誤的查證狀態。實跑 `_lens_dispositions_lines`，填入不存在的 `not-a-file.kt:1`，仍印出上述「只驗了證據存在」。

重現共同前置：在 repo 根目錄的 Python 程序中先執行此段，再分別執行 R1–R5；五段均已翻紅，Git 樹查詢使用現有 repo，其餘替身避免建立檔案或寫治理帳。

```python
import runpy, subprocess as sp, json
from pathlib import Path
from unittest.mock import patch

m = runpy.run_path("scripts/lumos")
g = m["_codeloop_guard_verdict"].__globals__
R = Path(".")
H = m["_codeloop_git_head"](R)

def gate(pf, overrides=None, advisory=False):
    real_run = sp.run
    def run(argv, *a, **kw):
        if len(argv) > 2 and argv[2] == "pitfalls":
            return sp.CompletedProcess(argv, 0, json.dumps(pf), "")
        return real_run(argv, *a, **kw)
    replacements = {
        "_bound_tests_check": lambda *a, **kw: {"status": "no-pins"},
        "_mainline_ref": lambda *a: None,
        "_gate_failopen": lambda *a: None,
    }
    replacements.update(overrides or {})
    with patch("subprocess.run", side_effect=run), patch.dict(g, replacements):
        v = g["_codeloop_guard_verdict"](
            R, diff_range="280b34a..HEAD", at_sha=H,
            branch="main", bound_advisory=advisory)
        return v, g["_codeloop_guard_verdict"].last_dispositions
```

pitfalls manifest 的唯一 claim 判為誤報：file: `scripts/lumos:21218` 使用 `with open(...) as f`，正常與例外離開均會關閉 handle。另已驗證「前題違規、下一題超時」會保留違規並擋下；f1 是例外路徑清空結果，與該正常超時分支不同。

圖譜鏡頭已執行指定的 `impact --diff 280b34a..HEAD --repo …`，以下逐項判定全部 32 個節點：

| 節點 | 判定 |
|---|---|
| Issues/code-loop守衛main-direct盲區 | 未重開原盲區；目的分支等於主線時仍使用推送範圍。 |
| Systems/bound-tests-gate | 受 f4 破壞；high 的紅測試可被 advisory 放行。 |
| Systems/canary-audit | 不影響；record 落盤合約與 second 純觀測判定未改。 |
| Systems/design-loop | 不影響；條款綁定及處置閘判準未改。 |
| Systems/guard-kill | 不影響；runner 的退出碼優先序與 JSON 輸出未改。 |
| Systems/lumos-cli-lifecycle | 不影響；sentinel 外內容保留及安裝更新邏輯未改。 |
| Systems/lumos-cli-read | 不影響；search 的 superseded／stale 過濾未改。 |
| Systems/slim-get-一行安裝 | 不影響；PowerShell 編碼及參數合約未改。 |
| Systems/slim-install-安裝器 | 不影響；注入冪等、備份、目標守衛與 shim 安裝未改。 |
| Systems/slim-uninstall-一行卸載 | 不影響；各步獨立清理、備份還原與 manifest 保留條件未改。 |
| Systems/授權與歸屬 | 不影響；授權檔排除清單及 vendored 檔頭未改。 |
| Systems/測試假綠形態 | 新 release 測試出現其警告的「未進被測分支」形態，見 f5。 |
| Systems/anchor-integrity | 不影響驗證規則；pre-push／測試檔仍屬既有錨點保護面。 |
| Systems/pitfalls-code-loop | 新適用題閘受 f1–f3 破壞；舊 tier 掃描與 pass 簿記豁免未改。 |
| Systems/loop-convergence-recording | 不影響；新增事件已列為非關門事件，處置集合判準未改。 |
| Systems/check-r-guard | 不影響；rollback／guard 雙軌解析未改。 |
| Systems/cochange-guard | 不影響；共改計算、門檻與 advisory 退出碼未改。 |
| Systems/lumos-deinit | 不影響；刪圖譜安全網與刪除範圍未改。 |
| Systems/reversibility-governance-ledger | 新表態事件的時間軸受 f6 影響；既有事件去重鍵分支維持原值。 |
| Systems/core-invariant-baseline | 不影響；此案未修改核心基線機制。 |
| Systems/judge-severity-gate | 不影響；judge 資料流與嚴重度裁定未改。 |
| Systems/check-t-sentinel | 不影響；COMBO 綁定計數與提醒判準未改。 |
| Systems/lumos-refcheck | 新增對 Git 樹的行號驗證有 f1；原工作樹呼叫未切入新分支。 |
| Systems/doctor-irreversible-hint | 不影響；Check H 掃描及只提醒的行為未改。 |
| Systems/效能檢核目錄 | 題目原文保留，但觸發選題有 f2、f7。 |
| Projects/code側刪除傳播守衛_實作計畫 | 不影響；delguard 的解析與 pre-commit 接線未改。 |
| Projects/公開精簡版_實作計畫 | 不影響生成與交付規則；生成器、白名單及安裝器未改。 |
| Projects/全repo審視_計劃 | 高風險合約測試守衛受 f4 影響；其他審視項目的實作未改。 |
| Projects/test-layers軟提醒_實作計畫 | 不影響；hook 呼叫仍保留 `|| true`。 |
| Projects/合約測試閘什麼時候跑_計劃 | 低風險 advisory 符合裁定；高風險仍須擋的部分被 f4 放寬。 |
| Projects/棧別提問表態閘_計劃 | 適用性、證據、修復座標及呈現承諾分別有 f1–f8；帳先於 marker 的呼叫順序符合規格。 |
| Projects/prepush主幹範圍修法_計劃 | 逐 ref 查詢座標保留，但新增寫側與修復指令未跟隨非 checkout SHA，見 f5。 |

已逐 hunk 讀完 1,644 行主 diff 與 455 行測試 diff，未改檔；未執行會建立暫存 repo 的原測試套件。上述重現與語法檢查已執行，八條引句均核對存在於凍結 diff。

最嚴重 severity: major,blocking 條數 5
