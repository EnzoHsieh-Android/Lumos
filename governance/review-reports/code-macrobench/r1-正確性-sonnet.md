severity: major

審查範圍:`scripts/lumos` 的 `_macrobench_*` 函式群、argparse 註冊、10 支測試、真結果檔和計劃/節點筆記。`python3.14 scripts/test_lumos.py -k macrobench` 跑出 48 條全綠。我在臨時副本改壞程式碼來試測試,實驗目錄已用字面絕對路徑刪除。

## 發現

### F1 S5 的測試抓不到「基準為負數」這一半的改壞(測試抓不住錯)
severity: major
blocking: 是
file: `scripts/test_lumos.py`(`t_macrobench_nonpositive_baseline`)、`scripts/lumos`(`_macrobench_worse`)

S5 要求基準是負數時用 `abs(base)` 算容差,基準是 0 時才用絕對容差。測試選的負數基準只有 -10,而 10% × |-10| = 1.0,剛好等於預設 `abs_tolerance` 1.0。所以「負數基準誤用絕對容差」跟「正確的 abs(base)×10%」在這支測試裡算出同一個數。

重現:把 `_macrobench_worse` 的 `if base != 0 else cfg["abs_tolerance"]` 改成 `if base > 0 else cfg["abs_tolerance"]`,這是對 S5 負數半邊的合理改壞,表現是負數基準不再按比例算容差。我用測試裡的五組輸入(-10→-12、-10→-9.5、-10→-8.5、0→0.5、0→1.5)比對原版和改壞版,結果完全一致,所以這支測試照綠。

兩版輸出開始不同的輸入:
- 基準 -100 → -95:原版容差 10,不算退步;改壞版容差 1,誤報退步。
- 基準 -0.5 → -0.2:原版容差 0.05,報退步;改壞版容差 1,漏報。

同一支測試的 0 基準案例也沒用過自訂 `abs_tolerance`,把 `cfg["abs_tolerance"]` 寫死成 1.0 一樣不會紅。

引句:「手算:基準 P50 -10、容差 10% → 允許慢 1ms;基準 0 → 用絕對容差 1ms。」

### F2 基準檔的項目內容沒驗證,手改或損壞會讓指令噴 traceback 並回 1
severity: minor
blocking: 否
file: `scripts/lumos`(`_macrobench_load_baseline`、`_macrobench_cmp_metrics`)

`_macrobench_load_baseline` 只檢查 `entries` 是 dict,不檢查每個項目的內部欄位。基準檔裡某項目的 `metrics.t` 只有 `{"median":1}` 時,比對會在讀 `b["maximum"]` 處丟 `KeyError`。我實際走過這條路徑:`_macrobench_compare` 噴 `KeyError('maximum')`,沒有被接住。

這違反「恆回 0」的設計,也繞過了「基準檔讀不了」那條友善路徑。觸發條件是手改或寫到一半損壞的基準檔,所以我只標 minor。

引句:「entries = json.loads(bpath.read_text(encoding="utf-8"))["entries"]」

### F3 同一情境出現在兩個檔時的處理沒有測試,訊息也誤導
severity: minor
blocking: 否
file: `scripts/lumos`(`_macrobench_collect`、`_macrobench_update`)

實跑:同一份結果檔複製在 `out/a/` 和 `out/b/`,`--update-baseline` 把兩份都丟掉,輸出「基準沒更新:這次一個結果檔都沒讀成功」。檔案其實都讀成功了,只是被當成重複丟掉,使用者會去找不存在的讀檔錯誤。

另外,整個 `t_macrobench_*` 都沒有「兩個檔同一情境」的案例。把 `_macrobench_collect` 裡的重複檢查整段拿掉,10 支測試還是全綠。如果消費專案的 `results_dirs` 涵蓋了 Gradle 在不同目錄留下的同一份結果檔副本,所有情境都會被丟掉(Gradle 是否真的這樣複製未證實)。

引句:「failed.append({"file": rel, "reason": f"{k} 也出現在 {seen[k]},兩份都不收"})」

## 其他鏡頭

**S1–S10 逐條對實作**
- S1、S2:符合。兩道門缺一不可,`delta > tol and outside` 都有對應測試。
- S3:符合,比的是 `model` 加 `fingerprint`。
- S4:符合,`outside` 在越大越好時比 `minimum`。
- S5:實作正確(見 F1,問題在測試)。
- S6:符合。`merged = dict(baseline); merged.update(current)` 把舊項目蓋進來,全部失敗時不寫檔。把它改成 `merged=current` 測試會紅。「現有基準檔讀不了時不覆寫」那支分支沒測試,但不在 S6 條文內,所以不另立一條。
- S7:符合,各種壞設定回 2,沒接和有退步回 0。
- S8:符合。P99 只進 `listed`,測試有對照。
- S9:符合。`b[stat] <= 0 < c[stat]` 且只限 `frameOverrunMs` 的 P90。測試用「基準 0 → 0.5」,差幅沒過容差,所以只有跨零規則會讓它成立;改成 `< 0` 會紅。
- S10:符合,`rglob("*-benchmarkData.json")` 配巢狀目錄。把 `rglob` 改成 `glob` 測試會紅。

**真結果檔格式**
真檔的 `metrics` 只有 `timeToInitialDisplayMs`,三個必要鍵齊全。`sampledMetrics` 的兩個指標都有 P50/P90/P95/P99,另帶 `runs`,讀取器不看 `runs`。真檔不會讓整檔讀失敗。
讀取是整檔全有或全無:任何指標缺 median/minimum/maximum 或缺 P50/P90,整個檔都進 `failed`。這符合計劃的意圖,沒有偏離條款。

**圖譜固定席**
- `lumos-cli-read`、`測試假綠形態`、`design-loop`、`guard-kill`、`bound-tests-gate`、`lumos-cli-lifecycle`:合約行談 search 篩選、還原翻紅釘、處置閘、guard kill 的 rc、`reinject`。這份 diff 只新增獨立子指令、help 表一行和 argparse 註冊,沒有碰那些函式。我不認為會破壞它們。
- `測試假綠形態`的「還原翻紅釘須有前置斷言」:S1、S3、S9 的測試有前置對照,S5 沒有(見 F1)。
- `pitfalls-code-loop`、`loop-convergence-recording`(RISK 標記):這份 diff 沒碰到。
- 各節點對 `scripts/test_lumos.py` 的牽連是測試檔新增函式,不改既有測試。
- 殘留決策和「這次新增的殘留」段:沒有出現。

**表態記錄**
我沒有逐條驗證表態記錄。與本次 diff 相關的 py-eventloop、py-parallel、py-memory、py-hotpath 都標 na,理由與同步程式的事實相符。

**邊界輸入**
- 基準 ≤0、基準 0 不會除以零。
- 缺百分位會丟 `ValueError`,進 `failed`。
- 參數鍵順序用 `sort_keys` 固定。
- 一個情境在同一個檔內重複時,後者靜默覆蓋前者,屬極端情形,未標 finding。
- 基準檔寫入走 `_write_lf`(暫存檔再原子替換),寫到一半被中斷不會留半截檔。

總結:本報告最高等級為 major(F1)
