severity: minor

## g1 run_cmd 的行尾註解含單引號時,整行對 Android 檢查不可見
severity: minor
blocking: 否
引句:「`#` 開頭的詞起到行尾是 shell 註解,不算任務」
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:40647`(`_detekt_split_segments` 在切詞失敗時回 None;`_detekt_walk_segments` 對 None 直接 `continue` 跳過整行)

r2 的註解修補在切詞之後才認 `#`。POSIX shell 的註解裡可以有不成對的引號,但 `shlex` 會因此拋 ValueError,整行就被丟掉。

1. 平台 run_cmd 寫成 `./gradlew test # it's fine`,專案是 Android,profile 是 kotlin-junit。
2. `_gradle_task_list` 回 `[]`,`_situation_rule_android_cmd_problem` 沒有任何原因,回 None,檢查放行。
3. 壞的頂層 `test` 沒被早擋,要等殺傷力基準跑完才失敗。這正是這個檢查要避免的事。

重現(driver 在 scratchpad 的 `g/d2.py`,載入 scripts/lumos 後直接呼叫):
- `_gradle_task_list("./gradlew test # it's fine")` 回 `[]`。
- `_gradle_task_list("./gradlew clean && ./gradlew test # it's fine")` 回 `[]`。
- 對照:`# ok` 版本回 `[('', ['test'])]`。

`t_situation_rule_android_run_cmd_segments` 的註解案例全是無引號的註解,抓不到這個。`_detekt_walk_segments` 的 docstring 已列「引號包住 # 開頭詞」這個已知限制,但沒列「註解內不成對引號讓整行消失」。

## g2 r2 新增三支測試沒有任何 `[test:]` 綁定,S6 條款字面也沒跟上
severity: minor
blocking: 否
引句:「- [S6] 當預設平台的 profile 是 kotlin-junit 或 java-junit、是 Android 專案而 run_cmd 含頂層 test 任務或 YOUR_MODULE 佔位,人裁指令 應 在跑殺傷力之前拒絕並印出正確格式與模組候選」
說明:原本想引的 `[test:…]` 綁定句不在凍結材料裡,所以改引 S6 條款原文;這句已在 r3-snapshot.patch 用 grep 確認逐字存在。
file: `/Users/enzo/harness/lumos-srl-android/scripts/test_lumos.py:136402`(segments)、`:136464`(header_scan_strip)、`/Users/enzo/harness/lumos-srl-android/scripts/test_lumos.py:136516` 附近的 `t_situation_rule_diff_no_git`

1. r2 新增 `t_situation_rule_android_run_cmd_segments`、`t_situation_rule_header_scan_strip`、`t_situation_rule_diff_no_git`。
2. 我在 `docs/` 用 grep 找這三個名字,一筆都沒有。棧別 WHY 的 `[test:]` 仍是原本 5 個,計劃 S6、S7 的 `[test:]` 也沒加。
3. 這三支守的是 r2 修的行為:每個 gradle 段、`-p`、`:test`、run_cmd 非字串、檔頭字串剝法、git 不在 PATH。
4. 它們只在整套測試時才會跑。推送前閘走 light 子集(`--suite keys`)時,只有「原始碼提到改到的函式或檔名」的測試會跑,綁定測試的路徑不會點到它們。
5. S6 條款字面仍只寫「頂層 test 或 YOUR_MODULE」,沒涵蓋 r2 加的每段、`:test`、`-p`,條款與行為不一致。

這次我沒有重現失敗:三支測試本身都存在、名稱正確。

## 附:圖譜鏡頭
這次沒附固定席節點,以下是 diff 實際牽連到的節點。

- **Systems/棧別提問表態閘**(人裁那條 WHY):r2 改動與程式一致,我逐項驗過,不影響其他合約。
  - 檔頭區剝法改走 `_strip_c_comments(kotlin=True)`:BOM 加 shebang、巢狀註解、`@file:` 多行括號、三引號字串、行尾在註解裡的 import,我對 10 種輸入跑過,插入點都對。
  - 效能:4MB 的空行、程式碼、三引號字串三種輸入,各在 0.1 到 1.4 秒、記憶體峰值不到 55MB。字串樣板極端輸入(44 萬個 `"${`)要 2.9 秒、123MB。
  - `--diff` 與 HEAD 都改走 `_lens_full_sha`:語意與原本一致,多了逾時,git 不在時回 None 而不丟例外。
  - `_gradle_task_list` 改回 `[(專案目錄, 任務)]`:呼叫端只有 `_situation_rule_android_cmd_problem` 與測試,都已同步。
  - `_detekt_walk_segments` 預設 `comments=False`:detekt 判定路徑行為不變。
  - 該 WHY 沒提 run_cmd 非字串會 rc 2,這點只寫在計劃的審計紀錄裡。
- **Projects/人裁殺傷力在真實Android專案跑得起來_計劃**:`lumos lint` 為 0 問題。用詞段的 r2 改寫與程式一致。
- **Systems/guard-kill、Systems/lumos-cli-lifecycle、SKILL.md、06 手冊**:r2 沒動它們。06 手冊仍寫「頂層 `test` 或 `YOUR_MODULE` 佔位會被擋」,沒提 Android 模組的 `:模組:test`、每個 gradle 段、`-p`,內容偏窄但不會讓人做出錯的操作。

最嚴重:minor;blocking 共 0 條。
