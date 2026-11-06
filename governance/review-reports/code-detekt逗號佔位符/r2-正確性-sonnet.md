severity: major

## F1 計劃正文三處仍把新提醒寫成 T3，與程式及本輪更正矛盾
severity: major
blocking: 是
引句:「- 實作更正(2026-11-06):範圍 5 與 [S7] 說的新提醒「T3」,實作時發現 T3 已是既有的「等號寫法」那則,新提醒改叫 T4;條款原文保留不改,天花板與兩條 REVISIT 已改成 T4。」
file: `docs/lumos-toolchain-knowledge/Projects/Android的detekt推送前真的擋_計劃.md:64`
file: `docs/lumos-toolchain-knowledge/Projects/Android的detekt推送前真的擋_計劃.md:65`
file: `docs/lumos-toolchain-knowledge/Projects/Android的detekt推送前真的擋_計劃.md:69`
歸因:有證據的原有漏查。這三行修前就寫 T3，修後原封不動，不是修補造成的回歸。但它們就是原問題（代號與程式不一致）的同族，本輪修補只掃了「天花板」和「REVISIT」兩處。

- 輸入：照計劃正文做事的人，例如要回頭處理 REVISIT 的人。
- 走到哪：
  - 第 64 行寫「健檢 T1、T3 會把這件事印出來」。程式裡 T3 是「等號寫法」（`scripts/lumos:38806`），印「型別規則推送前不擋」的是 T1 和 T4。
  - 第 65 行寫「沒貼就是 T3 提醒」。
  - 第 69 行寫「健檢只看字面印 T3」。
- 壞在哪：這三處是正文敘述，不是驗收條款（範圍 5 在第 51 行，[S7] 在第 85 行，才是條款）。「條款原文不改」的理由涵蓋不到它們。更正紀錄只說「天花板與兩條 REVISIT 已改成 T4」，沒提這三處。照這三行去查 T3 的人會找到錯的那則提醒，跟原問題同一種錯。
- 兩版查證：
  - `git -C <repo> show 8d63aa1d3:<計劃檔> | grep -n T3`，結果第 51、64、65、69、85、96、99、100 行都有。
  - `git -C <repo> show e99675dee:<計劃檔> | grep -n 'T3'`，結果第 51、64、65、69、85 行還在。只有第 96、99、100 行改成 T4。
  - 重現：`grep -n 'T3' <計劃檔>`。
- 修好條件：第 64、65、69 行改成 T4。第 64 行是「T1、T4」。

## 三問回答

**① 原問題的修復效果：天花板與兩條 REVISIT 部分修好，整份計劃沒修乾淨。**
- `grep -n '_DETEKT_ADVICE_ORDER\|"T3"\|"T4"' scripts/lumos` 的結果：
  - 順序是 `("T1","T2","T3","T4",…)`。
  - T3 是「有參數用了等號寫法」（`scripts/lumos:38806`，觸發在 `:38972`）。
  - T4 是「沒有任何 detekt<變體> 的 Gradle 任務」（`:38809`）。
  - `:38795` 附近的程式註解也明寫「計劃字面叫 T3，但 T3 已是等號寫法，改用 T4」。
- 計劃第 96、99、100 行現在都是 T4，與程式一致。這部分已修復。
- 殘留見 F1。

**② 相鄰說法是否仍成立：只有一部分成立。**
- `Android的detekt規則說實話_計劃.md:85` 的判定表有 T4 列，T3 列（`:80`）是等號寫法。兩者與程式一致，成立。
- `Systems/lint-declaration-health.md:32` 和 `:88` 都稱 T4，並註明計劃字面叫 T3。成立。
- 推送前計劃的第 64、65、69 行不成立，見 F1。

**③ 新議題四條逐項對照程式：四條都屬實。格式也合規。**
- 條 1：`_lint_run_and_parse` 開頭 `if _lint_gate_covers(cmd): return [], False`（`scripts/lumos:39572` 起，約第 39600 行）。入口對傳進來的、已換好檔名的 cmd 再判一次，與「對成品命令再判一次」吻合。
- 條 2：`_lint_spawn(injected_cmd, repo_root, fail_info)`（`scripts/lumos:39553`、`:39567`）。`fail_info` 是傳入的字典，在其中寫 `too_long`，閘端以 `fi.get("too_long")` 讀（約 `:40595` 一帶）。
- 條 3：指紋公式有兩份。`_lint_new_oversize` 用 `"oversize"`（`:40259`），`_lint_new_sep_split` 用 `"separator-path"`（`:40615`）。放行提示在 `:72421` 與 `:72425` 分兩段處理。
- 條 4：`.github/workflows/ci.yml:150-162` 用 curl 下載 detekt-cli，再用 `sha256sum -c` 比對。
- 摘要行格式：
  - PITFALL 帶 `[出處:]`、`[根因:]`、`[repro:]`，必有鍵齊全，`repro` 三選一也滿足。
  - REVISIT 用 `REVISIT:YYYY-MM-DD 一句要做什麼` 的寫法。
  - 執行 `python3.14 scripts/lumos lint Issues/detekt逗號佔位符代碼審放行的小問題`，結果「0 問題」。

**未驗範圍：**
- 沒實跑條 1 的檔名 `x{LINT_FILES}.kt` 重現。只做了程式閱讀對照。
- 沒驗卷證 `r1-intake.md` 的內容，也沒讀 r1 開頭的檔。
- 沒驗 `Systems/pitfalls-code-loop` 是否有對應連結的內容。

severity: major
