severity: minor

產生器檢查與截圖都沒問題。我在自己的 clone(`/tmp/lumos-seat-work/code-readme-e2e-diagram/單審-sonnet/repo`,提交 6ac960c9)跑 `python3 assets/readme-diagrams/generate.py --check`,rc=0,輸出「26 bilingual SVGs: validated, reproducible…」,其他場景沒被動到。中英兩張截圖我都看過,沒有字超出框或重疊。

新的 `validate_android_acceptance` 用 `["pass","dig"]` 比對兩個結果框,順序對調或少一個都會紅。五步用 `data-step` 比對 1 到 5 的順序。判定框與開跑前檢查各限一個。

## F1 圖與替代文字寫的 `lumos judge` 不是真指令
severity: minor
blocking: 否
file: `scripts/lumos:67227`
失敗場景:parser 裡只有 `android-e2e` 的子命令 `judge`,沒有頂層的 `lumos judge`。圖上的徽章寫 `lumos judge`,中英替代文字也寫 `lumos judge 判過不過`。讀者照圖敲 `lumos judge` 會得到 unknown command。同一份 README 正文寫的是 `lumos android-e2e judge`,圖文對不上。
引句:「b+=badge(528,614,"lumos judge","green",180)+'</g>'」

## F2 「沒過」一律導向分層查證,但 UI 流程與截圖沒過在那條路上沒有對應步驟
severity: minor
blocking: 否
file: `scripts/lumos:40654`
失敗場景:某支 Maestro 流程兩次都回 1,`_e2e_judge_ui` 判 fail,judge 印出「✗ UI 流程 …;報告 <路徑>」並回 1。照新的圖和 README,下一步是「接到分層查證,L0 先判有沒有異常」。但 L0 到 L3 吃的是 Macrobenchmark 數字和記憶體收集,UI 或截圖失敗在裡面沒有入口。只有記憶體類(接 L3 捷徑)和效能會對得上。這段措辭沿用舊圖,但新圖把它做成醒目的紅框,錯誤更顯眼。
引句:「- **Failed**: if any part failed, the result is failed; the terminal shows which part, why, and where the evidence is. Use the layered check above to dig in.」

## F3 README 說「終端會印原因和證據在哪」,記憶體那塊沒過時其實沒印
severity: minor
blocking: 否
file: `scripts/lumos:40577`、`scripts/lumos:40790`
失敗場景:記憶體 check 有 threshold_failures 時,`_e2e_judge_stability` 回 `{"result":"fail","detail":fails}`,沒有 `reason`。`_e2e_print_runs` 只印 `x["reason"]`,所以只會印「✗ 記憶體 <check>」,沒有原因也沒有證據路徑。UI 失敗會印報告路徑,截圖失敗會印差異圖,記憶體失敗兩樣都沒有。README 寫「哪一塊、原因和證據在哪」,對記憶體失敗不成立。
引句:「- **沒過**：只要有一塊沒過就是沒過，終端會印哪一塊、原因和證據在哪；照上面的分層查證往下找。」

## F4 圖底下那行把「中斷」歸為環境問題,但 README 的四種結果沒有它,實際行為也兩邊不靠
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh`(`main()` 最後一行 `return 2 if st.data["interrupted"] else rc`)
失敗場景:驗收跑到一半被 SIGTERM,腳本把 `interrupted` 設為 true,仍然交給 judge。judge 寫下「沒判完」的紀錄,終端印「沒判完」,腳本卻回 2。README 的「沒寫紀錄」只列開跑前檢查停下與換版本,「沒判完」只舉建置或安裝失敗為例,兩者都沒提中斷。只看 README 的人看不到中斷該歸哪一類。圖底部那行有提中斷,但沒說這次其實有寫一份「沒判完」的紀錄。
引句:「建置失敗、缺工具、跑到一半被中斷：是環境的問題，修好再跑」

## 圖譜鏡頭
固定席只有 `Systems/README圖產生器.md`(家,牽連檔 `generate.py`)。
- 它宣稱的行為與合約:改圖只改產生器、不手改 SVG,改完跑 `--check`,中英兩版要目視看有沒有字擠出框。這份 diff 都守住了。我另外跑了 `--check` 與看截圖,結果一致。
- 新增的 WHY 行有 `[出處:]`、`[因:]`、`[不選:]`,形狀完整。
- 筆記沒有殘留「三個回傳碼」或 `android-e2e-record` 的說法。我 grep 筆記與 assets 都找不到。
- 筆記下方的歷史段只記了 android-e2e 圖,沒有 android-acceptance 的版面與日期紀錄。這只是脈絡不完整,不算破壞合約。
- 行為與合約是否被破壞:沒有被破壞的項目。

角色卡後端兩題(`be-api-compat`、`be-authz`)沒有命中:這份 diff 只動文件、圖產生器與筆記,沒有對外 API 欄位或端點授權的變更。

這份 diff 通過產生器檢查,排版也乾淨,但圖上的 `lumos judge` 不是真指令(F1),「沒過」一律導向分層查證對 UI 與截圖失敗不適用(F2),都建議改。
