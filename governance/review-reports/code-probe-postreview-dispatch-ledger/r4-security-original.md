severity: major

finding: SEC-R4-01  
severity: major  
blocking: 是  
引句:「candidate = out.with_suffix(".candidate")」  
file: `governance/eval/ablation_lumos_first.py:239`, `scripts/scenario_probe.py:1287`

攻擊鏈：

- 誰：可寫入 `--out-dir` 的另一個本機帳號或非合作程序，但無權直接寫受害者其他檔案。
- 入口：父程序先建立可見的 `.pending` 檔；攻擊者由同 stem 推得尚未存在的 `.candidate` 路徑。
- 輸入：在模型執行期間建立 `candidate -> 受害者可寫的重要檔案` 的符號連結。
- 取得什麼：`Path(a.out).write_text(...)` 跟隨連結，以執行探針者權限截斷並覆寫目標，造成任意檔案破壞。後續父程序驗證發生在寫入之後，攔不回損害。
- 預期路徑：候選結果應拒絕既存連結，或以同目錄暫存檔加 `os.replace` 產生自己的普通檔。
- 實際路徑：父程序把 candidate 傳給子程序；子程序直接 `write_text`，沒有 `lstat`、`O_NOFOLLOW` 或原子替換守衛。
- 最小驗證命令（本席唯讀環境無法建立 fixture，未執行）：

```sh
d=$(mktemp -d)
printf KEEP > "$d/victim"
ln -s "$d/victim" "$d/result.candidate"
D="$d" python3.14 -c 'import os; from pathlib import Path; Path(os.environ["D"], "result.candidate").write_text("{\"results\":[]}", encoding="utf-8")'
cat "$d/victim"
```

實際會看到 victim 被探針 JSON 取代。  
歸因：未判定。before/after 均可見相同 `Path(a.out).write_text` sink，但唯讀環境無法產出同案例兩版執行結果，因此不稱為本修補造成；它是沿受影響 `main()` 查出的相鄰安全缺口。持久 SQLite 額度原問題的修法不因此失效，但這條寫入邊界仍須折入。

finding: SEC-R4-02  
severity: minor  
blocking: 否  
引句:「def text(x): return html.escape(str(x)).replace("|", "\\|").replace("\r", " ").replace("\n", " ")」  
file: `governance/eval/ablation_lumos_first.py:416`

攻擊鏈：

- 誰：提供舊消融輸出目錄／`meta.json` 的投稿者。
- 入口：操作者對該目錄執行 `--merge-only`。
- 輸入：例如 `date` 為 `\u001b]0;LUMOS-PROBE\u0007`；同理可放 OSC 52 終端剪貼簿序列。
- 取得什麼：控制終端標題；在支援 OSC 52 的終端可改寫剪貼簿。未見 shell 或任意程式執行。
- 預期路徑：外部 meta 應拒絕控制字元，或轉成可見的文字表示。
- 實際路徑：`_run_locked_batch` 接受任何非空字串；`text()` 只處理 HTML、表格分隔符及 CR/LF，ESC/BEL 保留，最後由 `print(md)` 送至終端。
- 最小驗證命令，本席已執行且輸出 `True`：

```sh
PYTHONDONTWRITEBYTECODE=1 python3.14 -c 'from governance.eval.ablation_lumos_first import render_md; z={"m1_passed":0,"n":0,"m1_rate":None,"m2_ever":0,"m2_n":0,"m2_rate":None,"m3_first_idx_median":None,"m3_n":0,"m4_gated_passed":0,"m4_gated_n":0,"m4_content_passed":0,"m4_content_n":0,"inconsistent_questions":[],"missing":0,"limit_hits":0,"instrument_errors":0}; s={"arms":{"with":z,"without":z},"expected_ids":[],"runs":1,"m1_delta_pp":None,"per_question":{},"class_counts":{}}; p="\x1b]0;LUMOS-PROBE\x07"; print(p in render_md(s,{"date":p,"claude_version":"x"}))'
```

同案例 before/after：`control_survived=True / True`，確認是既有未修缺口，不是修補回歸。另以 `<img src=x onerror=alert(1)>` 比較，before 為 raw HTML、after 為 `&lt;img`，所以本輪原始 HTML 注入問題確實修好；留下的是不同的終端控制序列入口。

安全分類：

