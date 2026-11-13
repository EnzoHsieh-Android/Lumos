severity: major

## g1 任務清單只認第一個 gradle 段,`&&` 或 `;` 後面的 `./gradlew test` 查不到
severity: major
blocking: 是
引句:「每一段第一個檔名是 `gradlew` 或 `gradle` 的詞之後、不以 `-` 開頭的詞;帶值選項表用 `_GRADLE_VALUE_OPTS` 加 `--tests`,選項的值不算任務。」
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:40965`(`_detekt_walk_segments`);修補在 r2-repair.patch 的 `_gradle_task_list`,它對第一個 gradle 段 `return` 就結束。
1. 計劃〈用詞〉寫「每一段」,程式碼 `for seg in _detekt_walk_segments(...): if _is_gradle_head(seg[0]): return ...` 只看第一個 gradle 段。
2. 重現:用 `importlib.machinery.SourceFileLoader` 載入 `scripts/lumos`,呼叫 `m._gradle_task_list`,實測輸出如下。
   - `"./gradlew clean && ./gradlew test --tests '*{method}'"` 回 `['clean']`
   - `"./gradlew --stop; ./gradlew test"` 回 `[]`
   - `"./gradlew clean test"` 回 `['clean','test']`(正常)
3. 結果:這種 Android 專案的 run_cmd 在人裁入口被放行,沒有 rc 2,也沒印格式和模組候選。要等殺傷力真的跑完才以 abort 或 killed_unattributed 收場,手冊保證的「跑之前先擋」落空。
4. 修補自己加的 `⑬` 單元測試只涵蓋 `sh -c`、`env`、`-P/-D`、`cd … && ./gradlew`(`cd` 那段不是 gradle 段),沒有「兩個 gradle 段」的案例。測試抓不到這個壞法,所以不降級。
5. 修法二選一。一是程式改成收集所有 gradle 段的任務。二是計劃〈用詞〉改成「第一個 gradle 段」,並把 `&&` 後面不查寫進筆記。

## g2 棧別提問表態閘 WHY 行對 `:模組:test` 的說法沒跟上
severity: minor
blocking: 否
引句:「或 Android 模組的 :模組:test 就拒絕,印要改的設定鍵、正確格式(不加 cd:殺傷力與合約測試閘都在平台根跑 run_cmd)」
file: `/Users/enzo/harness/lumos-srl-andoid` 之外無需查;對照 `/Users/enzo/harness/lumos-srl-android/docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md` 同篇的人裁段落。
1. 同一篇的人裁段落已寫「(開頭有沒有 `:` 都算)」,這條 WHY 行沒寫。
2. 三個月後的接手者讀 WHY 行,會以為 `app:test` 不擋。程式碼(`_gradle_test_module`)和 `⑫` 測試都擋它。
3. 寫法上是漏寫,不是矛盾,所以只列 minor。

## 附:圖譜鏡頭
- LUMOS-IMPACT 沒有附固定席節點。以下是我自己對本次改動牽連到的筆記判斷:
  - 檢查 `Systems/guard-kill`、`Systems/棧別提問表態閘`、`Projects/代碼審修正關卡第0步_計劃` S11、人裁計劃。
  - 筆記的 `lint` 全部 0 問題。
  - 新增、改名的 `[test:]` 都存在於 `scripts/test_lumos.py`:`t_situation_rule_import_flag_inserts`、`t_guard_kill_runs_at_platform_root`、`t_isolated_worktree_shared`、`t_situation_rule_android_run_cmd_check`、`t_kill_log_fail_excerpt` 等,各一支。
  - 舊名 `t_situation_rule_import_flag` 在 repo 內(排除卷證)已無殘留引用。
- 殺傷力改到平台根跑,對其他呼叫端的影響:
  - 推送前的合約測試閘 `_run_bound_tests` 與冒煙探測 `_filter_probe` 都用平台根當 cwd,與新行為一致。
  - 平台根是 repo 最上層時行為不變。
  - WHY 行的「代價」已承認:平台根是子資料夾、run_cmd 原本寫成從 repo 最上層跑的舊設定要改。這點成立。
  - 我搜過 `cd <平台根>` 之類殘留的舊教法,除了卷證和「原本」的歷史說明外沒有。`SKILL.md` 與 `06-代碼審與推送.md` 的說法和計劃、筆記一致。
- 檔頭區文法的新邊界我逐項實測,全部符合筆記所述,沒有發現新錯。測過:
  - 註解內的 import 不算也不當插入點
  - 多行 `@file:` 與字串裡的括號
  - BOM、shebang、CRLF
  - `as` 別名、`;` 一行多句
  - 反引號識別字
  - 沒有換行的 package
- `_kill_mask_paths` 的路徑邊界規則會漏遮句尾接 `.` 的家目錄路徑,但我給不出實際會出現的輸出,所以不列為發現。
- 本席跑過的子集全過:`runs_at_platform_root`(5)、`situation_rule_android_run_cmd_check`(33)、`situation_rule_import_flag`(49)、`kill_log_fail_excerpt`(16)、`isolated_worktree_shared`(9)。
- 另外兩組 `kill_recipe_check_matches` 與 `recipe_id_subdir_platform` 還在背景跑,沒等到結果,不能算已驗。
- 派工詞指定的鎖檔 `…/dispatch-lens/47ebf459…json.warming` 不存在,沒有鎖要處理。
- 我建的臨時目錄 `/private/tmp/lumos-seat-work/code-人裁殺傷力android/合約-sonnet` 已用字面路徑刪除。

最嚴重 severity: major,blocking 共 1 條。
