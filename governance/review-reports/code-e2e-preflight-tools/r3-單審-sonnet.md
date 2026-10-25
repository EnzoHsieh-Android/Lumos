severity: minor

## F1 README 回傳碼表說建置或安裝失敗「不會記成沒過」，實際可以記成沒過
severity: minor
blocking: 否

file: README.md、README.en.md 的回傳碼表，回傳 1 那一列。對照 ``scripts/lumos: `40654` `` 的 `_e2e_evaluate`：`result = "fail" if "fail" in rs else ("unjudged" if probs or "unjudged" in rs else "pass")`。對照 ``scripts/templates/android-e2e-run.sh: `364` `` 的 `accept`：`build` 回 1 之後不會中止，後面的 UI 流程照跑。

失敗場景：
- 輸入：e2e 段的 `build` 寫 `exit 1`，Maestro 一律回 1。
- 路徑：`build` 失敗，`install` 找不到 APK 也失敗，UI 流程兩次都回 1。`_e2e_evaluate` 的 `rs` 於是含有 `fail`。
- 實測輸出：整份紀錄是「Android 端到端驗收:沒過」，rc 為 1。`build`、`install` 兩列是 `?`，UI 那列是 `✗`。
- 結果：README 那句「建置或安裝失敗，會記成『沒判完』，不會誤記成『沒過』」只在其他幾塊剛好都過或都沒跑時才成立。照這句判讀的人看到「沒過」，可能去查 UI，而不是建置。
- 影響範圍：回傳碼仍是 1，表本身的分類沒錯，錯的是括號裡的例子。
- 圖譜側：`Systems/android-e2e-acceptance` 有一行寫「建置或安裝失敗…記成 unjudged 而不是 fail」，程式只在 UI 本身是過的時候才做到。測試 `t_android_e2e_judge_tool_failure` 的每個案例都帶「UI 是過的」前提，沒有涵蓋這個組合。

歸因：有證據的原有漏查。before 版（ff0bd815）寫的是「少了工具會記成沒判完」，同樣沒交代其他塊失敗時整體會變「沒過」。修補只換了例子，沒改掉這個過度承諾，但新措辭確實是修補帶進來的。
查證命令：用 `test_lumos` 的 `_e2e_script_env` 起一份專案（`build` 設 `exit 1`、假 maestro 的 `rcs` 設 `1 1`），整套跑一次，結果如上。
建議：改成「建置或安裝失敗會記成『沒判完』，除非別的塊也失敗」，或把例子換成不會被其他塊蓋掉的情況。

claim: 回傳 1 那列的例子對所有情況成立。input: 建置失敗加 UI 流程失敗。expected: 沒判完。case_source: 本席補的案例（原案例的「README 回傳碼表」repair 案例只對照過文件，沒跑）。before: 同樣會判沒過。after: 判沒過。comparison: 兩端行為相同，歸因為原有漏查。

引句:「紀錄寫好了，但有一塊沒過，或有一塊沒跑成（例如建置或安裝失敗，會記成」

## 三問

**1. 原問題的修復效果有何行為證據？**

兩支範本讀 `test_data` 的那一行逐字相同，測試改成各抽出那一行比相等，這個修復成立。
- 讀碼：after 版 `android-e2e-run.sh` 的那一行 `test_data = bool((st.get("test_data") or {}).get("value"))`，跟 `android-stability-collect.sh` 第 379 行 `.strip()` 之後完全相同，兩邊各只有一行含 `get("test_data")`。
- 跑測試：`python3.14 scripts/test_lumos.py -k android_e2e_preflight_stability_tools`，before 和 after 都是 18 passed。
- 破壞：只把 after 版 e2e 側的 `"value"` 改成 `"valu"`，結果 14 passed、4 failed。紅的有三條行為斷言（宣告測試資料卻缺 java_heap_dump 沒擋），加上「那一行相同」一條。
- 還原：改完用 `git checkout` 還原，clone 回到乾淨。
- 原問題是「判斷式只靠子字串存在」。before 版只檢查 `cond in 全文`，把整行改成 `not bool(...)` 仍然通過；after 版改成逐行比相等。

claim: 兩支範本讀 test_data 的那一行被機械守住。input: 只改 e2e 側的欄位名。expected: 測試紅。case_source: 作者案例 G1 repair，本席重跑。before: 未對 before 版做同一破壞，未判定。after: 紅。comparison: 只有修後證據，不能單憑它證明修前沒守住。