| 類別 | 判斷 |
|---|---|
| 注入 | HTML 注入已修；仍有 SEC-R4-02 終端控制序列注入。 |
| 權限 | SQLite 最終路徑拒絕非普通檔，但 candidate 寫入沒有同等守衛，構成 SEC-R4-01。沒有服務端身分／角色授權面。 |
| 秘密 | 新帳只存時間戳；SQLite 例外多數只輸出類型，未見 token、prompt 或 API key 新增進 log。既有 source token 遮罩未被破壞。 |
| 加密 | SHA-256 只用於題號檔名，不被當授權或密碼學證明；帳內沒有需要加密的秘密。 |
| 執行邊界 | subprocess 均使用 argv list，未見 `shell=True`、字串拼 shell、`eval` 或 `exec`。Claude/Codex 既有執行模式未被本 patch 放寬。 |
| R15 外部資料 | `calls` 結構驗證新增且會整批拒收錯型；meta 控制字元仍未驗證。 |
| R16 秘密不入 log | 未發現違反。 |
| R18 反序列化／shell | 只使用 JSON 與固定 SQL；沒有 pickle、不可信 YAML 或 shell 拼接。 |
| 行動端／新依賴 | 無行動端程式；新增 `sqlite3`、`html`、`re` 均為標準庫，沒有第三方依賴。 |
| DoS／限流 | 依派工要求不做資源席裁決；僅確認帳本 claim 位於兩個模型 subprocess 之前。 |

四檔覆蓋：

- `governance/eval/ablation_lumos_first.py`：逐 hunk 全讀，另讀完整受影響的載入、派工、計分、Markdown、merge-only 與 CLI 函式。
- `scripts/scenario_probe.py`：逐 hunk全讀，另追到兩個 runner、SQLite 交易、重試控制及 `main()` 最終輸出 sink。
- `scripts/test_autonomous_loop.py`：逐 hunk全讀，精準讀新增九個帳本／競速／跨日案例及相鄰改動。
- `scripts/test_lumos.py`：逐 hunk全讀，精準讀所有被改測試與新增持久帳、結果結構、恢復、報表案例；未讀無關的超大測試區段。

原問題與保持行為：

- 持久用量帳：程式碼已把權威來源移到同一 SQLite 帳，以 `BEGIN IMMEDIATE` 原子 claim，失敗、跨日期及歸檔不退款；Claude/Codex 都在 subprocess 前 claim。`max-per-window=0` 仍完全繞過帳本。就靜態路徑而言原問題已修。
- 同題超額計分、錯型 calls、恢復路徑、meta 原 byte 保存及 raw HTML 均有對應修正。
- 沒找到由本修補確證引入的安全回歸；SEC-R4-01 歸因未判定，SEC-R4-02 已證為兩版皆有。

獨立驗證：

- snapshot 1455 行全讀；由固定 before/after 以 `-U10` 重建後 SHA-256 精確等於 `15816452e6d94bcc59ccec186ff3ccdaf69c71221c91f23cdbe6efce26cbf53f`。
- 四個工作樹檔案與 after commit 無差異。
- 四檔固定版本均通過 Python `compile()`；`git diff --check` 通過。
- 獨立執行九個 `TestScenarioProbeAblation` 帳本測試，以及 `test_lumos.py` 的 persistent-ledger／fourth-round 子集；全都在進入被測程式前因唯讀沙盒沒有可寫暫存目錄而失敗。這是環境失敗，不列程式故障，相關 runtime 行為標未驗。
- before/after 的 HTML 與終端控制字元比較使用純記憶體 AST 抽取執行，不寫 fixture、不啟動模型。
- 未讀、未採信 `implementation-*.log`；未讀其他審查員報告、作者處置清單或 staging；未啟動模型、API、push 或圖譜寫入。閱讀預算未耗盡，凍結 patch 無未讀範圍。

固定圖譜鏡頭：

| 節點 | 判斷 |
|---|---|
| Systems/ablation-lumos-first | 無登記合約；受影響函式已查。 |
| Systems/codex-harness | 無登記合約；Codex argv list 與 sandbox 旗標未破壞。 |
| Systems/測試假綠形態 | 綁定的兩支 slim 測試未改；本 diff 未破壞該合約。 |
| Systems/autonomous-iteration-loop | 無登記合約；只增相關測試。 |
| Systems/lumos-cli-read | search/superseded 行為未觸及。 |
| Systems/lumos-cli-lifecycle | re-inject 行為未觸及。 |
| Systems/bound-tests-gate | 固定席測試閘未觸及。 |
| Systems/canary-audit | record/readback 與 second telemetry 未觸及。 |
| Systems/design-loop | 處置閘第五步未觸及。 |
| Systems/guard-kill | rc 優先序與 JSON 純度未觸及。 |
| Systems/slim-get-一行安裝 | PowerShell 合約未觸及。 |
| Systems/slim-install-安裝器 | 七條安裝合約未觸及。 |
| Systems/slim-uninstall-一行卸載 | 六條卸載合約未觸及。 |
| Systems/授權與歸屬 | vendored 集合與授權標頭未觸及；無新第三方檔。 |
| Projects/規格落成可驗收條件_計劃 | 無登記合約。 |
| Systems/lumos-deinit | 無登記合約。 |
| Projects/逃逸自動記_計劃 | 無登記合約。 |
| Systems/cochange-guard | 只有技術債；本 diff 未觸及。 |
| Systems/check-r-guard | 無登記合約。 |
| Systems/節點範圍與索引守衛 | `test_lumos.py` 只改探針測試；doctor/spec-trace/MOC 相關九條合約均未觸及。 |