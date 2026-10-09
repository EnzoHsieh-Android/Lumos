severity: major

finding: D4-CALLS-NULL

severity: major

blocking: 是

引句:「if calls is not None and any(not isinstance(call, (list, tuple)) or len(call) != 2」

file: `governance/eval/ablation_lumos_first.py:146`

原問題判定：未完全修好。巢狀錯型 `calls` 已拒收，但顯式 JSON `null` 仍被當成「沒有 calls 欄位」放行，仍可灌低 M2／M3。

具體輸入：正式結果列 `{"id":"a","passed":true,"calls":null,"n_calls":0,"reason":"ok"}`。

預期路徑：`invalid_batch_evidence()` 應把顯式 `calls:null` 判為錯型，整檔拒收；舊 shard 若完全缺少 `calls` 欄位，仍可維持 legacy 相容。

實際路徑：`row.get("calls")` 得到 `None`，`calls is not None` 為假，驗證回傳空清單；`backfill_limit()` 再把它轉成空 calls，`_arm_stats()` 把該列納入 M2，結果為 `0/1`，而不是資料不可判。

最小驗證命令：

```sh
PYTHONDONTWRITEBYTECODE=1 python3.14 -c 'import importlib.util,pathlib; p=pathlib.Path("governance/eval/ablation_lumos_first.py"); s=importlib.util.spec_from_file_location("a",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); d={"arm":"with","results":[{"id":"a","passed":True,"calls":None,"n_calls":0,"reason":"ok"}]}; print(m.invalid_batch_evidence(d,"with")); r=m.backfill_limit(dict(d["results"][0])); print(m._arm_stats([r],["a"],1)["m2_ever"],m._arm_stats([r],["a"],1)["m2_n"])'
```

實際輸出：`[]`，接著 `0 1`。

同案例前後歸因：before `532f5a15` 與 after `05e87b54` 都輸出 `evidence=[]`、`M2=0/1`；屬原 calls-schema 缺口未完全修復，不是本修補引入。

既有行為保持：`with-shard0.json` 完全缺少 `calls` 的 legacy 相容路徑仍可保留；本 finding 只要求區分「欄位不存在」與「欄位存在但為 null」。

回歸判定：未證出 after-only 回歸。

finding: D4-MARKDOWN-INJECTION

severity: major

blocking: 是

引句:「def text(x): return html.escape(str(x)).replace("|", "\\|").replace("\r", " ").replace("\n", " ")」

file: `governance/eval/ablation_lumos_first.py:416`

原問題判定：未完全修好。原始 HTML 尖括號已轉義，但報表仍把不可信字串當 Markdown 語法，而非純文字。

具體輸入：合法 printable 題號或來源 meta 為 `![remote](https://example.invalid/pixel.png)`；它不含逗號、控制字元、換行或表格分隔符，可通過現有題號入口。

預期路徑：題號、健康檔名、日期與 CLI 來源只應顯示為字面文字，不應建立圖片或連結節點。

實際路徑：`html.escape()` 不處理 `![]()`；完整 `render_md()` 輸出中該 token 原樣出現三次，包括標題與題目表格。CommonMark renderer 會把它解讀為圖片，報表可被偽裝，且允許支援外部圖片的檢視器發出外部請求。

最小驗證命令：

```sh
PYTHONDONTWRITEBYTECODE=1 python3.14 -c 'import html; s="![remote](https://example.invalid/pixel.png)"; print(html.escape(s).replace("|","\\|").replace("\r"," ").replace("\n"," "))'
```

實際輸出仍為 `![remote](https://example.invalid/pixel.png)`。本席另以固定 after 的完整 `render_md()` 路徑執行，該 token 計數為 3。

同案例前後歸因：before 與 after 的完整 `render_md()` 都保留三個相同 Markdown image token；屬既有報表文字處理缺口未完全修復，不是本修補造成。

既有行為保持：after 對 `<img ...>`、`|`、CR/LF 的處理有效；壞／空 meta 也只在報表顯示來源未知，原始 `meta.json` 不再被覆寫。

回歸判定：未證出 after-only 回歸。

四檔覆蓋：

- `governance/eval/ablation_lumos_first.py`：已讀全部修補 hunk 及 loader、validator、scoring、merge、renderer、CLI 呼叫鏈；有 D4-CALLS-NULL、D4-MARKDOWN-INJECTION。
- `scripts/scenario_probe.py`：已讀全部修補 hunk 及兩個 runner、重試、fatal、結果落檔呼叫鏈；持久 SQLite 帳、冷卻、零值停用、claim-before-launch、重試前核帳與 fatal 分流未見額外 finding。檔案型 SQLite／競速實跑因唯讀環境未驗。
- `scripts/test_autonomous_loop.py`：已讀全部修補 hunk；ledger 競速、死亡保留、舊檔辨認等測試有覆蓋，但需暫存目錄，本席無法獨立完成。舊 shard 測試刻意允許完全缺 `calls`，不構成放行 `calls:null` 的理由。
- `scripts/test_lumos.py`：已讀全部修補 hunk；逐題灌分、錯型 calls、來源 meta、raw HTML、恢復流程測試均有覆蓋；錯型集合漏 `null`，報表攻擊只測 `<img>`，未測 Markdown image/link 語法。

固定版本三分判定：

- 逐題計分原問題：修好。本席無落檔同例執行，100 筆題 A 成功加 1 筆題 B 失敗時，before M1=`0.9901`，after M1=`0.5`，並記 `excluded_surplus=99`。
- calls schema 原問題：部分修好；巢狀非二元素／非字串已拒收，顯式 `null` 未修，見 D4-CALLS-NULL。
- 持久用量帳原問題：靜態路徑符合「同帳五小時、0 停用、失敗不退款、跨日不重置、冷啟五小時」；本席未能做 SQLite／雙程序獨立實跑。
- 來源保留原問題：純合併不再改寫壞、空或 symlink `meta.json`；來源未知只進報表。未見 after-only 回歸。
- 報表原問題：HTML 尖括號修好，Markdown 語法未修，見 D4-MARKDOWN-INJECTION。
- 舊檔辨認原問題：本席以不落檔 fake glob 執行 `_result_json_files()`，`with-shard0.json` 與 `without-q-good.json` 被辨認，`with-notes.json`、`summary.json`、`with-shard-x.json` 被排除。
- 相鄰既有行為：正常一題一場計分、legacy shard、零值停用及純合併來源未知的程式路徑保留；未證出修補造成的回歸。
- 新發現歸因：兩條 finding 在 before／after 同案例皆重現，均標為原缺口未完全修，而非修補引入。

獨立執行與未驗：

- `AST OK 4`：四檔以 Python 3.14 `ast.parse` 成功。
- `git diff --check 532f5a15..05e87b54 -- 四檔`：無輸出。
- 不落檔純函式執行：逐題灌分 before/after、`calls:null` before/after、Markdown token before/after、正式／備註／legacy shard 名稱辨認均已實跑。
- 嘗試執行 9 支新增 unittest；9 支都在進入測試本體前因唯讀沙盒沒有可寫暫存目錄而 `FileNotFoundError: No usable temporary directory`。這是環境失敗，不列程式故障。
- 未驗：SQLite 真檔交易、五秒鎖逾時、兩程序最後名額競爭、父程序死亡、候選／pending 歸檔、CLI 純合併落檔與完整測試套件。
- 作者 raw 僅作作者量測：`implementation-ablation-corrected.log` 記 32 tests OK；`implementation-probe-boundary-corrected.log` 記 138 passed；`implementation-parent-race.log` 記 1 OK；`implementation-stop-contracts.log` 記 3 passed。較早的 `implementation-*-final.log` 保留 `re` 未匯入的紅燈，固定 after 已新增 `re` 且 corrected log 另存；這些均不冒稱本席獨立執行。

固定圖譜鏡頭：

- `Systems/ablation-lumos-first.md`：無登記合約；本次 production 改動落在其責任內，兩條資料／報表缺口如上。
- `Systems/codex-harness.md`：無登記合約；兩 runner 的持久 claim 接線未見額外 finding。
- `Systems/測試假綠形態.md`：既有兩支 slim 綁定測試及其「前置斷言」合約未改；新增灌分測試有先證明 100 筆 A／1 筆 B 現場。
- `Systems/autonomous-iteration-loop.md`：無登記合約；只改其測試檔內探針測試類，未改迴圈 production 行為。
- `Systems/lumos-cli-read.md`：search 排除 superseded／保留 stale、三路一致、stderr/json 合約未觸及。
- `Systems/lumos-cli-lifecycle.md`：re-inject sentinel 外 byte-equal 合約未觸及；兩條 debt 未改。
- `Systems/bound-tests-gate.md`：固定席綁定測試真跑及 fail-closed 合約未觸及。
- `Systems/canary-audit.md`：record/second 落盤讀回合約未觸及；second 純 telemetry 合約未觸及。
- `Systems/design-loop.md`：處置閘第五步、條款句式／綁定／回退／可見行解析合約未觸及。
- `Systems/guard-kill.md`：rc 優先序合約未觸及；JSON rc0/1 stdout 純度合約未觸及。
- `Systems/slim-get-一行安裝.md`：三支 PS1 ASCII/no-BOM 合約未觸及；不得使用 `$Args` 合約未觸及。
- `Systems/slim-install-安裝器.md`：sentinel 外 byte-equal、冪等、FULL-BACKUP、manifest、三層目標守衛、Windows interpreter、孤兒 cmd 碰撞七條合約均未觸及。
- `Systems/slim-uninstall-一行卸載.md`：bin 比對、清理步驟獨立、skill 備份、CLAUDE 精確還原、cmd shim 獨立、manifest 清理六條合約均未觸及。
- `Systems/授權與歸屬.md`：授權檔不得 vendor、主程式／vendored 檔 SPDX 兩條合約未觸及。
- `Projects/規格落成可驗收條件_計劃.md`：無登記合約，未見責任邊界破壞。
- `Systems/lumos-deinit.md`：無登記合約，未觸及。
- `Projects/逃逸自動記_計劃.md`：無登記合約，未觸及。
- `Systems/cochange-guard.md`：只有 rename/shallow-clone debt；未觸及。
- `Systems/check-r-guard.md`：無登記合約，未觸及。
- `Systems/節點範圍與索引守衛.md`：重用抽取解析、尊重 MOC 範圍、無索引明示跳過、只按合約數門檻、段落順序、閘名登記、單一懸空常數、bool 特判、三道治理帳九條合約均未觸及；`scripts/test_lumos.py` 的本輪 hunk 未改這些測試函式。

固定鏡頭結論：未發現本 delta 破壞已登記 ★INVARIANT★；兩條 blocking finding 是 `Systems/ablation-lumos-first` 責任內、計劃 S16 與報表安全邊界仍未完全落地。

未讀範圍：凍結 patch 1455 行已逐 hunk 全讀；四檔未改動區只讀與本 delta 直接相連的函式上下文，未重讀 `scripts/test_lumos.py` 其餘約三萬八千行。未讀其他審查員報告、作者處置清單及 staging；未發真模型、付費 API、push，未改 repo。閱讀預算未耗盡。

總結: 最嚴重 severity=major；blocking=2