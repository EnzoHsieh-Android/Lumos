severity: major

## b1 守的測試雜湊拿 `git grep -F` 第一個命中的檔當「測試檔」,補強測試內容沒被偵測到(G3 修補在多模組版面失效)
severity: major
blocking: 是(能舉出具體合理的改壞:測試名不變、內容補強後重跑,存活行不重跑;被保護的是〈範圍〉2 的重跑規則)

輸入:計劃筆記在 `docs/…` 寫了 `[test:fooTest]`,測試在 `src/test/kotlin/T.kt`。`git grep -l -F -e fooTest` 依路徑排序,第一個命中的是 `docs/p/plan.md`,不是測試檔。補強測試後重跑 `choice-kill`,存活行不會重跑。

走到的函式:`_choice_test_blobs` 取第一個命中的檔的物件編號 → `_choice_tests_sha(tests, blobs)` → `_choice_kill_pick`。
- 預期:原地補強測試(名字不變、內容變)後,雜湊要變。
- 實際:雜湊沒變。反過來,只改筆記(例如 `situation-rule` 改計劃)雜湊就變,存活行被白白重跑。
- 同根:測試名是別的檔的子字串時,第一個命中的可能是正式碼或別的測試檔。兩平台同名測試只存一個 blob(`bm = {n: b}`),另一個平台的測試檔改了也偵測不到。

引句:「bm = {n: b for n, b in (blobs or []) if b}」
file: `scripts/lumos:77634`(`_choice_tests_sha`);`_choice_test_blobs` 的 `git grep -l -F -e` 在 `scripts/lumos` 同區

測試為何照綠:`t_choice_kill_rerun_rules` 的夾具測試檔在 `app/src/test/…`,`app` 排在 `docs` 前面,所以第一個命中剛好是測試檔。`feature/`、`shared/`、`src/`、`domain/` 這類名字排在 `docs` 後面。

兩版證據(臨時 repo 只有 `docs/p/plan.md` 與 `src/test/kotlin/T.kt`,逐個提交呼叫 `_choice_test_blobs` 與 `_choice_tests_sha`):

| 提交 | 動作 | 修後 blob(前 8 碼) | 修後 `tests_sha` |
|---|---|---|---|
| a | 初始 | fc7cee66 | 39c0df06 |
| doc | 只改 plan.md | da5c5c1d | 7df902f2(變了) |
| strengthen | 只補強 T.kt | da5c5c1d | 7df902f2(沒變) |

- 修前 `7826895c`:`_choice_tests_sha(t)` 只吃名字,兩次輸出都是 `1d66f5793e55734d`。文件改動不會讓它變。
- 歸因:
  - 「補強內容仍偵測不到」是有證據的原有漏查。名字雜湊本來就偵測不到,修補沒解決(G3 repair 不成立)。
  - 「改文件就讓雜湊變、存活行白白重跑」是有證據的修復回歸。修前不會,修後會。
  - `_choice_test_blobs` 的 grep 邏輯是舊的,是修補開始依賴它。
- 對案例表:G3 repair 在 `app/` 版面成立(測試通過),在上面版面為否。G3 preserve 的「沒變不重跑」在上面版面被文件改動打破。

## b2 選擇點的 AI 放行不再出現在推送前小結,但 lint-waive 仍印「推送前小結會一直列出來」
severity: minor
blocking: 否(只是提醒;doctor 仍列出)

輸入:`lint-waive choice:…` 沒有終端,記 `origin: ai`。`_lint_waivers_split` 把 `choice:` 分成第三份,`_lint_waivers_ai_pending` 只回 lint 與 sit 兩份,選擇點那份兩邊都不算。推送前小結(`ai_pending` 與 `ai_pending_situation` 兩行提醒)沒有選擇點那一行。

引句:「print("  選擇點放行要在 lumos code-loop pass 之前提交:放行檔不是帳本檔,代碼審通過後才提交它會讓留痕失效" if choice else "", end="\n" if choice else "")」
file: `scripts/lumos:42438`(`_lint_waivers_ai_pending`);`cmd_lint_waive` 的 `origin == "ai"` 分支印「推送前小結與 lumos doctor 會一直列出來」。

兩版證據(放行檔放 `choice:` 一條、`kt-situation:` 一條、普通指紋一條,各自 `origin: ai`):
- 修前 `_lint_waivers_ai_pending(r)` = 2,`situation=True` = 1(選擇點被混算進新增告警,算得到)。
- 修後 = 1 與 1(選擇點那條在小結裡消失)。
- 歸因:有證據的修復回歸。g6 把它拆出來,卻沒補一行「選擇點 AI 放行」的小結提醒。

## 已驗主張(兩版證據)
- G1 回報上限穩定:20 行曾存活、上限 14。
  - `_choice_push_judge` 回報上限 0、1、14、19、20、21 都對。
  - 放行一個抽中的行後,抽中集合不變,未抽中仍是 6 行。
  - 修前放行後 `False`(重洗),曾存活數印 14。修後 `True`,印 20。
- G5 按檔掃:3000 項 `+` 串接那支檔(ast-grep 回 -25,輸出過大)加別的檔。
  - 修前 `choice-points` 整次「沒檢查到」。
  - 修後只標那一支,其餘照列,rc 3。
- G5 的 1500 行呼叫清單:修前 ast-grep 回 -25、整次算不出來。修後 1500 行都列出,約 4.7 秒。
- G4 串接鏈:1000 項 `name + v0 + … + "/"` 那行 →「沒有壞法」。
- 單行與空改動:`H..H` 輸出「改到的行 0」、rc 0。
- 連續相同行:9 行相同的中間行 → 不唯一;5 行相同夾在不同上下文 → 唯一。
- 中文檔名與字串(`小檔.kt`)→ 壞法正確。
- ast-grep 不在 PATH → rc 3。
- G9 遠端名 `my/fork`、在 `trunk` 上不帶 `--diff` → rc 2「目前分支 trunk 就是主線」。修前版本載不到型錄表,不能做兩版對照,所以修前結果未判定。
- SBR 規則改寫:`check.py --catalog-only --sg` 型錄問題 0 個;`--sg` 給壞路徑或缺參數,訊息正確。
- `t_choice_kill_rerun_rules` 在 `app/` 版面 11 項通過(只證明 `app/` 版面成立,見 b1)。

## 未驗範圍
- G2、G6、G7、G8、G11、G12:只讀程式,沒有兩版行為執行。
- 真 Gradle、Android 的端到端耗時沒測。
- 生效日邊界只讀了判斷式,沒做行為實驗。
- 計劃〈範圍〉1 沒寫「部分檔算不出來 → rc 3」,只寫「ast-grep 不在 → rc 3」。這屬措辭不一致,不影響推送,沒單獨列 finding。

## 三問回答
1. 原問題的修復效果:G1、G5、G4、SBR 有行為證據;G3 在 `docs` 排在測試檔前面的版面不成立(b1)。
2. 修補處的正常、錯誤與相鄰呼叫路徑:b1(文件改動讓雜湊翻動)、b2(小結少一行提醒)是修補引入的退步。其餘我走過的路徑成立。
3. 新發現的同一案例修前與修後:b1、b2 的兩版結果都附在各條下。

## 圖譜鏡頭
這次沒附固定席節點(hook 回報鏡頭計算超時),無法逐條判。

最嚴重:major;blocking 共 1 條