**2. 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立？**

成立。
- 測試的六個情境全綠：缺 trace_processor 擋下回 2；宣告測試資料卻缺 java_heap_dump 擋下回 2；沒宣告測試資料時缺 java_heap_dump 放行；兩者都在放行；e2e 沒開 stability 時兩者都缺也不擋；只有最外層 stability 時看 e2e 段、不擋。
- 擋下情境都檢查了「沒碰 App」（`installed.apk`、`maestro.log` 不存在）。整套跑的放行情境檢查了 APK 真的裝上。
- `cfg.get("stability") or {}` 在欄位缺或為 None 時都能走過。
- 本席沒驗 `stability` 為非 dict 的相鄰路徑。before 版同樣會在這裡出錯，不是修補造成的。
- `generate.py --check`：before 24 張、after 26 張，都通過。`git diff` 顯示動到的只有兩張 android 舊圖和新增兩張。
- 新圖的五步順序、必須過、效能只提醒、三種回傳碼、目前不擋推送，都跟範本與 judge 對得上。
  - 順序：`build`、`install`、`ui`、`visual`、`stability`、`macrobench`。
  - 只提醒：`_e2e_judge_macrobench` 只寫 notices。
  - 不擋推送：`scripts/lumos` 和 `scripts/hooks/pre-push` 裡沒有 `android_e2e` 的擋下接線。
  - 範本改道與上列行為沒有衝突。
- 兩張截圖（zh、en）文字都在框內，沒有溢出或重疊。
- README 的「上一張圖」確實指緊接在前的 android-e2e 圖，中間沒有別的圖。

**3. 新發現的同一案例在修前、修後各是什麼結果？**

只有 F1。同一輸入在修前、修後都得到整份紀錄「沒過」、rc 1，行為沒變，文件措辭才是問題，所以歸因為原有漏查。

未驗範圍：
- 新圖把五步全畫成固定流程，但截圖、記憶體、效能各自要在設定開了才跑，圖上沒標。README 內文有寫，圖沒寫，沒有具體失敗場景，所以沒列 finding。
- 腳本被 Ctrl-C 打斷時會寫一份「沒判完」的紀錄，卻回 2。圖和 README 說「2 沒寫紀錄」，這個路徑跟它不吻合。這是原有行為，我也沒具體走過，列在這裡不算 finding。
- 圖上的「99.5%」是預設值。`visual_threshold` 可以調到 99.5 到 100 之間，圖沒寫「預設」，只是精度問題。
- 沒對 before 版跑破壞測試。作者提供的案例也沒有 before 證據，所以「修前測試抓不到」這一點留未判定。

## 圖譜鏡頭

- `Systems/測試假綠形態`（★INVARIANT★ 修 bug 的還原翻紅釘要配前置斷言）：不影響，反而遵守。新測試加了「★前置★ 兩支範本各恰好一行讀 test_data」，現場不成立時比對不會假綠。
- `Systems/README圖產生器`：不影響。新場景用了標題集合加 `validate_android_acceptance`（五步依序、三個單一區塊），`--check` 通過。筆記補了一行 WHY，`lumos lint` 0 問題。
- `Systems/arch-alignment-lens`、`Systems/test-quality-handbook`：不影響，只是牽連到 `test_lumos.py`，沒有改動它們宣稱的行為。
- `Systems/lumos-cli-read`、`bound-tests-gate`、`canary-audit`、`guard-kill` 的 INVARIANT：不影響。本次沒碰 search、code-loop check、canary、guard kill 的行為或對應綁定測試。
- `Systems/android-e2e-acceptance`：它那行 WHY「建置或安裝失敗…記成 unjudged 而不是 fail」跟程式只在其他塊都過時才成立，見 F1。這一行不是這次 diff 新增的，未改動。
- 其餘列為「超出上限只列名」的節點：沒看到 diff 會破壞它們的跡象，沒有逐篇細讀。

## 角色鏡頭

- be-api-compat：不影響。範本只新增一道前置檢查，`macrobench.json` 的欄位沒有改名、刪除，也沒有改預設值；缺工具的情境照舊回 2。
- be-authz：不適用。沒有端點，也沒有資料授權相關改動。

修補本身與新圖對得上程式行為，唯一的發現是 README 回傳 1 那列的例子措辭過度承諾，影響很小。
